"""
Authentication and Authorization System

Provides JWT-based authentication, API key management, and session handling
for PyMapGIS enterprise features.
"""

try:
    import jwt
except ImportError:
    jwt = None
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from functools import wraps

logger = logging.getLogger(__name__)

# Check for optional dependencies
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    logger.warning("bcrypt not available, using basic password hashing")

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("redis not available, using in-memory session storage")


@dataclass
class AuthToken:
    """Authentication token data structure."""
    user_id: str
    username: str
    email: str
    roles: List[str]
    tenant_id: Optional[str] = None
    issued_at: datetime = None
    expires_at: datetime = None
    
    def __post_init__(self):
        if self.issued_at is None:
            self.issued_at = datetime.utcnow()
        if self.expires_at is None:
            self.expires_at = self.issued_at + timedelta(hours=24)


@dataclass
class APIKey:
    """API key data structure."""
    key_id: str
    user_id: str
    name: str
    key_hash: str
    permissions: List[str]
    created_at: datetime
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    is_active: bool = True


class JWTAuthenticator:
    """JWT-based authentication manager."""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        if jwt is None:
            raise ImportError("PyJWT is required for JWT authentication. Install with: pip install PyJWT")
        if not secret_key:
            raise ValueError("JWT secret key is required")
        self.secret_key = secret_key
        self.algorithm = algorithm
        
    def generate_token(self, auth_token: AuthToken) -> str:
        """Generate JWT token from auth token data."""
        payload = {
            "user_id": auth_token.user_id,
            "username": auth_token.username,
            "email": auth_token.email,
            "roles": auth_token.roles,
            "tenant_id": auth_token.tenant_id,
            "iat": auth_token.issued_at.timestamp(),
            "exp": auth_token.expires_at.timestamp(),
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
    def verify_token(self, token: str) -> Optional[AuthToken]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            return AuthToken(
                user_id=payload["user_id"],
                username=payload["username"],
                email=payload["email"],
                roles=payload["roles"],
                tenant_id=payload.get("tenant_id"),
                issued_at=datetime.fromtimestamp(payload["iat"]),
                expires_at=datetime.fromtimestamp(payload["exp"]),
            )
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None


class APIKeyManager:
    """API key management system."""
    
    def __init__(self):
        self.api_keys: Dict[str, APIKey] = {}
        
    def generate_api_key(
        self,
        user_id: str,
        name: str,
        permissions: List[str],
        expires_days: Optional[int] = None
    ) -> tuple[str, APIKey]:
        """Generate a new API key."""
        # Generate secure random key
        raw_key = secrets.token_urlsafe(32)
        key_id = secrets.token_hex(16)
        
        # Hash the key for storage
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        # Create expiration date
        expires_at = None
        if expires_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
            
        api_key = APIKey(
            key_id=key_id,
            user_id=user_id,
            name=name,
            key_hash=key_hash,
            permissions=permissions,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
        )
        
        self.api_keys[key_id] = api_key
        
        # Return the raw key (only time it's available)
        return f"pymapgis_{key_id}_{raw_key}", api_key
        
    def verify_api_key(self, api_key: str) -> Optional[APIKey]:
        """Verify an API key and return associated data."""
        try:
            # Parse key format: pymapgis_{key_id}_{raw_key}
            parts = api_key.split("_")
            if len(parts) != 3 or parts[0] != "pymapgis":
                return None
                
            key_id = parts[1]
            raw_key = parts[2]
            
            # Check if key exists
            if key_id not in self.api_keys:
                return None
                
            stored_key = self.api_keys[key_id]
            
            # Verify key hash
            key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
            if key_hash != stored_key.key_hash:
                return None
                
            # Check if key is active
            if not stored_key.is_active:
                return None
                
            # Check expiration
            if stored_key.expires_at and datetime.utcnow() > stored_key.expires_at:
                return None
                
            # Update last used
            stored_key.last_used = datetime.utcnow()
            
            return stored_key
            
        except Exception as e:
            logger.warning(f"API key verification failed: {e}")
            return None
            
    def revoke_api_key(self, key_id: str) -> bool:
        """Revoke an API key."""
        if key_id in self.api_keys:
            self.api_keys[key_id].is_active = False
            return True
        return False
        
    def list_user_keys(self, user_id: str) -> List[APIKey]:
        """List all API keys for a user."""
        return [
            key for key in self.api_keys.values()
            if key.user_id == user_id and key.is_active
        ]


class SessionManager:
    """Session management system."""
    
    def __init__(self, redis_client=None):
        self.redis_client = redis_client if REDIS_AVAILABLE else None
        self.memory_sessions: Dict[str, Dict[str, Any]] = {}
        
    def create_session(self, user_id: str, data: Dict[str, Any], timeout_minutes: int = 60) -> str:
        """Create a new session."""
        session_id = secrets.token_urlsafe(32)
        session_data = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(minutes=timeout_minutes)).isoformat(),
            **data
        }
        
        if self.redis_client:
            # Store in Redis with TTL
            self.redis_client.setex(
                f"session:{session_id}",
                timeout_minutes * 60,
                str(session_data)
            )
        else:
            # Store in memory
            self.memory_sessions[session_id] = session_data
            
        return session_id
        
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data."""
        if self.redis_client:
            data = self.redis_client.get(f"session:{session_id}")
            return eval(data.decode()) if data else None
        else:
            session = self.memory_sessions.get(session_id)
            if session:
                # Check expiration
                expires_at = datetime.fromisoformat(session["expires_at"])
                if datetime.utcnow() > expires_at:
                    del self.memory_sessions[session_id]
                    return None
            return session
            
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if self.redis_client:
            return bool(self.redis_client.delete(f"session:{session_id}"))
        else:
            return bool(self.memory_sessions.pop(session_id, None))


class AuthenticationManager:
    """Main authentication manager."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.jwt_auth = JWTAuthenticator(
            secret_key=config["jwt_secret_key"],
            algorithm=config.get("jwt_algorithm", "HS256")
        )
        self.api_key_manager = APIKeyManager()
        self.session_manager = SessionManager()
        
    def hash_password(self, password: str) -> str:
        """Hash a password securely."""
        if BCRYPT_AVAILABLE:
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        else:
            # Fallback to SHA256 with salt (less secure)
            salt = secrets.token_hex(16)
            return f"{salt}:{hashlib.sha256((salt + password).encode()).hexdigest()}"
            
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        if BCRYPT_AVAILABLE:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        else:
            # Fallback verification
            try:
                salt, hash_value = hashed.split(':')
                return hashlib.sha256((salt + password).encode()).hexdigest() == hash_value
            except ValueError:
                return False


# Decorator functions
def require_auth(f: Callable) -> Callable:
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # This would integrate with your web framework
        # For now, it's a placeholder
        return f(*args, **kwargs)
    return decorated_function


def require_role(required_role: str) -> Callable:
    """Decorator to require specific role."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This would check user roles
            # For now, it's a placeholder
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Convenience functions
def authenticate_user(username: str, password: str, auth_manager: AuthenticationManager) -> Optional[AuthToken]:
    """Authenticate a user with username/password."""
    # This would integrate with your user storage system
    # For now, it's a placeholder
    pass
