"""
OAuth 2.0 Integration System

Provides OAuth 2.0 authentication with support for multiple providers
including Google, Microsoft, GitHub, and custom providers.
"""

import json
import time
import secrets
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from urllib.parse import urlencode, parse_qs
import base64

logger = logging.getLogger(__name__)

# Optional imports for OAuth providers
try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests not available - OAuth functionality limited")

try:
    import jwt

    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    logger.warning("PyJWT not available - JWT token validation limited")


@dataclass
class OAuthToken:
    """OAuth token data structure."""

    access_token: str
    refresh_token: Optional[str]
    token_type: str
    expires_at: datetime
    scope: List[str]
    provider: str
    user_info: Dict[str, Any]

    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.utcnow() >= self.expires_at

    def expires_soon(self, threshold_minutes: int = 5) -> bool:
        """Check if token expires soon."""
        threshold = datetime.utcnow() + timedelta(minutes=threshold_minutes)
        return self.expires_at <= threshold

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["expires_at"] = self.expires_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OAuthToken":
        """Create from dictionary."""
        data["expires_at"] = datetime.fromisoformat(data["expires_at"])
        return cls(**data)


class OAuthProvider(ABC):
    """Abstract OAuth provider base class."""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        """
        Initialize OAuth provider.

        Args:
            client_id: OAuth client ID
            client_secret: OAuth client secret
            redirect_uri: Redirect URI for OAuth flow
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Provider name."""
        pass

    @property
    @abstractmethod
    def auth_url(self) -> str:
        """Authorization URL."""
        pass

    @property
    @abstractmethod
    def token_url(self) -> str:
        """Token exchange URL."""
        pass

    @property
    @abstractmethod
    def user_info_url(self) -> str:
        """User info URL."""
        pass

    @property
    @abstractmethod
    def default_scopes(self) -> List[str]:
        """Default OAuth scopes."""
        pass

    def get_auth_url(
        self, state: Optional[str] = None, scopes: Optional[List[str]] = None
    ) -> str:
        """
        Get authorization URL for OAuth flow.

        Args:
            state: State parameter for CSRF protection
            scopes: OAuth scopes to request

        Returns:
            Authorization URL
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library required for OAuth")

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes or self.default_scopes),
        }

        if state:
            params["state"] = state

        return f"{self.auth_url}?{urlencode(params)}"

    def exchange_code(self, code: str, state: Optional[str] = None) -> OAuthToken:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code
            state: State parameter for verification

        Returns:
            OAuth token
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library required for OAuth")

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri,
        }

        response = requests.post(self.token_url, data=data)
        response.raise_for_status()

        token_data = response.json()
        user_info = self._get_user_info(token_data["access_token"])

        expires_at = datetime.utcnow() + timedelta(
            seconds=token_data.get("expires_in", 3600)
        )

        return OAuthToken(
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            token_type=token_data.get("token_type", "Bearer"),
            expires_at=expires_at,
            scope=token_data.get("scope", "").split(),
            provider=self.provider_name,
            user_info=user_info,
        )

    def refresh_token(self, refresh_token: str) -> OAuthToken:
        """
        Refresh an OAuth token.

        Args:
            refresh_token: Refresh token

        Returns:
            New OAuth token
        """
        if not REQUESTS_AVAILABLE:
            raise ImportError("requests library required for OAuth")

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        response = requests.post(self.token_url, data=data)
        response.raise_for_status()

        token_data = response.json()
        user_info = self._get_user_info(token_data["access_token"])

        expires_at = datetime.utcnow() + timedelta(
            seconds=token_data.get("expires_in", 3600)
        )

        return OAuthToken(
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token", refresh_token),
            token_type=token_data.get("token_type", "Bearer"),
            expires_at=expires_at,
            scope=token_data.get("scope", "").split(),
            provider=self.provider_name,
            user_info=user_info,
        )

    def _get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from provider."""
        if not REQUESTS_AVAILABLE:
            return {}

        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(self.user_info_url, headers=headers)

        if response.status_code == 200:
            return response.json()
        return {}


class GoogleOAuthProvider(OAuthProvider):
    """Google OAuth provider."""

    @property
    def provider_name(self) -> str:
        return "google"

    @property
    def auth_url(self) -> str:
        return "https://accounts.google.com/o/oauth2/v2/auth"

    @property
    def token_url(self) -> str:
        return "https://oauth2.googleapis.com/token"

    @property
    def user_info_url(self) -> str:
        return "https://www.googleapis.com/oauth2/v2/userinfo"

    @property
    def default_scopes(self) -> List[str]:
        return ["openid", "email", "profile"]


class MicrosoftOAuthProvider(OAuthProvider):
    """Microsoft OAuth provider."""

    @property
    def provider_name(self) -> str:
        return "microsoft"

    @property
    def auth_url(self) -> str:
        return "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"

    @property
    def token_url(self) -> str:
        return "https://login.microsoftonline.com/common/oauth2/v2.0/token"

    @property
    def user_info_url(self) -> str:
        return "https://graph.microsoft.com/v1.0/me"

    @property
    def default_scopes(self) -> List[str]:
        return ["openid", "email", "profile", "User.Read"]


