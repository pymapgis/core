"""
Authentication and Security Middleware

Provides middleware components for authentication, authorization,
rate limiting, and security enforcement in PyMapGIS applications.
"""

import time
import logging
from functools import wraps
from typing import Dict, Any, Optional, Callable, List
from collections import defaultdict, deque
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded."""

    pass


class AuthenticationRequired(Exception):
    """Exception raised when authentication is required."""

    pass


class PermissionDenied(Exception):
    """Exception raised when permission is denied."""

    pass


class RateLimitMiddleware:
    """Rate limiting middleware."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 3600):
        """
        Initialize rate limit middleware.

        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, deque] = defaultdict(deque)

    def check_rate_limit(self, identifier: str) -> bool:
        """
        Check if request is within rate limit.

        Args:
            identifier: Client identifier (IP, user ID, etc.)

        Returns:
            bool: True if within limit

        Raises:
            RateLimitExceeded: If rate limit exceeded
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old requests
        client_requests = self.requests[identifier]
        while client_requests and client_requests[0] < window_start:
            client_requests.popleft()

        # Check limit
        if len(client_requests) >= self.max_requests:
            raise RateLimitExceeded(
                f"Rate limit exceeded: {len(client_requests)}/{self.max_requests}"
            )

        # Add current request
        client_requests.append(now)
        return True

    def get_remaining_requests(self, identifier: str) -> int:
        """Get remaining requests for identifier."""
        now = time.time()
        window_start = now - self.window_seconds

        client_requests = self.requests[identifier]
        # Count requests in current window
        current_requests = sum(
            1 for req_time in client_requests if req_time >= window_start
        )

        return max(0, self.max_requests - current_requests)


class AuthenticationMiddleware:
    """Authentication middleware."""

    def __init__(self):
        """Initialize authentication middleware."""
        from . import get_api_key_manager, get_oauth_manager, get_session_manager

        self.api_key_manager = get_api_key_manager()
        self.oauth_manager = get_oauth_manager()
        self.session_manager = get_session_manager()

    def authenticate_request(
        self, headers: Dict[str, str], params: Dict[str, str]
    ) -> Optional[str]:
        """
        Authenticate a request using various methods.

        Args:
            headers: Request headers
            params: Request parameters

        Returns:
            User ID if authenticated, None otherwise
        """
        # Try API key authentication
        api_key = headers.get("X-API-Key") or params.get("api_key")
        if api_key:
            api_key_obj = self.api_key_manager.validate_key(api_key)
            if api_key_obj:
                return f"api_key:{api_key_obj.key_id}"

        # Try OAuth token authentication
        auth_header = headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove 'Bearer ' prefix
            user_id = self.oauth_manager.validate_token(token)
            if user_id:
                return f"oauth:{user_id}"

        # Try session authentication
        session_id = headers.get("X-Session-ID") or params.get("session_id")
        if session_id:
            session = self.session_manager.validate_session(session_id)
            if session:
                return f"session:{session.user_id}"

        return None

    def require_authentication(self, func: Callable) -> Callable:
        """Decorator to require authentication."""

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract headers and params from function arguments
            headers = kwargs.get("headers", {})
            params = kwargs.get("params", {})

            user_id = self.authenticate_request(headers, params)
            if not user_id:
                raise AuthenticationRequired("Authentication required")

            # Add user_id to kwargs
            kwargs["authenticated_user"] = user_id
            return func(*args, **kwargs)

        return wrapper


class AuthorizationMiddleware:
    """Authorization middleware."""

    def __init__(self):
        """Initialize authorization middleware."""
        from . import get_rbac_manager

        self.rbac_manager = get_rbac_manager()

    def check_permission(
        self, user_id: str, permission: str, resource: str = "*"
    ) -> bool:
        """
        Check if user has permission.

        Args:
            user_id: User identifier
            permission: Required permission
            resource: Resource identifier

        Returns:
            bool: True if user has permission
        """
        # Extract actual user ID from authenticated user string
        if ":" in user_id:
            _, actual_user_id = user_id.split(":", 1)
        else:
            actual_user_id = user_id

        return self.rbac_manager.check_permission(actual_user_id, permission, resource)

    def require_permission(self, permission: str, resource: str = "*") -> Callable:
        """Decorator to require specific permission."""

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                user_id = kwargs.get("authenticated_user")
                if not user_id:
                    raise AuthenticationRequired("Authentication required")

                if not self.check_permission(user_id, permission, resource):
                    raise PermissionDenied(f"Permission denied: {permission}")

                return func(*args, **kwargs)

            return wrapper

        return decorator


