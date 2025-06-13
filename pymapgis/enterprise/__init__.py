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

from .auth import (
    AuthenticationManager,
    JWTAuthenticator,
    APIKeyManager,
    SessionManager,
    authenticate_user,
    require_auth,
    require_role,
)

from .users import (
    UserManager,
    User,
    UserRole,
    UserProfile,
    create_user,
    get_user,
    update_user,
    delete_user,
)

from .rbac import (
    RBACManager,
    Permission,
    Role,
    Resource,
    check_permission,
    grant_permission,
    revoke_permission,
)

from .oauth import (
    OAuthManager,
    GoogleOAuthProvider,
    GitHubOAuthProvider,
    MicrosoftOAuthProvider,
    oauth_login,
    oauth_callback,
)

from .tenants import (
    TenantManager,
    Tenant,
    TenantUser,
    create_tenant,
    get_tenant,
    switch_tenant,
)

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

# Export all components
__all__ = [
    # Core authentication
    "AuthenticationManager",
    "JWTAuthenticator", 
    "APIKeyManager",
    "SessionManager",
    "authenticate_user",
    "require_auth",
    "require_role",
    
    # User management
    "UserManager",
    "User",
    "UserRole",
    "UserProfile",
    "create_user",
    "get_user", 
    "update_user",
    "delete_user",
    
    # RBAC
    "RBACManager",
    "Permission",
    "Role",
    "Resource",
    "check_permission",
    "grant_permission",
    "revoke_permission",
    
    # OAuth
    "OAuthManager",
    "GoogleOAuthProvider",
    "GitHubOAuthProvider", 
    "MicrosoftOAuthProvider",
    "oauth_login",
    "oauth_callback",
    
    # Multi-tenant
    "TenantManager",
    "Tenant",
    "TenantUser",
    "create_tenant",
    "get_tenant",
    "switch_tenant",
    
    # Configuration
    "DEFAULT_ENTERPRISE_CONFIG",
    "__version__",
    "__enterprise_features__",
]
