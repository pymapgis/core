"""
Role-Based Access Control (RBAC) System

Provides comprehensive RBAC functionality with roles, permissions,
and hierarchical access control for PyMapGIS enterprise features.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Optional, Any, Union
from dataclasses import dataclass, asdict, field
from enum import Enum

logger = logging.getLogger(__name__)


class PermissionType(Enum):
    """Permission type enumeration."""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"
    EXECUTE = "execute"


class ResourceType(Enum):
    """Resource type enumeration."""

    DATA = "data"
    CLOUD = "cloud"
    ANALYTICS = "analytics"
    STREAMING = "streaming"
    SYSTEM = "system"
    USER = "user"
    API = "api"


@dataclass
class Permission:
    """Permission data structure."""

    name: str
    resource_type: ResourceType
    permission_type: PermissionType
    resource_pattern: str = "*"  # Resource pattern (supports wildcards)
    description: str = ""

    def matches_resource(self, resource: str) -> bool:
        """Check if permission matches a resource."""
        if self.resource_pattern == "*":
            return True

        # Simple wildcard matching
        if "*" in self.resource_pattern:
            pattern_parts = self.resource_pattern.split("*")
            if len(pattern_parts) == 2:
                prefix, suffix = pattern_parts
                return resource.startswith(prefix) and resource.endswith(suffix)

        return self.resource_pattern == resource

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["resource_type"] = self.resource_type.value
        data["permission_type"] = self.permission_type.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Permission":
        """Create from dictionary."""
        data["resource_type"] = ResourceType(data["resource_type"])
        data["permission_type"] = PermissionType(data["permission_type"])
        return cls(**data)


@dataclass
class Role:
    """Role data structure."""

    name: str
    description: str
    permissions: Set[str] = field(default_factory=set)
    parent_roles: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_permission(self, permission_name: str) -> None:
        """Add permission to role."""
        self.permissions.add(permission_name)

    def remove_permission(self, permission_name: str) -> None:
        """Remove permission from role."""
        self.permissions.discard(permission_name)

    def has_permission(self, permission_name: str) -> bool:
        """Check if role has permission."""
        return permission_name in self.permissions

    def add_parent_role(self, role_name: str) -> None:
        """Add parent role for inheritance."""
        self.parent_roles.add(role_name)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["permissions"] = list(self.permissions)
        data["parent_roles"] = list(self.parent_roles)
        data["created_at"] = self.created_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Role":
        """Create from dictionary."""
        data["permissions"] = set(data["permissions"])
        data["parent_roles"] = set(data["parent_roles"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


@dataclass
class User:
    """User data structure."""

    user_id: str
    username: str
    email: str
    roles: Set[str] = field(default_factory=set)
    direct_permissions: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_role(self, role_name: str) -> None:
        """Add role to user."""
        self.roles.add(role_name)

    def remove_role(self, role_name: str) -> None:
        """Remove role from user."""
        self.roles.discard(role_name)

    def has_role(self, role_name: str) -> bool:
        """Check if user has role."""
        return role_name in self.roles

    def add_permission(self, permission_name: str) -> None:
        """Add direct permission to user."""
        self.direct_permissions.add(permission_name)

    def remove_permission(self, permission_name: str) -> None:
        """Remove direct permission from user."""
        self.direct_permissions.discard(permission_name)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["roles"] = list(self.roles)
        data["direct_permissions"] = list(self.direct_permissions)
        data["created_at"] = self.created_at.isoformat()
        data["last_login"] = self.last_login.isoformat() if self.last_login else None
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Create from dictionary."""
        data["roles"] = set(data["roles"])
        data["direct_permissions"] = set(data["direct_permissions"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["last_login"] = (
            datetime.fromisoformat(data["last_login"]) if data["last_login"] else None
        )
        return cls(**data)


class RBACManager:
    """Role-Based Access Control Manager."""

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize RBAC Manager.

        Args:
            storage_path: Path to store RBAC data
        """
        self.storage_path = storage_path or Path.home() / ".pymapgis" / "rbac.json"
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        self.permissions: Dict[str, Permission] = {}
        self.roles: Dict[str, Role] = {}
        self.users: Dict[str, User] = {}

        self._load_data()
        self._create_default_permissions()
        self._create_default_roles()

    def create_permission(
        self,
        name: str,
        resource_type: ResourceType,
        permission_type: PermissionType,
        resource_pattern: str = "*",
        description: str = "",
    ) -> Permission:
        """Create a new permission."""
        permission = Permission(
            name=name,
            resource_type=resource_type,
            permission_type=permission_type,
            resource_pattern=resource_pattern,
            description=description,
        )

        self.permissions[name] = permission
        self._save_data()

        logger.info(f"Created permission: {name}")
        return permission

    def create_role(
        self, name: str, description: str, permissions: Optional[List[str]] = None
    ) -> Role:
        """Create a new role."""
        role = Role(
            name=name, description=description, permissions=set(permissions or [])
        )

        self.roles[name] = role
        self._save_data()

        logger.info(f"Created role: {name}")
        return role

    def create_user(
        self, user_id: str, username: str, email: str, roles: Optional[List[str]] = None
    ) -> User:
        """Create a new user."""
        user = User(
            user_id=user_id, username=username, email=email, roles=set(roles or [])
        )

        self.users[user_id] = user
        self._save_data()

        logger.info(f"Created user: {username} ({user_id})")
        return user

    def assign_role(self, user_id: str, role_name: str) -> bool:
        """Assign role to user."""
        if user_id not in self.users or role_name not in self.roles:
            return False

        self.users[user_id].add_role(role_name)
        self._save_data()

        logger.info(f"Assigned role {role_name} to user {user_id}")
        return True

    def revoke_role(self, user_id: str, role_name: str) -> bool:
        """Revoke role from user."""
        if user_id not in self.users:
            return False

        self.users[user_id].remove_role(role_name)
        self._save_data()

        logger.info(f"Revoked role {role_name} from user {user_id}")
        return True

    def check_permission(
        self, user_id: str, permission_name: str, resource: str = "*"
    ) -> bool:
        """
        Check if user has permission for resource.

        Args:
            user_id: User identifier
            permission_name: Permission to check
            resource: Resource identifier

        Returns:
            bool: True if user has permission
        """
        if user_id not in self.users:
            return False

        user = self.users[user_id]

        if not user.is_active:
            return False

        # Check direct permissions
        if permission_name in user.direct_permissions:
            permission = self.permissions.get(permission_name)
            if permission and permission.matches_resource(resource):
                return True

        # Check role-based permissions
        all_permissions = self._get_user_permissions(user_id)
        if permission_name in all_permissions:
            permission = self.permissions.get(permission_name)
            if permission and permission.matches_resource(resource):
                return True

        return False

    def get_user_permissions(self, user_id: str) -> Set[str]:
        """Get all permissions for user (direct + role-based)."""
        return self._get_user_permissions(user_id)

    def get_user_roles(self, user_id: str) -> Set[str]:
        """Get all roles for user (direct + inherited)."""
        if user_id not in self.users:
            return set()

        return self._get_all_roles(self.users[user_id].roles)

    def _get_user_permissions(self, user_id: str) -> Set[str]:
        """Get all permissions for user including inherited."""
        if user_id not in self.users:
            return set()

        user = self.users[user_id]
        permissions = user.direct_permissions.copy()

        # Add permissions from roles
        all_roles = self._get_all_roles(user.roles)
        for role_name in all_roles:
            if role_name in self.roles:
                permissions.update(self.roles[role_name].permissions)

        return permissions

    def _get_all_roles(self, role_names: Set[str]) -> Set[str]:
        """Get all roles including inherited parent roles."""
        all_roles = set()
        to_process = list(role_names)

        while to_process:
            role_name = to_process.pop()
            if role_name in all_roles or role_name not in self.roles:
                continue

            all_roles.add(role_name)
            role = self.roles[role_name]
            to_process.extend(role.parent_roles)

        return all_roles

    def _create_default_permissions(self) -> None:
        """Create default permissions if they don't exist."""
        default_permissions = [
            ("data.read", ResourceType.DATA, PermissionType.READ, "*", "Read data"),
            ("data.write", ResourceType.DATA, PermissionType.WRITE, "*", "Write data"),
            (
                "data.delete",
                ResourceType.DATA,
                PermissionType.DELETE,
                "*",
                "Delete data",
            ),
            (
                "cloud.read",
                ResourceType.CLOUD,
                PermissionType.READ,
                "*",
                "Read cloud data",
            ),
            (
                "cloud.write",
                ResourceType.CLOUD,
                PermissionType.WRITE,
                "*",
                "Write cloud data",
            ),
            (
                "analytics.execute",
                ResourceType.ANALYTICS,
                PermissionType.EXECUTE,
                "*",
                "Execute analytics",
            ),
            (
                "system.admin",
                ResourceType.SYSTEM,
                PermissionType.ADMIN,
                "*",
                "System administration",
            ),
        ]

        for (
            name,
            resource_type,
            permission_type,
            pattern,
            description,
        ) in default_permissions:
            if name not in self.permissions:
                self.create_permission(
                    name, resource_type, permission_type, pattern, description
                )

    def _create_default_roles(self) -> None:
        """Create default roles if they don't exist."""
        default_roles = [
            ("viewer", "Read-only access", ["data.read", "cloud.read"]),
            (
                "editor",
                "Read and write access",
                ["data.read", "data.write", "cloud.read", "cloud.write"],
            ),
            (
                "analyst",
                "Analytics access",
                ["data.read", "cloud.read", "analytics.execute"],
            ),
            (
                "admin",
                "Full access",
                [
                    "data.read",
                    "data.write",
                    "data.delete",
                    "cloud.read",
                    "cloud.write",
                    "analytics.execute",
                    "system.admin",
                ],
            ),
        ]

        for name, description, permissions in default_roles:
            if name not in self.roles:
                self.create_role(name, description, permissions)

    def _load_data(self) -> None:
        """Load RBAC data from storage."""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)

            # Load permissions
            for perm_data in data.get("permissions", []):
                permission = Permission.from_dict(perm_data)
                self.permissions[permission.name] = permission

            # Load roles
            for role_data in data.get("roles", []):
                role = Role.from_dict(role_data)
                self.roles[role.name] = role

            # Load users
            for user_data in data.get("users", []):
                user = User.from_dict(user_data)
                self.users[user.user_id] = user

        except Exception as e:
            logger.error(f"Failed to load RBAC data: {e}")

    def _save_data(self) -> None:
        """Save RBAC data to storage."""
        try:
            data = {
                "permissions": [perm.to_dict() for perm in self.permissions.values()],
                "roles": [role.to_dict() for role in self.roles.values()],
                "users": [user.to_dict() for user in self.users.values()],
                "updated_at": datetime.utcnow().isoformat(),
            }

            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save RBAC data: {e}")


# Convenience functions
def create_role(
    name: str,
    description: str,
    permissions: Optional[List[str]] = None,
    manager: Optional[RBACManager] = None,
) -> Role:
    """Create a role using the global manager."""
    if manager is None:
        from . import get_rbac_manager

        manager = get_rbac_manager()

    return manager.create_role(name, description, permissions)


def assign_role(
    user_id: str, role_name: str, manager: Optional[RBACManager] = None
) -> bool:
    """Assign role to user using the global manager."""
    if manager is None:
        from . import get_rbac_manager

        manager = get_rbac_manager()

    return manager.assign_role(user_id, role_name)


def check_permission(
    user_id: str,
    permission_name: str,
    resource: str = "*",
    manager: Optional[RBACManager] = None,
) -> bool:
    """Check permission using the global manager."""
    if manager is None:
        from . import get_rbac_manager

        manager = get_rbac_manager()

    return manager.check_permission(user_id, permission_name, resource)


def has_permission(
    user_id: str,
    permission_name: str,
    resource: str = "*",
    manager: Optional[RBACManager] = None,
) -> bool:
    """Alias for check_permission."""
    return check_permission(user_id, permission_name, resource, manager)
