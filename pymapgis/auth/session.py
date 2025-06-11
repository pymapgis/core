"""
Session Management System

Provides secure session handling, token management, and session lifecycle
management for PyMapGIS authentication.
"""

import json
import secrets
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class Session:
    """Session data structure."""

    session_id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    last_accessed: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    is_active: bool
    metadata: Dict[str, Any]

    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.utcnow() >= self.expires_at

    def is_valid(self) -> bool:
        """Check if session is valid."""
        return self.is_active and not self.is_expired()

    def refresh(self, timeout_seconds: int = 3600) -> None:
        """Refresh session expiration."""
        self.last_accessed = datetime.utcnow()
        self.expires_at = self.last_accessed + timedelta(seconds=timeout_seconds)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["expires_at"] = self.expires_at.isoformat()
        data["last_accessed"] = self.last_accessed.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Create from dictionary."""
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["expires_at"] = datetime.fromisoformat(data["expires_at"])
        data["last_accessed"] = datetime.fromisoformat(data["last_accessed"])
        return cls(**data)


class SessionManager:
    """Session management system."""

    def __init__(
        self, storage_path: Optional[Path] = None, default_timeout: int = 3600
    ):
        """
        Initialize Session Manager.

        Args:
            storage_path: Path to store session data
            default_timeout: Default session timeout in seconds
        """
        self.storage_path = storage_path or Path.home() / ".pymapgis" / "sessions.json"
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.default_timeout = default_timeout

        self.sessions: Dict[str, Session] = {}
        self.user_sessions: Dict[str, set] = {}  # user_id -> set of session_ids

        self._load_sessions()
        self._cleanup_expired_sessions()

    def create_session(
        self,
        user_id: str,
        timeout_seconds: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Session:
        """
        Create a new session.

        Args:
            user_id: User identifier
            timeout_seconds: Session timeout in seconds
            ip_address: Client IP address
            user_agent: Client user agent
            metadata: Additional session metadata

        Returns:
            Session object
        """
        session_id = secrets.token_urlsafe(32)
        timeout = timeout_seconds or self.default_timeout
        now = datetime.utcnow()

        session = Session(
            session_id=session_id,
            user_id=user_id,
            created_at=now,
            expires_at=now + timedelta(seconds=timeout),
            last_accessed=now,
            ip_address=ip_address,
            user_agent=user_agent,
            is_active=True,
            metadata=metadata or {},
        )

        # Store session
        self.sessions[session_id] = session

        # Track user sessions
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = set()
        self.user_sessions[user_id].add(session_id)

        self._save_sessions()
        logger.info(f"Created session {session_id} for user {user_id}")
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID."""
        return self.sessions.get(session_id)

    def validate_session(
        self, session_id: str, refresh: bool = True
    ) -> Optional[Session]:
        """
        Validate a session.

        Args:
            session_id: Session ID to validate
            refresh: Whether to refresh session expiration

        Returns:
            Session object if valid, None otherwise
        """
        session = self.sessions.get(session_id)

        if not session or not session.is_valid():
            if session:
                self.invalidate_session(session_id)
            return None

        if refresh:
            session.refresh(self.default_timeout)
            self._save_sessions()

        return session

    def invalidate_session(self, session_id: str) -> bool:
        """
        Invalidate a session.

        Args:
            session_id: Session ID to invalidate

        Returns:
            bool: True if session was invalidated
        """
        if session_id not in self.sessions:
            return False

        session = self.sessions[session_id]
        session.is_active = False

        # Remove from user sessions
        user_id = session.user_id
        if user_id in self.user_sessions:
            self.user_sessions[user_id].discard(session_id)
            if not self.user_sessions[user_id]:
                del self.user_sessions[user_id]

        # Remove from sessions
        del self.sessions[session_id]

        self._save_sessions()
        logger.info(f"Invalidated session {session_id}")
        return True

    def invalidate_user_sessions(self, user_id: str) -> int:
        """
        Invalidate all sessions for a user.

        Args:
            user_id: User identifier

        Returns:
            int: Number of sessions invalidated
        """
        if user_id not in self.user_sessions:
            return 0

        session_ids = self.user_sessions[user_id].copy()
        count = 0

        for session_id in session_ids:
            if self.invalidate_session(session_id):
                count += 1

        return count

    def get_user_sessions(
        self, user_id: str, active_only: bool = True
    ) -> list[Session]:
        """
        Get all sessions for a user.

        Args:
            user_id: User identifier
            active_only: Only return active sessions

        Returns:
            List of sessions
        """
        if user_id not in self.user_sessions:
            return []

        sessions = []
        for session_id in self.user_sessions[user_id]:
            session = self.sessions.get(session_id)
            if session and (not active_only or session.is_valid()):
                sessions.append(session)

        return sorted(sessions, key=lambda s: s.last_accessed, reverse=True)

    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.

        Returns:
            int: Number of sessions cleaned up
        """
        return self._cleanup_expired_sessions()

    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        active_sessions = [s for s in self.sessions.values() if s.is_valid()]

        return {
            "total_sessions": len(self.sessions),
            "active_sessions": len(active_sessions),
            "expired_sessions": len(self.sessions) - len(active_sessions),
            "unique_users": len(self.user_sessions),
            "average_session_duration": self._calculate_average_duration(),
        }

    def _cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        expired_sessions = [
            session_id
            for session_id, session in self.sessions.items()
            if not session.is_valid()
        ]

        count = 0
        for session_id in expired_sessions:
            if self.invalidate_session(session_id):
                count += 1

        if count > 0:
            logger.info(f"Cleaned up {count} expired sessions")

        return count

    def _calculate_average_duration(self) -> float:
        """Calculate average session duration in seconds."""
        if not self.sessions:
            return 0.0

        total_duration = 0.0
        count = 0

        for session in self.sessions.values():
            if not session.is_active:
                continue

            duration = (session.last_accessed - session.created_at).total_seconds()
            total_duration += duration
            count += 1

        return total_duration / count if count > 0 else 0.0

    def _load_sessions(self) -> None:
        """Load sessions from storage."""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)

            for session_data in data.get("sessions", []):
                session = Session.from_dict(session_data)
                self.sessions[session.session_id] = session

                # Rebuild user sessions index
                user_id = session.user_id
                if user_id not in self.user_sessions:
                    self.user_sessions[user_id] = set()
                self.user_sessions[user_id].add(session.session_id)

        except Exception as e:
            logger.error(f"Failed to load sessions: {e}")

    def _save_sessions(self) -> None:
        """Save sessions to storage."""
        try:
            data = {
                "sessions": [session.to_dict() for session in self.sessions.values()],
                "updated_at": datetime.utcnow().isoformat(),
            }

            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save sessions: {e}")


# Convenience functions
def create_session(
    user_id: str,
    timeout_seconds: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    manager: Optional[SessionManager] = None,
) -> Session:
    """Create a session using the global manager."""
    if manager is None:
        from . import get_session_manager

        manager = get_session_manager()

    return manager.create_session(
        user_id, timeout_seconds, ip_address, user_agent, metadata
    )


def validate_session(
    session_id: str, refresh: bool = True, manager: Optional[SessionManager] = None
) -> Optional[Session]:
    """Validate a session using the global manager."""
    if manager is None:
        from . import get_session_manager

        manager = get_session_manager()

    return manager.validate_session(session_id, refresh)


def invalidate_session(
    session_id: str, manager: Optional[SessionManager] = None
) -> bool:
    """Invalidate a session using the global manager."""
    if manager is None:
        from . import get_session_manager

        manager = get_session_manager()

    return manager.invalidate_session(session_id)
