"""
Test suite for PyMapGIS Authentication & Security features.

Tests API key management, OAuth, RBAC, session management,
and security utilities.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta

# Import PyMapGIS auth components
try:
    from pymapgis.auth import (
        APIKeyManager,
        APIKeyScope,
        OAuthManager,
        GoogleOAuthProvider,
        RBACManager,
        ResourceType,
        PermissionType,
        SessionManager,
        SecurityManager,
        SecurityConfig,
        RateLimitMiddleware,
        AuthenticationMiddleware,
        generate_api_key,
        validate_api_key,
        create_role,
        assign_role,
        check_permission,
        create_session,
        validate_session,
        hash_password,
        verify_password,
        generate_secure_token,
    )

    AUTH_AVAILABLE = True
except ImportError:
    AUTH_AVAILABLE = False


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.mark.skipif(not AUTH_AVAILABLE, reason="Authentication module not available")
class TestAPIKeyManager:
    """Test API key management functionality."""

    def test_api_key_generation(self, temp_dir):
        """Test API key generation."""
        manager = APIKeyManager(storage_path=temp_dir / "api_keys.json")

        # Generate API key
        raw_key, api_key = manager.generate_key(
            name="Test Key",
            scopes=[APIKeyScope.READ, APIKeyScope.WRITE],
            expires_in_days=30,
        )

        assert raw_key is not None
        assert len(raw_key) > 20  # Should be reasonably long
        assert api_key.name == "Test Key"
        assert APIKeyScope.READ in api_key.scopes
        assert APIKeyScope.WRITE in api_key.scopes
        assert api_key.is_valid()

    def test_api_key_validation(self, temp_dir):
        """Test API key validation."""
        manager = APIKeyManager(storage_path=temp_dir / "api_keys.json")

        # Generate and validate key
        raw_key, api_key = manager.generate_key(
            name="Validation Test", scopes=[APIKeyScope.READ]
        )

        # Valid key
        validated = manager.validate_key(raw_key, APIKeyScope.READ)
        assert validated is not None
        assert validated.key_id == api_key.key_id

        # Invalid scope
        validated_invalid = manager.validate_key(raw_key, APIKeyScope.ADMIN)
        assert validated_invalid is None

        # Invalid key
        validated_wrong = manager.validate_key("wrong_key")
        assert validated_wrong is None

    def test_api_key_revocation(self, temp_dir):
        """Test API key revocation."""
        manager = APIKeyManager(storage_path=temp_dir / "api_keys.json")

        # Generate key
        raw_key, api_key = manager.generate_key(
            name="Revocation Test", scopes=[APIKeyScope.READ]
        )

        # Revoke key
        revoked = manager.revoke_key(api_key.key_id)
        assert revoked is True

        # Key should no longer validate
        validated = manager.validate_key(raw_key)
        assert validated is None

    def test_api_key_rotation(self, temp_dir):
        """Test API key rotation."""
        manager = APIKeyManager(storage_path=temp_dir / "api_keys.json")

        # Generate original key
        raw_key, api_key = manager.generate_key(
            name="Rotation Test", scopes=[APIKeyScope.READ, APIKeyScope.WRITE]
        )

        # Rotate key
        new_raw_key, new_api_key = manager.rotate_key(api_key.key_id)

        assert new_raw_key != raw_key
        assert new_api_key.key_id != api_key.key_id
        assert new_api_key.scopes == api_key.scopes

        # Old key should be invalid
        old_validated = manager.validate_key(raw_key)
        assert old_validated is None

        # New key should be valid
        new_validated = manager.validate_key(new_raw_key)
        assert new_validated is not None


@pytest.mark.skipif(not AUTH_AVAILABLE, reason="Authentication module not available")
class TestRBACManager:
    """Test RBAC functionality."""

    def test_permission_creation(self, temp_dir):
        """Test permission creation."""
        manager = RBACManager(storage_path=temp_dir / "rbac.json")

        permission = manager.create_permission(
            name="test.read",
            resource_type=ResourceType.DATA,
            permission_type=PermissionType.READ,
            description="Test read permission",
        )

        assert permission.name == "test.read"
        assert permission.resource_type == ResourceType.DATA
        assert permission.permission_type == PermissionType.READ

    def test_role_creation(self, temp_dir):
        """Test role creation."""
        manager = RBACManager(storage_path=temp_dir / "rbac.json")

        # Create permission first
        manager.create_permission(
            name="test.read",
            resource_type=ResourceType.DATA,
            permission_type=PermissionType.READ,
        )

        # Create role
        role = manager.create_role(
            name="test_role", description="Test role", permissions=["test.read"]
        )

        assert role.name == "test_role"
        assert "test.read" in role.permissions

    def test_user_creation_and_role_assignment(self, temp_dir):
        """Test user creation and role assignment."""
        manager = RBACManager(storage_path=temp_dir / "rbac.json")

        # Create user
        user = manager.create_user(
            user_id="test_user", username="testuser", email="test@example.com"
        )

        assert user.user_id == "test_user"
        assert user.username == "testuser"

        # Assign role
        assigned = manager.assign_role("test_user", "viewer")  # Default role
        assert assigned is True

        # Check role assignment
        user_roles = manager.get_user_roles("test_user")
        assert "viewer" in user_roles

    def test_permission_checking(self, temp_dir):
        """Test permission checking."""
        manager = RBACManager(storage_path=temp_dir / "rbac.json")

        # Create user with viewer role (has data.read permission)
        manager.create_user(
            user_id="test_user",
            username="testuser",
            email="test@example.com",
            roles=["viewer"],
        )

        # Check permissions
        can_read = manager.check_permission("test_user", "data.read")
        can_write = manager.check_permission("test_user", "data.write")

        assert can_read is True
        assert can_write is False


@pytest.mark.skipif(not AUTH_AVAILABLE, reason="Authentication module not available")
class TestSessionManager:
    """Test session management functionality."""

    def test_session_creation(self, temp_dir):
        """Test session creation."""
        manager = SessionManager(storage_path=temp_dir / "sessions.json")

        session = manager.create_session(
            user_id="test_user", timeout_seconds=3600, ip_address="192.168.1.1"
        )

        assert session.user_id == "test_user"
        assert session.ip_address == "192.168.1.1"
        assert session.is_valid()

    def test_session_validation(self, temp_dir):
        """Test session validation."""
        manager = SessionManager(storage_path=temp_dir / "sessions.json")

        # Create session
        session = manager.create_session(user_id="test_user", timeout_seconds=3600)

        # Validate session
        validated = manager.validate_session(session.session_id)
        assert validated is not None
        assert validated.session_id == session.session_id

        # Invalid session
        invalid = manager.validate_session("invalid_session_id")
        assert invalid is None

    def test_session_invalidation(self, temp_dir):
        """Test session invalidation."""
        manager = SessionManager(storage_path=temp_dir / "sessions.json")

        # Create session
        session = manager.create_session(user_id="test_user")

        # Invalidate session
        invalidated = manager.invalidate_session(session.session_id)
        assert invalidated is True

        # Session should no longer validate
        validated = manager.validate_session(session.session_id)
        assert validated is None


@pytest.mark.skipif(not AUTH_AVAILABLE, reason="Authentication module not available")
class TestSecurityUtilities:
    """Test security utilities."""

    def test_password_hashing(self):
        """Test password hashing and verification."""
        manager = SecurityManager()

        password = "test_password_123"
        hashed = manager.hash_password(password)

        assert hashed != password
        assert len(hashed) > 20

        # Verify correct password
        assert manager.verify_password(password, hashed) is True

        # Verify wrong password
        assert manager.verify_password("wrong_password", hashed) is False

    def test_token_generation(self):
        """Test secure token generation."""
        manager = SecurityManager()

        token1 = manager.generate_secure_token(32)
        token2 = manager.generate_secure_token(32)

        assert len(token1) > 20
        assert len(token2) > 20
        assert token1 != token2  # Should be unique

    def test_data_encryption(self):
        """Test data encryption (if available)."""
        manager = SecurityManager()

        test_data = "sensitive_data_123"
        encrypted = manager.encrypt_data(test_data)

        if encrypted:  # Only test if encryption is available
            decrypted = manager.decrypt_data(encrypted)
            assert decrypted == test_data
        else:
            # Encryption not available, skip test
            pytest.skip("Encryption not available")


@pytest.mark.skipif(not AUTH_AVAILABLE, reason="Authentication module not available")
class TestMiddleware:
    """Test authentication middleware."""

    def test_rate_limiting(self):
        """Test rate limiting middleware."""
        limiter = RateLimitMiddleware(max_requests=3, window_seconds=60)

        # Should allow first 3 requests
        for i in range(3):
            result = limiter.check_rate_limit("test_client")
            assert result is True

        # Should block 4th request
        with pytest.raises(Exception):  # RateLimitExceeded
            limiter.check_rate_limit("test_client")

    def test_authentication_middleware(self, temp_dir):
        """Test authentication middleware."""
        # Create API key for testing
        api_manager = APIKeyManager(storage_path=temp_dir / "api_keys.json")
        raw_key, api_key = api_manager.generate_key(
            name="Test Key", scopes=[APIKeyScope.READ]
        )

        # Test authentication
        auth_middleware = AuthenticationMiddleware()

        # Test with valid API key
        headers = {"X-API-Key": raw_key}
        user_id = auth_middleware.authenticate_request(headers, {})
        assert user_id is not None
        assert "api_key:" in user_id

        # Test with invalid API key
        headers_invalid = {"X-API-Key": "invalid_key"}
        user_id_invalid = auth_middleware.authenticate_request(headers_invalid, {})
        assert user_id_invalid is None


@pytest.mark.skipif(not AUTH_AVAILABLE, reason="Authentication module not available")
class TestConvenienceFunctions:
    """Test convenience functions."""

    def test_generate_api_key_function(self, temp_dir):
        """Test generate_api_key convenience function."""
        # This would use the global manager, but we'll test the function exists
        assert callable(generate_api_key)

    def test_validate_api_key_function(self, temp_dir):
        """Test validate_api_key convenience function."""
        assert callable(validate_api_key)

    def test_rbac_functions(self, temp_dir):
        """Test RBAC convenience functions."""
        assert callable(create_role)
        assert callable(assign_role)
        assert callable(check_permission)

    def test_session_functions(self, temp_dir):
        """Test session convenience functions."""
        assert callable(create_session)
        assert callable(validate_session)

    def test_security_functions(self, temp_dir):
        """Test security convenience functions."""
        assert callable(hash_password)
        assert callable(verify_password)
        assert callable(generate_secure_token)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
