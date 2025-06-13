"""
PyMapGIS Enterprise Features

This module provides enterprise-grade features including:
- Multi-user authentication and authorization
- Role-based access control (RBAC)
- OAuth integration
- API key management
- Multi-tenant support

Phase 3 Enterprise Features Implementation
"""

# Import core classes only to avoid circular imports
try:
    from .auth import (
        AuthenticationManager,
        JWTAuthenticator,
        APIKeyManager,
        SessionManager,
    )
except ImportError:
    AuthenticationManager = None  # type: ignore
    JWTAuthenticator = None  # type: ignore
    APIKeyManager = None  # type: ignore
    SessionManager = None  # type: ignore

try:
    from .users import (
        UserManager,
        User,
        UserRole,
        UserProfile,
    )
except ImportError:
    UserManager = None  # type: ignore
    User = None  # type: ignore
    UserRole = None  # type: ignore
    UserProfile = None  # type: ignore

try:
    from .rbac import (
        RBACManager,
        Permission,
        Role,
        Resource,
    )
except ImportError:
    RBACManager = None  # type: ignore
    Permission = None  # type: ignore
    Role = None  # type: ignore
    Resource = None  # type: ignore

try:
    from .oauth import (
        OAuthManager,
        GoogleOAuthProvider,
        GitHubOAuthProvider,
        MicrosoftOAuthProvider,
    )
except ImportError:
    OAuthManager = None  # type: ignore
    GoogleOAuthProvider = None  # type: ignore
    GitHubOAuthProvider = None  # type: ignore
    MicrosoftOAuthProvider = None  # type: ignore

try:
    from .tenants import (
        TenantManager,
        Tenant,
        TenantUser,
    )
except ImportError:
    TenantManager = None  # type: ignore
    Tenant = None  # type: ignore
    TenantUser = None  # type: ignore

# Version info
__version__ = "0.3.0"
__enterprise_features__ = [
    "multi_user_auth",
    "rbac",
    "oauth_integration", 
    "api_key_management",
    "multi_tenant_support",
    "session_management",
]

# Default configuration
DEFAULT_ENTERPRISE_CONFIG = {
    "auth": {
        "jwt_secret_key": None,  # Must be set in production
        "jwt_algorithm": "HS256",
        "jwt_expiration_hours": 24,
        "session_timeout_minutes": 60,
        "password_min_length": 8,
        "require_email_verification": True,
    },
    "rbac": {
        "default_user_role": "user",
        "admin_role": "admin",
        "viewer_role": "viewer",
        "enable_resource_permissions": True,
    },
    "oauth": {
        "enabled_providers": ["google", "github"],
        "redirect_uri": "/auth/oauth/callback",
        "state_expiration_minutes": 10,
    },
    "tenants": {
        "enable_multi_tenant": False,
        "default_tenant": "default",
        "max_users_per_tenant": 100,
    },
    "api_keys": {
        "enable_api_keys": True,
        "key_expiration_days": 365,
        "max_keys_per_user": 10,
    },
}

# Export available components
__all__ = []

# Add available components to __all__
if AuthenticationManager is not None:
    __all__.extend(["AuthenticationManager", "JWTAuthenticator", "APIKeyManager", "SessionManager"])
if UserManager is not None:
    __all__.extend(["UserManager", "User", "UserRole", "UserProfile"])
if RBACManager is not None:
    __all__.extend(["RBACManager", "Permission", "Role", "Resource"])
if OAuthManager is not None:
    __all__.extend(["OAuthManager", "GoogleOAuthProvider", "GitHubOAuthProvider", "MicrosoftOAuthProvider"])
if TenantManager is not None:
    __all__.extend(["TenantManager", "Tenant", "TenantUser"])

# Always export configuration
__all__.extend(["DEFAULT_ENTERPRISE_CONFIG", "__version__", "__enterprise_features__"])
