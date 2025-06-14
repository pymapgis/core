"""
API Key Management System

Provides secure API key generation, validation, and management for PyMapGIS.
Supports key rotation, expiration, and scope-based permissions.
"""

import secrets
import hashlib
import time
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class APIKeyStatus(Enum):
    """API Key status enumeration."""

    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"


class APIKeyScope(Enum):
    """API Key scope enumeration."""

    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    CLOUD_READ = "cloud:read"
    CLOUD_WRITE = "cloud:write"
    ANALYTICS = "analytics"
    STREAMING = "streaming"


@dataclass
class APIKey:
    """API Key data structure."""

    key_id: str
    key_hash: str
    name: str
    scopes: Set[APIKeyScope]
    created_at: datetime
    expires_at: Optional[datetime]
    last_used: Optional[datetime]
    usage_count: int
    status: APIKeyStatus
    metadata: Dict[str, Any]

    def is_valid(self) -> bool:
        """Check if API key is valid."""
        if self.status != APIKeyStatus.ACTIVE:
            return False

        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False

        return True

    def has_scope(self, scope: APIKeyScope) -> bool:
        """Check if API key has required scope."""
        return scope in self.scopes

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["scopes"] = [scope.value for scope in self.scopes]
        data["status"] = self.status.value
        data["created_at"] = self.created_at.isoformat()
        data["expires_at"] = self.expires_at.isoformat() if self.expires_at else None
        data["last_used"] = self.last_used.isoformat() if self.last_used else None
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "APIKey":
        """Create from dictionary."""
        data["scopes"] = {APIKeyScope(scope) for scope in data["scopes"]}
        data["status"] = APIKeyStatus(data["status"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["expires_at"] = (
            datetime.fromisoformat(data["expires_at"]) if data["expires_at"] else None
        )
        data["last_used"] = (
            datetime.fromisoformat(data["last_used"]) if data["last_used"] else None
        )
        return cls(**data)


class APIKeyManager:
    """API Key Management System."""

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize API Key Manager.

        Args:
            storage_path: Path to store API key data
        """
        self.storage_path = storage_path or Path.home() / ".pymapgis" / "api_keys.json"
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        self.keys: Dict[str, APIKey] = {}
        self.key_lookup: Dict[str, str] = {}  # key_hash -> key_id

        self._load_keys()

    def generate_key(
        self,
        name: str,
        scopes: List[APIKeyScope],
        expires_in_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> tuple[str, APIKey]:
        """
        Generate a new API key.

        Args:
            name: Human-readable name for the key
            scopes: List of scopes for the key
            expires_in_days: Number of days until expiration
            metadata: Additional metadata

        Returns:
            tuple: (raw_key, api_key_object)
        """
        # Generate secure random key
        raw_key = secrets.token_urlsafe(32)
        key_hash = self._hash_key(raw_key)
        key_id = secrets.token_hex(16)

        # Calculate expiration
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)

        # Create API key object
        api_key = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            name=name,
            scopes=set(scopes),
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            last_used=None,
            usage_count=0,
            status=APIKeyStatus.ACTIVE,
            metadata=metadata or {},
        )

        # Store key
        self.keys[key_id] = api_key
        self.key_lookup[key_hash] = key_id
        self._save_keys()

        logger.info(f"Generated API key '{name}' with ID {key_id}")
        return raw_key, api_key

    def validate_key(
        self, raw_key: str, required_scope: Optional[APIKeyScope] = None
    ) -> Optional[APIKey]:
        """
        Validate an API key.

        Args:
            raw_key: Raw API key string
            required_scope: Required scope for validation

        Returns:
            APIKey object if valid, None otherwise
        """
        key_hash = self._hash_key(raw_key)
        key_id = self.key_lookup.get(key_hash)

        if not key_id:
            return None

        api_key = self.keys.get(key_id)
        if not api_key or not api_key.is_valid():
            return None

        if required_scope and not api_key.has_scope(required_scope):
            return None

        # Update usage statistics
        api_key.last_used = datetime.utcnow()
        api_key.usage_count += 1
        self._save_keys()

        return api_key

    def revoke_key(self, key_id: str) -> bool:
        """
        Revoke an API key.

        Args:
            key_id: API key ID to revoke

        Returns:
            bool: True if revoked successfully
        """
        if key_id not in self.keys:
            return False

        api_key = self.keys[key_id]
        api_key.status = APIKeyStatus.REVOKED

        # Remove from lookup
        if api_key.key_hash in self.key_lookup:
            del self.key_lookup[api_key.key_hash]

        self._save_keys()
        logger.info(f"Revoked API key {key_id}")
        return True

    def rotate_key(self, key_id: str) -> Optional[tuple[str, APIKey]]:
        """
        Rotate an API key (generate new key with same properties).

        Args:
            key_id: API key ID to rotate

        Returns:
            tuple: (new_raw_key, new_api_key_object) or None
        """
        if key_id not in self.keys:
            return None

        old_key = self.keys[key_id]

        # Generate new key with same properties
        new_raw_key, new_api_key = self.generate_key(
            name=f"{old_key.name} (rotated)",
            scopes=list(old_key.scopes),
            expires_in_days=(
                None
                if not old_key.expires_at
                else (old_key.expires_at - datetime.utcnow()).days
            ),
            metadata=old_key.metadata.copy(),
        )

        # Revoke old key
        self.revoke_key(key_id)

        logger.info(f"Rotated API key {key_id} -> {new_api_key.key_id}")
        return new_raw_key, new_api_key

    def list_keys(self, include_revoked: bool = False) -> List[APIKey]:
        """
        List all API keys.

        Args:
            include_revoked: Include revoked keys in list

        Returns:
            List of API keys
        """
        keys = list(self.keys.values())

        if not include_revoked:
            keys = [key for key in keys if key.status != APIKeyStatus.REVOKED]

        return sorted(keys, key=lambda k: k.created_at, reverse=True)

    def get_key_stats(self) -> Dict[str, Any]:
        """Get API key usage statistics."""
        keys = list(self.keys.values())

        return {
            "total_keys": len(keys),
            "active_keys": len([k for k in keys if k.status == APIKeyStatus.ACTIVE]),
            "expired_keys": len([k for k in keys if k.status == APIKeyStatus.EXPIRED]),
            "revoked_keys": len([k for k in keys if k.status == APIKeyStatus.REVOKED]),
            "total_usage": sum(k.usage_count for k in keys),
            "most_used_key": (
                max(keys, key=lambda k: k.usage_count).name if keys else None
            ),
        }

    def _hash_key(self, raw_key: str) -> str:
        """Hash an API key for secure storage."""
        return hashlib.sha256(raw_key.encode()).hexdigest()

    def _load_keys(self) -> None:
        """Load API keys from storage."""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)

            for key_data in data.get("keys", []):
                api_key = APIKey.from_dict(key_data)
                self.keys[api_key.key_id] = api_key
                self.key_lookup[api_key.key_hash] = api_key.key_id

        except Exception as e:
            logger.error(f"Failed to load API keys: {e}")

    def _save_keys(self) -> None:
        """Save API keys to storage."""
        try:
            data = {
                "keys": [key.to_dict() for key in self.keys.values()],
                "updated_at": datetime.utcnow().isoformat(),
            }

            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save API keys: {e}")


# Convenience functions
def generate_api_key(
    name: str,
    scopes: List[str],
    expires_in_days: Optional[int] = None,
    manager: Optional[APIKeyManager] = None,
) -> tuple[str, APIKey]:
    """Generate an API key using the global manager."""
    if manager is None:
        from . import get_api_key_manager

        manager = get_api_key_manager()

    scope_enums = [APIKeyScope(scope) for scope in scopes]
    return manager.generate_key(name, scope_enums, expires_in_days)


def validate_api_key(
    raw_key: str,
    required_scope: Optional[str] = None,
    manager: Optional[APIKeyManager] = None,
) -> Optional[APIKey]:
    """Validate an API key using the global manager."""
    if manager is None:
        from . import get_api_key_manager

        manager = get_api_key_manager()

    scope_enum = APIKeyScope(required_scope) if required_scope else None
    return manager.validate_key(raw_key, scope_enum)


def rotate_api_key(
    key_id: str, manager: Optional[APIKeyManager] = None
) -> Optional[tuple[str, APIKey]]:
    """Rotate an API key using the global manager."""
    if manager is None:
        from . import get_api_key_manager

        manager = get_api_key_manager()

    return manager.rotate_key(key_id)
