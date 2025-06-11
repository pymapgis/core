"""
PyMapGIS Authentication & Security Module

This module provides comprehensive authentication and security features for PyMapGIS,
including API key management, OAuth 2.0 integration, and Role-Based Access Control (RBAC).

Features:
- API Key Management: Secure generation, validation, and rotation
- OAuth 2.0 Integration: Support for multiple providers (Google, Microsoft, GitHub)
- RBAC: Role-based access control with granular permissions
- Session Management: Secure session handling and token management
- Security Middleware: Request validation and rate limiting

Enterprise Features:
- Multi-provider OAuth support
- Custom role definitions
- Audit logging
- Token refresh and rotation
- Permission inheritance
"""

from typing import Optional

from .api_keys import (
    APIKeyManager,
    APIKey,
    generate_api_key,
    validate_api_key,
    rotate_api_key,
)

from .oauth import (
    OAuthManager,
    OAuthProvider,
    GoogleOAuthProvider,
    MicrosoftOAuthProvider,
    GitHubOAuthProvider,
    authenticate_oauth,
    refresh_oauth_token,
)

from .rbac import (
    RBACManager,
    Role,
    Permission,
    User,
    create_role,
    assign_role,
    check_permission,
    has_permission,
)

from .session import (
    SessionManager,
    Session,
    create_session,
    validate_session,
    invalidate_session,
)

from .middleware import (
    AuthenticationMiddleware,
    RateLimitMiddleware,
    SecurityMiddleware,
    require_auth,
    require_permission,
    rate_limit,
)

from .security import (
    SecurityConfig,
    encrypt_data,
    decrypt_data,
    hash_password,
    verify_password,
    generate_secure_token,
)

# Version and metadata
__version__ = "0.3.2"
__author__ = "PyMapGIS Team"

# Default configuration
DEFAULT_CONFIG = {
    "api_key_length": 32,
    "session_timeout": 3600,  # 1 hour
    "max_login_attempts": 5,
    "rate_limit_requests": 100,
    "rate_limit_window": 3600,  # 1 hour
    "token_refresh_threshold": 300,  # 5 minutes
    "audit_logging": True,
    "encryption_algorithm": "AES-256-GCM",
}

# Global instances
_api_key_manager = None
_oauth_manager = None
_rbac_manager = None
_session_manager = None


def get_api_key_manager() -> APIKeyManager:
    """Get the global API key manager instance."""
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager


def get_oauth_manager() -> OAuthManager:
    """Get the global OAuth manager instance."""
    global _oauth_manager
    if _oauth_manager is None:
        _oauth_manager = OAuthManager()
    return _oauth_manager


def get_rbac_manager() -> RBACManager:
    """Get the global RBAC manager instance."""
    global _rbac_manager
    if _rbac_manager is None:
        _rbac_manager = RBACManager()
    return _rbac_manager


def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


# Convenience functions
def authenticate(
    api_key: Optional[str] = None,
    oauth_token: Optional[str] = None,
    session_id: Optional[str] = None,
) -> bool:
    """
    Authenticate using any supported method.

    Args:
        api_key: API key for authentication
        oauth_token: OAuth token for authentication
        session_id: Session ID for authentication

    Returns:
        bool: True if authentication successful
    """
    if api_key:
        api_result = validate_api_key(api_key)
        return api_result is not None
    elif oauth_token:
        oauth_manager = get_oauth_manager()
        oauth_result = oauth_manager.validate_token(oauth_token)
        return oauth_result is not None
    elif session_id:
        session_result = validate_session(session_id)
        return session_result is not None
    return False


def authorize(user_id: str, permission: str) -> bool:
    """
    Check if user has required permission.

    Args:
        user_id: User identifier
        permission: Required permission

    Returns:
        bool: True if user has permission
    """
    return check_permission(user_id, permission)


# Export all public components
__all__ = [
    # API Keys
    "APIKeyManager",
    "APIKey",
    "generate_api_key",
    "validate_api_key",
    "rotate_api_key",
    # OAuth
    "OAuthManager",
    "OAuthProvider",
    "GoogleOAuthProvider",
    "MicrosoftOAuthProvider",
    "GitHubOAuthProvider",
    "authenticate_oauth",
    "refresh_oauth_token",
    # RBAC
    "RBACManager",
    "Role",
    "Permission",
    "User",
    "create_role",
    "assign_role",
    "check_permission",
    "has_permission",
    # Session Management
    "SessionManager",
    "Session",
    "create_session",
    "validate_session",
    "invalidate_session",
    # Middleware
    "AuthenticationMiddleware",
    "RateLimitMiddleware",
    "SecurityMiddleware",
    "require_auth",
    "require_permission",
    "rate_limit",
    # Security
    "SecurityConfig",
    "encrypt_data",
    "decrypt_data",
    "hash_password",
    "verify_password",
    "generate_secure_token",
    # Manager instances
    "get_api_key_manager",
    "get_oauth_manager",
    "get_rbac_manager",
    "get_session_manager",
    # Convenience functions
    "authenticate",
    "authorize",
    # Configuration
    "DEFAULT_CONFIG",
]
