"""
OAuth Integration System

Provides OAuth authentication with multiple providers
for PyMapGIS enterprise features.
"""

import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from abc import ABC, abstractmethod
import urllib.parse

logger = logging.getLogger(__name__)

# Check for optional dependencies
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None
    logger.warning("requests not available, OAuth functionality limited")


@dataclass
class OAuthConfig:
    """OAuth provider configuration."""
    client_id: str
    client_secret: str
    redirect_uri: str
    scope: List[str]
    authorize_url: str
    token_url: str
    user_info_url: str


@dataclass
class OAuthState:
    """OAuth state data for security."""
    state: str
    provider: str
    created_at: datetime
    expires_at: datetime
    redirect_after: Optional[str] = None
    
    def is_expired(self) -> bool:
        """Check if state has expired."""
        return datetime.utcnow() > self.expires_at


@dataclass
class OAuthUserInfo:
    """OAuth user information."""
    provider: str
    provider_user_id: str
    email: str
    name: str
    username: Optional[str] = None
    avatar_url: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None


class OAuthProvider(ABC):
    """Abstract OAuth provider."""
    
    def __init__(self, config: OAuthConfig):
        self.config = config
        
    @abstractmethod
    def get_authorization_url(self, state: str) -> str:
        """Get authorization URL for OAuth flow."""
        pass
        
    @abstractmethod
    def exchange_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange authorization code for access token."""
        pass
        
    @abstractmethod
    def get_user_info(self, access_token: str) -> Optional[OAuthUserInfo]:
        """Get user information using access token."""
        pass


class GoogleOAuthProvider(OAuthProvider):
    """Google OAuth provider."""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        config = OAuthConfig(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=["openid", "email", "profile"],
            authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
            token_url="https://oauth2.googleapis.com/token",
            user_info_url="https://www.googleapis.com/oauth2/v2/userinfo"
        )
        super().__init__(config)
        
    def get_authorization_url(self, state: str) -> str:
        """Get Google authorization URL."""
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": " ".join(self.config.scope),
            "response_type": "code",
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        return f"{self.config.authorize_url}?{urllib.parse.urlencode(params)}"
        
    def exchange_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange code for Google access token."""
        if not REQUESTS_AVAILABLE:
            logger.error("requests library required for OAuth")
            return None
            
        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.config.redirect_uri
        }
        
        try:
            response = requests.post(self.config.token_url, data=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Google token exchange failed: {e}")
            return None
            
    def get_user_info(self, access_token: str) -> Optional[OAuthUserInfo]:
        """Get Google user information."""
        if not REQUESTS_AVAILABLE:
            return None
            
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = requests.get(self.config.user_info_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            return OAuthUserInfo(
                provider="google",
                provider_user_id=data["id"],
                email=data["email"],
                name=data["name"],
                username=data.get("email"),  # Google doesn't have username
                avatar_url=data.get("picture"),
                raw_data=data
            )
        except Exception as e:
            logger.error(f"Google user info failed: {e}")
            return None


class GitHubOAuthProvider(OAuthProvider):
    """GitHub OAuth provider."""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        config = OAuthConfig(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=["user:email"],
            authorize_url="https://github.com/login/oauth/authorize",
            token_url="https://github.com/login/oauth/access_token",
            user_info_url="https://api.github.com/user"
        )
        super().__init__(config)
        
    def get_authorization_url(self, state: str) -> str:
        """Get GitHub authorization URL."""
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": " ".join(self.config.scope),
            "state": state
        }
        return f"{self.config.authorize_url}?{urllib.parse.urlencode(params)}"
        
    def exchange_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange code for GitHub access token."""
        if not REQUESTS_AVAILABLE:
            return None
            
        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code
        }
        
        headers = {"Accept": "application/json"}
        
        try:
            response = requests.post(self.config.token_url, data=data, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"GitHub token exchange failed: {e}")
            return None
            
    def get_user_info(self, access_token: str) -> Optional[OAuthUserInfo]:
        """Get GitHub user information."""
        if not REQUESTS_AVAILABLE:
            return None
            
        headers = {"Authorization": f"token {access_token}"}
        
        try:
            # Get user info
            response = requests.get(self.config.user_info_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Get primary email
            email_response = requests.get("https://api.github.com/user/emails", headers=headers)
            email_response.raise_for_status()
            emails = email_response.json()
            primary_email = next((e["email"] for e in emails if e["primary"]), data.get("email"))
            
            return OAuthUserInfo(
                provider="github",
                provider_user_id=str(data["id"]),
                email=primary_email,
                name=data.get("name") or data["login"],
                username=data["login"],
                avatar_url=data.get("avatar_url"),
                raw_data=data
            )
        except Exception as e:
            logger.error(f"GitHub user info failed: {e}")
            return None


class MicrosoftOAuthProvider(OAuthProvider):
    """Microsoft OAuth provider."""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str, tenant: str = "common"):
        config = OAuthConfig(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=["openid", "profile", "email"],
            authorize_url=f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize",
            token_url=f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
            user_info_url="https://graph.microsoft.com/v1.0/me"
        )
        super().__init__(config)
        
    def get_authorization_url(self, state: str) -> str:
        """Get Microsoft authorization URL."""
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": " ".join(self.config.scope),
            "response_type": "code",
            "state": state
        }
        return f"{self.config.authorize_url}?{urllib.parse.urlencode(params)}"
        
    def exchange_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """Exchange code for Microsoft access token."""
        if not REQUESTS_AVAILABLE:
            return None
            
        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.config.redirect_uri
        }
        
        try:
            response = requests.post(self.config.token_url, data=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Microsoft token exchange failed: {e}")
            return None
            
    def get_user_info(self, access_token: str) -> Optional[OAuthUserInfo]:
        """Get Microsoft user information."""
        if not REQUESTS_AVAILABLE:
            return None
            
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            response = requests.get(self.config.user_info_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            return OAuthUserInfo(
                provider="microsoft",
                provider_user_id=data["id"],
                email=data.get("mail") or data.get("userPrincipalName"),
                name=data.get("displayName"),
                username=data.get("userPrincipalName"),
                raw_data=data
            )
        except Exception as e:
            logger.error(f"Microsoft user info failed: {e}")
            return None


class OAuthManager:
    """OAuth management system."""
    
    def __init__(self):
        self.providers: Dict[str, OAuthProvider] = {}
        self.states: Dict[str, OAuthState] = {}
        
    def register_provider(self, name: str, provider: OAuthProvider):
        """Register an OAuth provider."""
        self.providers[name] = provider
        logger.info(f"Registered OAuth provider: {name}")
        
    def create_authorization_url(self, provider_name: str, redirect_after: Optional[str] = None) -> Optional[str]:
        """Create authorization URL for OAuth flow."""
        if provider_name not in self.providers:
            logger.error(f"Unknown OAuth provider: {provider_name}")
            return None
            
        # Generate secure state
        state = secrets.token_urlsafe(32)
        
        # Store state
        oauth_state = OAuthState(
            state=state,
            provider=provider_name,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(minutes=10),
            redirect_after=redirect_after
        )
        self.states[state] = oauth_state
        
        # Get authorization URL
        provider = self.providers[provider_name]
        return provider.get_authorization_url(state)
        
    def handle_callback(self, code: str, state: str) -> Optional[OAuthUserInfo]:
        """Handle OAuth callback."""
        # Validate state
        if state not in self.states:
            logger.error("Invalid OAuth state")
            return None
            
        oauth_state = self.states[state]
        
        # Check expiration
        if oauth_state.is_expired():
            logger.error("OAuth state expired")
            del self.states[state]
            return None
            
        # Get provider
        provider = self.providers[oauth_state.provider]
        
        # Exchange code for token
        token_data = provider.exchange_code_for_token(code)
        if not token_data:
            logger.error("Token exchange failed")
            return None
            
        # Get user info
        access_token = token_data.get("access_token")
        if not access_token:
            logger.error("No access token received")
            return None
            
        user_info = provider.get_user_info(access_token)
        
        # Clean up state
        del self.states[state]
        
        return user_info
        
    def cleanup_expired_states(self):
        """Clean up expired OAuth states."""
        expired_states = [
            state for state, oauth_state in self.states.items()
            if oauth_state.is_expired()
        ]
        
        for state in expired_states:
            del self.states[state]
            
        if expired_states:
            logger.info(f"Cleaned up {len(expired_states)} expired OAuth states")


# Convenience functions
def oauth_login(provider_name: str, oauth_manager: OAuthManager, redirect_after: Optional[str] = None) -> Optional[str]:
    """Start OAuth login flow."""
    return oauth_manager.create_authorization_url(provider_name, redirect_after)


def oauth_callback(code: str, state: str, oauth_manager: OAuthManager) -> Optional[OAuthUserInfo]:
    """Handle OAuth callback."""
    return oauth_manager.handle_callback(code, state)
