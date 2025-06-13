"""
Role-Based Access Control (RBAC) System

Provides comprehensive permission management and access control
for PyMapGIS enterprise features.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Resource type enumeration."""
    MAP = "map"
    DATASET = "dataset"
    LAYER = "layer"
    PROJECT = "project"
    ANALYSIS = "analysis"
    REPORT = "report"
    USER = "user"
    TENANT = "tenant"
    API_KEY = "api_key"


class Action(Enum):
    """Action enumeration."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    SHARE = "share"
    ADMIN = "admin"


@dataclass
class Permission:
    """Permission data structure."""
    permission_id: str
    name: str
    description: str
    resource_type: ResourceType
    actions: List[Action]
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
            
    def allows_action(self, action: Action) -> bool:
        """Check if permission allows specific action."""
        return action in self.actions or Action.ADMIN in self.actions


@dataclass
class Role:
    """Role data structure."""
    role_id: str
    name: str
    description: str
    permissions: List[str]  # Permission IDs
    is_system_role: bool = False
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class Resource:
    """Resource data structure."""
    resource_id: str
    resource_type: ResourceType
    name: str
    owner_id: str
    tenant_id: Optional[str] = None
    is_public: bool = False
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class RBACManager:
    """Role-Based Access Control manager."""
    
    def __init__(self):
        self.permissions: Dict[str, Permission] = {}
        self.roles: Dict[str, Role] = {}
        self.resources: Dict[str, Resource] = {}
        self.user_permissions: Dict[str, Set[str]] = {}  # user_id -> permission_ids
        self.resource_permissions: Dict[str, Dict[str, Set[str]]] = {}  # resource_id -> user_id -> permission_ids
        
        # Initialize default permissions and roles
        self._initialize_default_permissions()
        self._initialize_default_roles()
        
    def _initialize_default_permissions(self):
        """Initialize default system permissions."""
        default_permissions = [
            # Map permissions
            Permission("map_read", "Read Maps", "View maps and their content", ResourceType.MAP, [Action.READ]),
            Permission("map_create", "Create Maps", "Create new maps", ResourceType.MAP, [Action.CREATE]),
            Permission("map_edit", "Edit Maps", "Modify existing maps", ResourceType.MAP, [Action.UPDATE]),
            Permission("map_delete", "Delete Maps", "Remove maps", ResourceType.MAP, [Action.DELETE]),
            Permission("map_share", "Share Maps", "Share maps with others", ResourceType.MAP, [Action.SHARE]),
            
            # Dataset permissions
            Permission("dataset_read", "Read Datasets", "View datasets", ResourceType.DATASET, [Action.READ]),
            Permission("dataset_create", "Create Datasets", "Upload new datasets", ResourceType.DATASET, [Action.CREATE]),
            Permission("dataset_edit", "Edit Datasets", "Modify datasets", ResourceType.DATASET, [Action.UPDATE]),
            Permission("dataset_delete", "Delete Datasets", "Remove datasets", ResourceType.DATASET, [Action.DELETE]),
            
            # Analysis permissions
            Permission("analysis_read", "Read Analysis", "View analysis results", ResourceType.ANALYSIS, [Action.READ]),
            Permission("analysis_create", "Create Analysis", "Run new analysis", ResourceType.ANALYSIS, [Action.CREATE, Action.EXECUTE]),
            Permission("analysis_edit", "Edit Analysis", "Modify analysis", ResourceType.ANALYSIS, [Action.UPDATE]),
            Permission("analysis_delete", "Delete Analysis", "Remove analysis", ResourceType.ANALYSIS, [Action.DELETE]),
            
            # User management permissions
            Permission("user_read", "Read Users", "View user information", ResourceType.USER, [Action.READ]),
            Permission("user_create", "Create Users", "Add new users", ResourceType.USER, [Action.CREATE]),
            Permission("user_edit", "Edit Users", "Modify user accounts", ResourceType.USER, [Action.UPDATE]),
            Permission("user_delete", "Delete Users", "Remove user accounts", ResourceType.USER, [Action.DELETE]),
            Permission("user_admin", "User Admin", "Full user management", ResourceType.USER, [Action.ADMIN]),
            
            # System admin permissions
            Permission("system_admin", "System Admin", "Full system administration", ResourceType.TENANT, [Action.ADMIN]),
        ]
        
        for perm in default_permissions:
            self.permissions[perm.permission_id] = perm
            
    def _initialize_default_roles(self):
        """Initialize default system roles."""
        default_roles = [
            Role(
                "viewer",
                "Viewer",
                "Can view maps, datasets, and analysis results",
                ["map_read", "dataset_read", "analysis_read"],
                is_system_role=True
            ),
            Role(
                "user",
                "User", 
                "Can create and edit own content",
                ["map_read", "map_create", "map_edit", "map_share",
                 "dataset_read", "dataset_create", "dataset_edit",
                 "analysis_read", "analysis_create", "analysis_edit"],
                is_system_role=True
            ),
            Role(
                "analyst",
                "Analyst",
                "Advanced analysis capabilities",
                ["map_read", "map_create", "map_edit", "map_share",
                 "dataset_read", "dataset_create", "dataset_edit", "dataset_delete",
                 "analysis_read", "analysis_create", "analysis_edit", "analysis_delete"],
                is_system_role=True
            ),
            Role(
                "editor",
                "Editor",
                "Can manage content and some users",
                ["map_read", "map_create", "map_edit", "map_delete", "map_share",
                 "dataset_read", "dataset_create", "dataset_edit", "dataset_delete",
                 "analysis_read", "analysis_create", "analysis_edit", "analysis_delete",
                 "user_read", "user_create", "user_edit"],
                is_system_role=True
            ),
            Role(
                "admin",
                "Administrator",
                "Full system administration",
                ["system_admin", "user_admin"],
                is_system_role=True
            ),
        ]
        
        for role in default_roles:
            self.roles[role.role_id] = role
            
    def create_permission(
        self,
        permission_id: str,
        name: str,
        description: str,
        resource_type: ResourceType,
        actions: List[Action]
    ) -> Permission:
        """Create a new permission."""
        if permission_id in self.permissions:
            raise ValueError(f"Permission '{permission_id}' already exists")
            
        permission = Permission(permission_id, name, description, resource_type, actions)
        self.permissions[permission_id] = permission
        
        logger.info(f"Created permission: {permission_id}")
        return permission
        
    def create_role(self, role_id: str, name: str, description: str, permissions: List[str]) -> Role:
        """Create a new role."""
        if role_id in self.roles:
            raise ValueError(f"Role '{role_id}' already exists")
            
        # Validate permissions exist
        for perm_id in permissions:
            if perm_id not in self.permissions:
                raise ValueError(f"Permission '{perm_id}' does not exist")
                
        role = Role(role_id, name, description, permissions)
        self.roles[role_id] = role
        
        logger.info(f"Created role: {role_id}")
        return role
        
    def assign_role_to_user(self, user_id: str, role_id: str):
        """Assign a role to a user."""
        if role_id not in self.roles:
            raise ValueError(f"Role '{role_id}' does not exist")
            
        role = self.roles[role_id]
        
        # Add all role permissions to user
        if user_id not in self.user_permissions:
            self.user_permissions[user_id] = set()
            
        self.user_permissions[user_id].update(role.permissions)
        logger.info(f"Assigned role '{role_id}' to user '{user_id}'")
        
    def grant_permission(self, user_id: str, permission_id: str, resource_id: Optional[str] = None):
        """Grant a specific permission to a user."""
        if permission_id not in self.permissions:
            raise ValueError(f"Permission '{permission_id}' does not exist")
            
        if resource_id:
            # Resource-specific permission
            if resource_id not in self.resource_permissions:
                self.resource_permissions[resource_id] = {}
            if user_id not in self.resource_permissions[resource_id]:
                self.resource_permissions[resource_id][user_id] = set()
            self.resource_permissions[resource_id][user_id].add(permission_id)
        else:
            # Global permission
            if user_id not in self.user_permissions:
                self.user_permissions[user_id] = set()
            self.user_permissions[user_id].add(permission_id)
            
        logger.info(f"Granted permission '{permission_id}' to user '{user_id}'" + 
                   (f" for resource '{resource_id}'" if resource_id else ""))
        
    def revoke_permission(self, user_id: str, permission_id: str, resource_id: Optional[str] = None):
        """Revoke a specific permission from a user."""
        if resource_id:
            # Resource-specific permission
            if (resource_id in self.resource_permissions and 
                user_id in self.resource_permissions[resource_id]):
                self.resource_permissions[resource_id][user_id].discard(permission_id)
        else:
            # Global permission
            if user_id in self.user_permissions:
                self.user_permissions[user_id].discard(permission_id)
                
        logger.info(f"Revoked permission '{permission_id}' from user '{user_id}'" +
                   (f" for resource '{resource_id}'" if resource_id else ""))
        
    def check_permission(
        self,
        user_id: str,
        permission_id: str,
        resource_id: Optional[str] = None
    ) -> bool:
        """Check if user has a specific permission."""
        # Check global permissions
        if user_id in self.user_permissions and permission_id in self.user_permissions[user_id]:
            return True
            
        # Check resource-specific permissions
        if resource_id and resource_id in self.resource_permissions:
            if (user_id in self.resource_permissions[resource_id] and
                permission_id in self.resource_permissions[resource_id][user_id]):
                return True
                
        return False
        
    def check_action(
        self,
        user_id: str,
        resource_type: ResourceType,
        action: Action,
        resource_id: Optional[str] = None
    ) -> bool:
        """Check if user can perform an action on a resource type."""
        # Get all user permissions
        user_perms = set()
        if user_id in self.user_permissions:
            user_perms.update(self.user_permissions[user_id])
            
        if resource_id and resource_id in self.resource_permissions:
            if user_id in self.resource_permissions[resource_id]:
                user_perms.update(self.resource_permissions[resource_id][user_id])
                
        # Check if any permission allows the action
        for perm_id in user_perms:
            if perm_id in self.permissions:
                permission = self.permissions[perm_id]
                if (permission.resource_type == resource_type and
                    permission.allows_action(action)):
                    return True
                    
        return False
        
    def get_user_permissions(self, user_id: str) -> List[Permission]:
        """Get all permissions for a user."""
        perm_ids = set()
        
        # Global permissions
        if user_id in self.user_permissions:
            perm_ids.update(self.user_permissions[user_id])
            
        # Resource-specific permissions
        for resource_perms in self.resource_permissions.values():
            if user_id in resource_perms:
                perm_ids.update(resource_perms[user_id])
                
        return [self.permissions[perm_id] for perm_id in perm_ids if perm_id in self.permissions]


# Convenience functions
def check_permission(user_id: str, permission_id: str, rbac_manager: RBACManager, resource_id: Optional[str] = None) -> bool:
    """Check if user has permission."""
    return rbac_manager.check_permission(user_id, permission_id, resource_id)


def grant_permission(user_id: str, permission_id: str, rbac_manager: RBACManager, resource_id: Optional[str] = None):
    """Grant permission to user."""
    rbac_manager.grant_permission(user_id, permission_id, resource_id)


def revoke_permission(user_id: str, permission_id: str, rbac_manager: RBACManager, resource_id: Optional[str] = None):
    """Revoke permission from user."""
    rbac_manager.revoke_permission(user_id, permission_id, resource_id)
