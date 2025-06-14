# PyMapGIS Enterprise Features

This document provides an overview of PyMapGIS Enterprise Features, designed for multi-user environments, advanced authentication, and organizational management.

## Overview

PyMapGIS Enterprise Features provide a comprehensive suite of tools for:

- **Multi-user Authentication & Authorization**
- **Role-Based Access Control (RBAC)**
- **OAuth Integration** with popular providers
- **Multi-tenant Support** for organizations
- **API Key Management**
- **Session Management**

## Quick Start

### Basic Setup

```python
from pymapgis.enterprise import (
    AuthenticationManager,
    UserManager,
    RBACManager,
    TenantManager,
    DEFAULT_ENTERPRISE_CONFIG
)

# Configure authentication
config = DEFAULT_ENTERPRISE_CONFIG.copy()
config["auth"]["jwt_secret_key"] = "your-secret-key"

# Initialize managers
auth_manager = AuthenticationManager(config["auth"])
user_manager = UserManager()
rbac_manager = RBACManager()
tenant_manager = TenantManager()
```

### Create Your First Organization

```python
from pymapgis.enterprise import create_tenant, create_user, UserProfile

# Create organization
tenant = create_tenant(
    name="My Organization",
    slug="my-org",
    owner_id="owner-user-id",
    tenant_manager=tenant_manager
)

# Create user
profile = UserProfile(
    first_name="John",
    last_name="Doe",
    organization="My Organization"
)

user = create_user(
    username="johndoe",
    email="john@myorg.com",
    password="secure_password",
    first_name="John",
    last_name="Doe",
    user_manager=user_manager,
    auth_manager=auth_manager,
    tenant_id=tenant.tenant_id
)
```

## Core Components

### 1. Authentication System

**Features:**
- JWT-based authentication
- Secure password hashing (bcrypt)
- API key management
- Session management

**Example:**
```python
from pymapgis.enterprise.auth import JWTAuthenticator, AuthToken

# Create JWT authenticator
jwt_auth = JWTAuthenticator("your-secret-key")

# Create auth token
auth_token = AuthToken(
    user_id="user123",
    username="johndoe",
    email="john@example.com",
    roles=["user", "analyst"]
)

# Generate JWT
jwt_token = jwt_auth.generate_token(auth_token)

# Verify JWT
verified_token = jwt_auth.verify_token(jwt_token)
```

### 2. User Management

**Features:**
- User registration and profiles
- Role assignment
- User search and filtering
- Account management

**Example:**
```python
from pymapgis.enterprise.users import UserManager, UserRole, UserProfile

user_manager = UserManager()

# Create user profile
profile = UserProfile(
    first_name="Jane",
    last_name="Smith",
    organization="Tech Corp",
    department="Engineering"
)

# Create user
user = user_manager.create_user(
    username="janesmith",
    email="jane@techcorp.com",
    password_hash=auth_manager.hash_password("password"),
    profile=profile,
    roles=[UserRole.USER, UserRole.ANALYST]
)
```

### 3. Role-Based Access Control (RBAC)

**Features:**
- Granular permissions
- Resource-level access control
- Default roles (Viewer, User, Analyst, Editor, Admin)
- Custom role creation

**Example:**
```python
from pymapgis.enterprise.rbac import RBACManager, ResourceType, Action

rbac_manager = RBACManager()

# Assign role to user
rbac_manager.assign_role_to_user("user123", "analyst")

# Check permissions
can_create_map = rbac_manager.check_action(
    "user123", 
    ResourceType.MAP, 
    Action.CREATE
)

# Grant specific permission
rbac_manager.grant_permission("user123", "dataset_delete")
```

### 4. OAuth Integration

**Features:**
- Google OAuth
- GitHub OAuth
- Microsoft OAuth
- Custom OAuth providers

**Example:**
```python
from pymapgis.enterprise.oauth import OAuthManager, GoogleOAuthProvider

oauth_manager = OAuthManager()

# Register Google OAuth
google_provider = GoogleOAuthProvider(
    client_id="your-google-client-id",
    client_secret="your-google-client-secret",
    redirect_uri="http://localhost:8000/auth/callback"
)
oauth_manager.register_provider("google", google_provider)

# Start OAuth flow
auth_url = oauth_manager.create_authorization_url("google")
```

### 5. Multi-Tenant Support

**Features:**
- Organization isolation
- Subscription tiers
- Resource limits
- Usage tracking