class SecurityMiddleware:
    """Combined security middleware."""

    def __init__(
        self,
        rate_limit_requests: int = 100,
        rate_limit_window: int = 3600,
        require_https: bool = True,
    ):
        """
        Initialize security middleware.

        Args:
            rate_limit_requests: Maximum requests per window
            rate_limit_window: Rate limit window in seconds
            require_https: Require HTTPS connections
        """
        self.rate_limiter = RateLimitMiddleware(rate_limit_requests, rate_limit_window)
        self.auth_middleware = AuthenticationMiddleware()
        self.authz_middleware = AuthorizationMiddleware()
        self.require_https = require_https

    def process_request(
        self,
        headers: Dict[str, str],
        params: Dict[str, str],
        client_ip: str,
        is_https: bool = True,
    ) -> Dict[str, Any]:
        """
        Process request through security middleware.

        Args:
            headers: Request headers
            params: Request parameters
            client_ip: Client IP address
            is_https: Whether request is HTTPS

        Returns:
            Dict with security context

        Raises:
            Various security exceptions
        """
        # Check HTTPS requirement
        if self.require_https and not is_https:
            raise PermissionDenied("HTTPS required")

        # Check rate limit
        self.rate_limiter.check_rate_limit(client_ip)

        # Authenticate request
        user_id = self.auth_middleware.authenticate_request(headers, params)

        return {
            "authenticated_user": user_id,
            "client_ip": client_ip,
            "is_authenticated": user_id is not None,
            "remaining_requests": self.rate_limiter.get_remaining_requests(client_ip),
        }


# Global middleware instances
_rate_limiter = None
_auth_middleware = None
_authz_middleware = None
_security_middleware = None


def get_rate_limiter() -> RateLimitMiddleware:
    """Get global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimitMiddleware()
    return _rate_limiter


def get_auth_middleware() -> AuthenticationMiddleware:
    """Get global authentication middleware instance."""
    global _auth_middleware
    if _auth_middleware is None:
        _auth_middleware = AuthenticationMiddleware()
    return _auth_middleware


def get_authz_middleware() -> AuthorizationMiddleware:
    """Get global authorization middleware instance."""
    global _authz_middleware
    if _authz_middleware is None:
        _authz_middleware = AuthorizationMiddleware()
    return _authz_middleware


def get_security_middleware() -> SecurityMiddleware:
    """Get global security middleware instance."""
    global _security_middleware
    if _security_middleware is None:
        _security_middleware = SecurityMiddleware()
    return _security_middleware


# Convenience decorators
def require_auth(func: Callable) -> Callable:
    """Decorator to require authentication."""
    return get_auth_middleware().require_authentication(func)


def require_permission(permission: str, resource: str = "*") -> Callable:
    """Decorator to require specific permission."""
    return get_authz_middleware().require_permission(permission, resource)


def rate_limit(max_requests: int = 100, window_seconds: int = 3600) -> Callable:
    """Decorator to apply rate limiting."""
    limiter = RateLimitMiddleware(max_requests, window_seconds)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Try to extract client identifier
            client_id = kwargs.get("client_ip", "unknown")
            limiter.check_rate_limit(client_id)
            return func(*args, **kwargs)

        return wrapper

    return decorator


# Context manager for security
class SecurityContext:
    """Security context manager."""

    def __init__(self, headers: Dict[str, str], params: Dict[str, str], client_ip: str):
        """Initialize security context."""
        self.headers = headers
        self.params = params
        self.client_ip = client_ip
        self.security_info = None

    def __enter__(self):
        """Enter security context."""
        middleware = get_security_middleware()
        self.security_info = middleware.process_request(
            self.headers, self.params, self.client_ip
        )
        return self.security_info

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit security context."""
        if exc_type:
            logger.warning(f"Security context error: {exc_type.__name__}: {exc_val}")
        return False
