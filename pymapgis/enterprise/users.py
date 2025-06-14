"""
User Management System

Provides user registration, profile management, and user operations
for PyMapGIS enterprise features.
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class UserRole(Enum):
    """User role enumeration."""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"
    ANALYST = "analyst"
    EDITOR = "editor"


@dataclass
class UserProfile:
    """User profile data structure."""
    first_name: str
    last_name: str
    organization: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}".strip()


@dataclass
class User:
    """User data structure."""
    user_id: str
    username: str
    email: str
    password_hash: str
    roles: List[UserRole]
    profile: UserProfile
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = None
    updated_at: datetime = None
    last_login: Optional[datetime] = None
    tenant_id: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
            
    def has_role(self, role: UserRole) -> bool:
        """Check if user has a specific role."""
        return role in self.roles
        
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return UserRole.ADMIN in self.roles
        
    def can_edit(self) -> bool:
        """Check if user can edit content."""
        return any(role in self.roles for role in [UserRole.ADMIN, UserRole.EDITOR, UserRole.ANALYST])
        
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert user to dictionary."""
        data = asdict(self)
        if not include_sensitive:
            data.pop('password_hash', None)
        data['roles'] = [role.value for role in self.roles]
        return data


class UserManager:
    """User management system."""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.username_index: Dict[str, str] = {}  # username -> user_id
        self.email_index: Dict[str, str] = {}     # email -> user_id
        
    def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        profile: UserProfile,
        roles: Optional[List[UserRole]] = None,
        tenant_id: Optional[str] = None
    ) -> User:
        """Create a new user."""
        # Validate uniqueness
        if username in self.username_index:
            raise ValueError(f"Username '{username}' already exists")
        if email in self.email_index:
            raise ValueError(f"Email '{email}' already exists")
            
        # Generate user ID
        user_id = str(uuid.uuid4())
        
        # Set default role if none provided
        if roles is None:
            roles = [UserRole.USER]
            
        # Create user
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            roles=roles,
            profile=profile,
            tenant_id=tenant_id
        )
        
        # Store user and update indices
        self.users[user_id] = user
        self.username_index[username] = user_id
        self.email_index[email] = user_id
        
        logger.info(f"Created user: {username} ({email})")
        return user
        
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)
        
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        user_id = self.username_index.get(username)
        return self.users.get(user_id) if user_id else None
        
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        user_id = self.email_index.get(email)
        return self.users.get(user_id) if user_id else None
        
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Optional[User]:
        """Update user information."""
        user = self.users.get(user_id)
        if not user:
            return None
            
        # Handle username change
        if 'username' in updates and updates['username'] != user.username:
            new_username = updates['username']
            if new_username in self.username_index:
                raise ValueError(f"Username '{new_username}' already exists")
            # Update index
            del self.username_index[user.username]
            self.username_index[new_username] = user_id
            user.username = new_username
            
        # Handle email change
        if 'email' in updates and updates['email'] != user.email:
            new_email = updates['email']
            if new_email in self.email_index:
                raise ValueError(f"Email '{new_email}' already exists")
            # Update index
            del self.email_index[user.email]
            self.email_index[new_email] = user_id
            user.email = new_email
            
        # Handle other updates
        for key, value in updates.items():
            if key in ['username', 'email']:
                continue  # Already handled
            elif key == 'roles' and isinstance(value, list):
                user.roles = [UserRole(role) if isinstance(role, str) else role for role in value]
            elif key == 'profile' and isinstance(value, dict):
                # Update profile fields
                for profile_key, profile_value in value.items():
                    if hasattr(user.profile, profile_key):
                        setattr(user.profile, profile_key, profile_value)
            elif hasattr(user, key):
                setattr(user, key, value)
                
        user.updated_at = datetime.utcnow()
        logger.info(f"Updated user: {user.username}")
        return user
        
    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        user = self.users.get(user_id)
        if not user:
            return False
            
        # Remove from indices
        self.username_index.pop(user.username, None)
        self.email_index.pop(user.email, None)
        
        # Remove user
        del self.users[user_id]
        
        logger.info(f"Deleted user: {user.username}")
        return True
        
    def list_users(
        self,
        tenant_id: Optional[str] = None,
        role: Optional[UserRole] = None,
        active_only: bool = True
    ) -> List[User]:
        """List users with optional filtering."""
        users = list(self.users.values())
        
        if tenant_id:
            users = [u for u in users if u.tenant_id == tenant_id]
            
        if role:
            users = [u for u in users if role in u.roles]
            
        if active_only:
            users = [u for u in users if u.is_active]
            
        return users
        
    def search_users(self, query: str, limit: int = 50) -> List[User]:
        """Search users by username, email, or name."""
        query = query.lower()
        results: List[User] = []
        
        for user in self.users.values():
            if len(results) >= limit:
                break
                
            # Search in username, email, and full name
            if (query in user.username.lower() or
                query in user.email.lower() or
                query in user.profile.full_name.lower()):
                results.append(user)
                
        return results
        
    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics."""
        total_users = len(self.users)
        active_users = len([u for u in self.users.values() if u.is_active])
        verified_users = len([u for u in self.users.values() if u.is_verified])
        
        # Role distribution
        role_counts: Dict[str, int] = {}
        for user in self.users.values():
            for role in user.roles:
                role_counts[role.value] = role_counts.get(role.value, 0) + 1
                
        return {
            "total_users": total_users,
            "active_users": active_users,
            "verified_users": verified_users,
            "role_distribution": role_counts,
            "recent_registrations": len([
                u for u in self.users.values()
                if (datetime.utcnow() - u.created_at).days <= 7
            ])
        }


# Convenience functions
def create_user(
    username: str,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    user_manager: UserManager,
    auth_manager,
    **kwargs
) -> User:
    """Create a new user with profile."""
    
    # Hash password
    password_hash = auth_manager.hash_password(password)
    
    # Create profile
    profile = UserProfile(
        first_name=first_name,
        last_name=last_name,
        **{k: v for k, v in kwargs.items() if hasattr(UserProfile, k)}
    )
    
    # Create user
    return user_manager.create_user(
        username=username,
        email=email,
        password_hash=password_hash,
        profile=profile,
        **{k: v for k, v in kwargs.items() if k in ['roles', 'tenant_id']}
    )


def get_user(user_id: str, user_manager: UserManager) -> Optional[User]:
    """Get user by ID."""
    return user_manager.get_user(user_id)


def update_user(user_id: str, updates: Dict[str, Any], user_manager: UserManager) -> Optional[User]:
    """Update user information."""
    return user_manager.update_user(user_id, updates)


def delete_user(user_id: str, user_manager: UserManager) -> bool:
    """Delete a user."""
    return user_manager.delete_user(user_id)