class GitHubOAuthProvider(OAuthProvider):
    """GitHub OAuth provider."""

    @property
    def provider_name(self) -> str:
        return "github"

    @property
    def auth_url(self) -> str:
        return "https://github.com/login/oauth/authorize"

    @property
    def token_url(self) -> str:
        return "https://github.com/login/oauth/access_token"

    @property
    def user_info_url(self) -> str:
        return "https://api.github.com/user"

    @property
    def default_scopes(self) -> List[str]:
        return ["user:email", "read:user"]


class OAuthManager:
    """OAuth management system."""

    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize OAuth manager.

        Args:
            storage_path: Path to store OAuth data
        """
        self.storage_path = (
            storage_path or Path.home() / ".pymapgis" / "oauth_tokens.json"
        )
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        self.providers: Dict[str, OAuthProvider] = {}
        self.tokens: Dict[str, OAuthToken] = {}  # user_id -> token
        self.sessions: Dict[str, Dict[str, Any]] = {}  # session_id -> session_data

        self._load_tokens()

    def register_provider(self, provider: OAuthProvider) -> None:
        """Register an OAuth provider."""
        self.providers[provider.provider_name] = provider
        logger.info(f"Registered OAuth provider: {provider.provider_name}")

    def start_auth_flow(self, provider_name: str, user_id: str) -> tuple[str, str]:
        """
        Start OAuth authentication flow.

        Args:
            provider_name: Name of OAuth provider
            user_id: User identifier

        Returns:
            tuple: (auth_url, session_id)
        """
        if provider_name not in self.providers:
            raise ValueError(f"Unknown OAuth provider: {provider_name}")

        provider = self.providers[provider_name]
        session_id = secrets.token_urlsafe(32)
        state = secrets.token_urlsafe(16)

        # Store session data
        self.sessions[session_id] = {
            "user_id": user_id,
            "provider": provider_name,
            "state": state,
            "created_at": datetime.utcnow().isoformat(),
        }

        auth_url = provider.get_auth_url(state=state)
        return auth_url, session_id

    def complete_auth_flow(self, session_id: str, code: str, state: str) -> OAuthToken:
        """
        Complete OAuth authentication flow.

        Args:
            session_id: Session ID from start_auth_flow
            code: Authorization code from provider
            state: State parameter for verification

        Returns:
            OAuth token
        """
        if session_id not in self.sessions:
            raise ValueError("Invalid session ID")

        session_data = self.sessions[session_id]

        # Verify state parameter
        if session_data["state"] != state:
            raise ValueError("Invalid state parameter")

        provider = self.providers[session_data["provider"]]
        token = provider.exchange_code(code, state)

        # Store token
        user_id = session_data["user_id"]
        self.tokens[user_id] = token
        self._save_tokens()

        # Clean up session
        del self.sessions[session_id]

        logger.info(
            f"Completed OAuth flow for user {user_id} with provider {provider.provider_name}"
        )
        return token

    def get_token(self, user_id: str) -> Optional[OAuthToken]:
        """Get OAuth token for user."""
        return self.tokens.get(user_id)

    def validate_token(self, access_token: str) -> Optional[str]:
        """
        Validate OAuth token and return user ID.

        Args:
            access_token: Access token to validate

        Returns:
            User ID if token is valid, None otherwise
        """
        for user_id, token in self.tokens.items():
            if token.access_token == access_token and not token.is_expired():
                return user_id
        return None

    def refresh_user_token(self, user_id: str) -> Optional[OAuthToken]:
        """Refresh OAuth token for user."""
        if user_id not in self.tokens:
            return None

        token = self.tokens[user_id]
        if not token.refresh_token:
            return None

        provider = self.providers[token.provider]
        new_token = provider.refresh_token(token.refresh_token)

        self.tokens[user_id] = new_token
        self._save_tokens()

        return new_token

    def revoke_token(self, user_id: str) -> bool:
        """Revoke OAuth token for user."""
        if user_id in self.tokens:
            del self.tokens[user_id]
            self._save_tokens()
            return True
        return False

    def _load_tokens(self) -> None:
        """Load OAuth tokens from storage."""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)

            for user_id, token_data in data.get("tokens", {}).items():
                self.tokens[user_id] = OAuthToken.from_dict(token_data)

        except Exception as e:
            logger.error(f"Failed to load OAuth tokens: {e}")

    def _save_tokens(self) -> None:
        """Save OAuth tokens to storage."""
        try:
            data = {
                "tokens": {
                    user_id: token.to_dict() for user_id, token in self.tokens.items()
                },
                "updated_at": datetime.utcnow().isoformat(),
            }

            with open(self.storage_path, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save OAuth tokens: {e}")


# Convenience functions
def authenticate_oauth(
    provider_name: str, user_id: str, manager: Optional[OAuthManager] = None
) -> tuple[str, str]:
    """Start OAuth authentication flow."""
    if manager is None:
        from . import get_oauth_manager

        manager = get_oauth_manager()

    return manager.start_auth_flow(provider_name, user_id)


def refresh_oauth_token(
    user_id: str, manager: Optional[OAuthManager] = None
) -> Optional[OAuthToken]:
    """Refresh OAuth token for user."""
    if manager is None:
        from . import get_oauth_manager

        manager = get_oauth_manager()

    return manager.refresh_user_token(user_id)