**Example:**
```python
from pymapgis.enterprise.tenants import TenantManager, SubscriptionTier

tenant_manager = TenantManager()

# Create organization
tenant = tenant_manager.create_tenant(
    name="Enterprise Corp",
    slug="enterprise-corp",
    owner_id="owner123",
    subscription_tier=SubscriptionTier.PROFESSIONAL
)

# Add user to organization
tenant_manager.add_user_to_tenant(
    tenant.tenant_id,
    "user456",
    role="member"
)
```

## Default Roles & Permissions

### Viewer
- Read maps, datasets, and analysis results
- No creation or modification rights

### User
- Create and edit own maps and datasets
- Run basic analysis
- Share content

### Analyst
- Advanced analysis capabilities
- Manage datasets
- Delete own content

### Editor
- Manage all content
- Create and edit users
- Advanced sharing permissions

### Administrator
- Full system administration
- User management
- System configuration

## Subscription Tiers

### Free Tier
- 5 users maximum
- 1 GB storage
- 10 maps, 25 datasets
- 1,000 API calls/month
- Basic features only

### Basic Tier
- 25 users maximum
- 10 GB storage
- 100 maps, 500 datasets
- 50,000 API calls/month
- OAuth integration

### Professional Tier
- 100 users maximum
- 100 GB storage
- 1,000 maps, 5,000 datasets
- 500,000 API calls/month
- All features

### Enterprise Tier
- 1,000 users maximum
- 1 TB storage
- 10,000 maps, 50,000 datasets
- 5,000,000 API calls/month
- Custom features

## Security Best Practices

1. **Use Strong JWT Secrets**: Generate cryptographically secure secret keys
2. **Enable HTTPS**: Always use HTTPS in production
3. **Regular Key Rotation**: Rotate JWT secrets and API keys regularly
4. **Principle of Least Privilege**: Grant minimum required permissions
5. **Monitor Access**: Log and monitor authentication attempts
6. **Secure OAuth**: Validate OAuth state parameters

## Configuration

### Environment Variables

```bash
# Authentication
PYMAPGIS_JWT_SECRET_KEY=your-secret-key
PYMAPGIS_JWT_EXPIRATION_HOURS=24

# OAuth
PYMAPGIS_GOOGLE_CLIENT_ID=your-google-client-id
PYMAPGIS_GOOGLE_CLIENT_SECRET=your-google-client-secret
PYMAPGIS_GITHUB_CLIENT_ID=your-github-client-id
PYMAPGIS_GITHUB_CLIENT_SECRET=your-github-client-secret

# Database (if using external storage)
PYMAPGIS_DATABASE_URL=postgresql://user:pass@localhost/pymapgis
PYMAPGIS_REDIS_URL=redis://localhost:6379/0
```

### Configuration File

```python
ENTERPRISE_CONFIG = {
    "auth": {
        "jwt_secret_key": "your-secret-key",
        "jwt_algorithm": "HS256",
        "jwt_expiration_hours": 24,
        "session_timeout_minutes": 60,
        "password_min_length": 8,
        "require_email_verification": True,
    },
    "rbac": {
        "default_user_role": "user",
        "admin_role": "admin",
        "enable_resource_permissions": True,
    },
    "oauth": {
        "enabled_providers": ["google", "github"],
        "redirect_uri": "/auth/oauth/callback",
    },
    "tenants": {
        "enable_multi_tenant": True,
        "default_tenant": "default",
        "max_users_per_tenant": 100,
    },
}
```

## API Integration

### FastAPI Integration

```python
from fastapi import FastAPI, Depends, HTTPException
from pymapgis.enterprise import require_auth, require_role

app = FastAPI()

@app.get("/api/maps")
@require_auth
def get_maps(current_user: User = Depends(get_current_user)):
    """Get user's maps."""
    return {"maps": []}

@app.post("/api/admin/users")
@require_role("admin")
def create_user(user_data: dict, current_user: User = Depends(get_current_user)):
    """Admin-only user creation."""
    return {"message": "User created"}
```

## Next Steps

1. **Setup Authentication**: Configure JWT secrets and password policies
2. **Define Roles**: Customize roles and permissions for your use case
3. **Configure OAuth**: Set up OAuth providers for social login
4. **Create Organizations**: Set up multi-tenant structure
5. **Integrate with Frontend**: Connect with your web application
6. **Monitor Usage**: Implement logging and monitoring

For detailed API documentation, see the individual module documentation:
- [Authentication API](auth.md)
- [User Management API](users.md)
- [RBAC API](rbac.md)
- [OAuth API](oauth.md)
- [Multi-Tenant API](tenants.md)
