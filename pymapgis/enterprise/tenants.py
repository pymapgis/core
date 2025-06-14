"""
Multi-Tenant Support System

Provides organization/workspace isolation and management
for PyMapGIS enterprise features.
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class TenantStatus(Enum):
    """Tenant status enumeration."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    EXPIRED = "expired"


class SubscriptionTier(Enum):
    """Subscription tier enumeration."""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class TenantLimits:
    """Tenant resource limits."""
    max_users: int = 10
    max_storage_gb: int = 5
    max_maps: int = 50
    max_datasets: int = 100
    max_api_calls_per_month: int = 10000
    can_use_advanced_features: bool = False
    can_use_oauth: bool = False
    can_use_api_keys: bool = True


@dataclass
class TenantUsage:
    """Tenant resource usage tracking."""
    current_users: int = 0
    storage_used_gb: float = 0.0
    maps_count: int = 0
    datasets_count: int = 0
    api_calls_this_month: int = 0
    last_updated: datetime = None
    
    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.utcnow()


@dataclass
class Tenant:
    """Tenant data structure."""
    tenant_id: str
    name: str
    slug: str  # URL-friendly identifier
    description: Optional[str] = None
    status: TenantStatus = TenantStatus.ACTIVE
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    limits: TenantLimits = None
    usage: TenantUsage = None
    owner_id: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None
    trial_ends_at: Optional[datetime] = None
    settings: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        if self.limits is None:
            self.limits = self._get_default_limits()
        if self.usage is None:
            self.usage = TenantUsage()
        if self.settings is None:
            self.settings = {}
            
    def _get_default_limits(self) -> TenantLimits:
        """Get default limits based on subscription tier."""
        limits_by_tier = {
            SubscriptionTier.FREE: TenantLimits(
                max_users=5,
                max_storage_gb=1,
                max_maps=10,
                max_datasets=25,
                max_api_calls_per_month=1000,
                can_use_advanced_features=False,
                can_use_oauth=False,
                can_use_api_keys=True
            ),
            SubscriptionTier.BASIC: TenantLimits(
                max_users=25,
                max_storage_gb=10,
                max_maps=100,
                max_datasets=500,
                max_api_calls_per_month=50000,
                can_use_advanced_features=True,
                can_use_oauth=True,
                can_use_api_keys=True
            ),
            SubscriptionTier.PROFESSIONAL: TenantLimits(
                max_users=100,
                max_storage_gb=100,
                max_maps=1000,
                max_datasets=5000,
                max_api_calls_per_month=500000,
                can_use_advanced_features=True,
                can_use_oauth=True,
                can_use_api_keys=True
            ),
            SubscriptionTier.ENTERPRISE: TenantLimits(
                max_users=1000,
                max_storage_gb=1000,
                max_maps=10000,
                max_datasets=50000,
                max_api_calls_per_month=5000000,
                can_use_advanced_features=True,
                can_use_oauth=True,
                can_use_api_keys=True
            ),
        }
        return limits_by_tier.get(self.subscription_tier, limits_by_tier[SubscriptionTier.FREE])
        
    def is_active(self) -> bool:
        """Check if tenant is active."""
        return self.status == TenantStatus.ACTIVE
        
    def is_within_limits(self) -> Dict[str, bool]:
        """Check if tenant is within resource limits."""
        return {
            "users": self.usage.current_users <= self.limits.max_users,
            "storage": self.usage.storage_used_gb <= self.limits.max_storage_gb,
            "maps": self.usage.maps_count <= self.limits.max_maps,
            "datasets": self.usage.datasets_count <= self.limits.max_datasets,
            "api_calls": self.usage.api_calls_this_month <= self.limits.max_api_calls_per_month,
        }
        
    def can_add_user(self) -> bool:
        """Check if tenant can add another user."""
        return self.usage.current_users < self.limits.max_users
        
    def can_create_map(self) -> bool:
        """Check if tenant can create another map."""
        return self.usage.maps_count < self.limits.max_maps
        
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert tenant to dictionary."""
        data = asdict(self)
        data['status'] = self.status.value
        data['subscription_tier'] = self.subscription_tier.value
        return data


@dataclass
class TenantUser:
    """Tenant user association."""
    tenant_id: str
    user_id: str
    role: str = "member"
    joined_at: datetime = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.joined_at is None:
            self.joined_at = datetime.utcnow()


class TenantManager:
    """Multi-tenant management system."""
    
    def __init__(self):
        self.tenants: Dict[str, Tenant] = {}
        self.slug_index: Dict[str, str] = {}  # slug -> tenant_id
        self.tenant_users: Dict[str, List[TenantUser]] = {}  # tenant_id -> users
        self.user_tenants: Dict[str, List[str]] = {}  # user_id -> tenant_ids
        
    def create_tenant(
        self,
        name: str,
        slug: str,
        owner_id: str,
        description: Optional[str] = None,
        subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    ) -> Tenant:
        """Create a new tenant."""
        # Validate slug uniqueness
        if slug in self.slug_index:
            raise ValueError(f"Tenant slug '{slug}' already exists")
            
        # Generate tenant ID
        tenant_id = str(uuid.uuid4())
        
        # Create tenant
        tenant = Tenant(
            tenant_id=tenant_id,
            name=name,
            slug=slug,
            description=description,
            subscription_tier=subscription_tier,
            owner_id=owner_id
        )
        
        # Store tenant and update indices
        self.tenants[tenant_id] = tenant
        self.slug_index[slug] = tenant_id
        
        # Add owner as admin user
        self.add_user_to_tenant(tenant_id, owner_id, "admin")
        
        logger.info(f"Created tenant: {name} ({slug})")
        return tenant
        
    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get tenant by ID."""
        return self.tenants.get(tenant_id)
        
    def get_tenant_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get tenant by slug."""
        tenant_id = self.slug_index.get(slug)
        return self.tenants.get(tenant_id) if tenant_id else None
        
    def update_tenant(self, tenant_id: str, updates: Dict[str, Any]) -> Optional[Tenant]:
        """Update tenant information."""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return None
            
        # Handle slug change
        if 'slug' in updates and updates['slug'] != tenant.slug:
            new_slug = updates['slug']
            if new_slug in self.slug_index:
                raise ValueError(f"Tenant slug '{new_slug}' already exists")
            # Update index
            del self.slug_index[tenant.slug]
            self.slug_index[new_slug] = tenant_id
            tenant.slug = new_slug
            
        # Handle other updates
        for key, value in updates.items():
            if key == 'slug':
                continue  # Already handled
            elif key == 'status' and isinstance(value, str):
                tenant.status = TenantStatus(value)
            elif key == 'subscription_tier' and isinstance(value, str):
                tenant.subscription_tier = SubscriptionTier(value)
                tenant.limits = tenant._get_default_limits()  # Update limits
            elif key == 'settings' and isinstance(value, dict):
                tenant.settings.update(value)
            elif hasattr(tenant, key):
                setattr(tenant, key, value)
                
        tenant.updated_at = datetime.utcnow()
        logger.info(f"Updated tenant: {tenant.name}")
        return tenant
        
    def delete_tenant(self, tenant_id: str) -> bool:
        """Delete a tenant."""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
            
        # Remove from indices
        self.slug_index.pop(tenant.slug, None)
        
        # Remove user associations
        if tenant_id in self.tenant_users:
            for tenant_user in self.tenant_users[tenant_id]:
                user_tenants = self.user_tenants.get(tenant_user.user_id, [])
                if tenant_id in user_tenants:
                    user_tenants.remove(tenant_id)
            del self.tenant_users[tenant_id]
            
        # Remove tenant
        del self.tenants[tenant_id]
        
        logger.info(f"Deleted tenant: {tenant.name}")
        return True
        
    def add_user_to_tenant(self, tenant_id: str, user_id: str, role: str = "member") -> bool:
        """Add user to tenant."""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return False
            
        # Check if tenant can add more users
        if not tenant.can_add_user():
            raise ValueError("Tenant has reached maximum user limit")
            
        # Create tenant user association
        tenant_user = TenantUser(tenant_id=tenant_id, user_id=user_id, role=role)
        
        # Add to tenant users
        if tenant_id not in self.tenant_users:
            self.tenant_users[tenant_id] = []
        self.tenant_users[tenant_id].append(tenant_user)
        
        # Add to user tenants
        if user_id not in self.user_tenants:
            self.user_tenants[user_id] = []
        self.user_tenants[user_id].append(tenant_id)
        
        # Update usage
        tenant.usage.current_users += 1
        tenant.usage.last_updated = datetime.utcnow()
        
        logger.info(f"Added user {user_id} to tenant {tenant.name} as {role}")
        return True
        
    def remove_user_from_tenant(self, tenant_id: str, user_id: str) -> bool:
        """Remove user from tenant."""
        if tenant_id not in self.tenant_users:
            return False
            
        # Find and remove tenant user
        tenant_users = self.tenant_users[tenant_id]
        for i, tenant_user in enumerate(tenant_users):
            if tenant_user.user_id == user_id:
                del tenant_users[i]
                break
        else:
            return False
            
        # Remove from user tenants
        if user_id in self.user_tenants:
            user_tenants = self.user_tenants[user_id]
            if tenant_id in user_tenants:
                user_tenants.remove(tenant_id)
                
        # Update usage
        tenant = self.tenants[tenant_id]
        tenant.usage.current_users = max(0, tenant.usage.current_users - 1)
        tenant.usage.last_updated = datetime.utcnow()
        
        logger.info(f"Removed user {user_id} from tenant {tenant.name}")
        return True
        
    def get_tenant_users(self, tenant_id: str) -> List[TenantUser]:
        """Get all users in a tenant."""
        return self.tenant_users.get(tenant_id, [])
        
    def get_user_tenants(self, user_id: str) -> List[str]:
        """Get all tenants for a user."""
        return self.user_tenants.get(user_id, [])
        
    def is_user_in_tenant(self, user_id: str, tenant_id: str) -> bool:
        """Check if user is in tenant."""
        return tenant_id in self.get_user_tenants(user_id)
        
    def get_user_role_in_tenant(self, user_id: str, tenant_id: str) -> Optional[str]:
        """Get user's role in tenant."""
        tenant_users = self.tenant_users.get(tenant_id, [])
        for tenant_user in tenant_users:
            if tenant_user.user_id == user_id:
                return tenant_user.role
        return None
        
    def update_usage(self, tenant_id: str, usage_updates: Dict[str, Any]):
        """Update tenant usage statistics."""
        tenant = self.tenants.get(tenant_id)
        if not tenant:
            return
            
        for key, value in usage_updates.items():
            if hasattr(tenant.usage, key):
                setattr(tenant.usage, key, value)
                
        tenant.usage.last_updated = datetime.utcnow()
        
    def get_tenant_stats(self) -> Dict[str, Any]:
        """Get tenant statistics."""
        total_tenants = len(self.tenants)
        active_tenants = len([t for t in self.tenants.values() if t.is_active()])
        
        # Subscription distribution
        subscription_counts: Dict[str, int] = {}
        for tenant in self.tenants.values():
            tier = tenant.subscription_tier.value
            subscription_counts[tier] = subscription_counts.get(tier, 0) + 1
            
        return {
            "total_tenants": total_tenants,
            "active_tenants": active_tenants,
            "subscription_distribution": subscription_counts,
            "total_users": sum(len(users) for users in self.tenant_users.values()),
        }


# Convenience functions
def create_tenant(
    name: str,
    slug: str,
    owner_id: str,
    tenant_manager: TenantManager,
    **kwargs
) -> Tenant:
    """Create a new tenant."""
    return tenant_manager.create_tenant(name, slug, owner_id, **kwargs)


def get_tenant(tenant_id: str, tenant_manager: TenantManager) -> Optional[Tenant]:
    """Get tenant by ID."""
    return tenant_manager.get_tenant(tenant_id)


def switch_tenant(user_id: str, tenant_id: str, tenant_manager: TenantManager) -> bool:
    """Switch user's active tenant context."""
    return tenant_manager.is_user_in_tenant(user_id, tenant_id)
