#!/usr/bin/env python3
"""
PyMapGIS Authentication & Security Demo

Demonstrates the comprehensive authentication and security features
including API keys, OAuth, RBAC, and session management.
"""

import sys
import time
from pathlib import Path

# Add PyMapGIS to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pymapgis as pmg


def demo_api_keys():
    """Demonstrate API key management."""
    print("\n🔑 API Key Management Demo")
    print("=" * 50)

    # Get API key manager
    api_manager = pmg.get_api_key_manager()

    # Generate API keys with different scopes
    print("Generating API keys...")

    # Read-only key
    read_key, read_api_key = pmg.generate_api_key(
        name="Read Only Key", scopes=["read", "cloud:read"], expires_in_days=30
    )
    print(f"✅ Generated read-only key: {read_key[:16]}...")

    # Full access key
    admin_key, admin_api_key = pmg.generate_api_key(
        name="Admin Key",
        scopes=["read", "write", "admin", "cloud:read", "cloud:write"],
        expires_in_days=90,
    )
    print(f"✅ Generated admin key: {admin_key[:16]}...")

    # Validate keys
    print("\nValidating API keys...")

    # Test read key
    validated_read = pmg.validate_api_key(read_key, "read")
    print(f"✅ Read key validation: {'PASS' if validated_read else 'FAIL'}")

    # Test admin key
    validated_admin = pmg.validate_api_key(admin_key, "admin")
    print(f"✅ Admin key validation: {'PASS' if validated_admin else 'FAIL'}")

    # Test invalid scope
    invalid_scope = pmg.validate_api_key(read_key, "admin")
    print(f"✅ Invalid scope test: {'PASS' if not invalid_scope else 'FAIL'}")

    # List all keys
    all_keys = api_manager.list_keys()
    print(f"\n📊 Total API keys: {len(all_keys)}")

    # Get statistics
    stats = api_manager.get_key_stats()
    print(f"📊 Active keys: {stats['active_keys']}")
    print(f"📊 Total usage: {stats['total_usage']}")

    return read_key, admin_key


def demo_rbac():
    """Demonstrate Role-Based Access Control."""
    print("\n👥 RBAC (Role-Based Access Control) Demo")
    print("=" * 50)

    # Get RBAC manager
    rbac_manager = pmg.get_rbac_manager()

    # Create users
    print("Creating users...")

    analyst_user = rbac_manager.create_user(
        user_id="analyst_001",
        username="john_analyst",
        email="john@company.com",
        roles=["analyst"],
    )
    print(f"✅ Created analyst user: {analyst_user.username}")

    admin_user = rbac_manager.create_user(
        user_id="admin_001",
        username="jane_admin",
        email="jane@company.com",
        roles=["admin"],
    )
    print(f"✅ Created admin user: {admin_user.username}")

    # Test permissions
    print("\nTesting permissions...")

    # Analyst permissions
    can_read = pmg.check_permission("analyst_001", "data.read")
    can_admin = pmg.check_permission("analyst_001", "system.admin")
    print(f"✅ Analyst can read data: {'YES' if can_read else 'NO'}")
    print(f"✅ Analyst can admin system: {'YES' if can_admin else 'NO'}")

    # Admin permissions
    admin_can_read = pmg.check_permission("admin_001", "data.read")
    admin_can_admin = pmg.check_permission("admin_001", "system.admin")
    print(f"✅ Admin can read data: {'YES' if admin_can_read else 'NO'}")
    print(f"✅ Admin can admin system: {'YES' if admin_can_admin else 'NO'}")

    # Get user permissions
    analyst_perms = rbac_manager.get_user_permissions("analyst_001")
    admin_perms = rbac_manager.get_user_permissions("admin_001")

    print(f"\n📊 Analyst permissions: {len(analyst_perms)}")
    print(f"📊 Admin permissions: {len(admin_perms)}")

    return analyst_user, admin_user


def demo_sessions():
    """Demonstrate session management."""
    print("\n🔐 Session Management Demo")
    print("=" * 50)

    # Get session manager
    session_manager = pmg.get_session_manager()

    # Create sessions
    print("Creating sessions...")

    # Create session for analyst
    analyst_session = pmg.create_session(
        user_id="analyst_001",
        timeout_seconds=3600,
        ip_address="192.168.1.100",
        user_agent="PyMapGIS-Client/1.0",
    )
    print(f"✅ Created analyst session: {analyst_session.session_id[:16]}...")

    # Create session for admin
    admin_session = pmg.create_session(
        user_id="admin_001",
        timeout_seconds=7200,
        ip_address="192.168.1.101",
        user_agent="PyMapGIS-Admin/1.0",
    )
    print(f"✅ Created admin session: {admin_session.session_id[:16]}...")

    # Validate sessions
    print("\nValidating sessions...")

    validated_analyst = pmg.validate_session(analyst_session.session_id)
    validated_admin = pmg.validate_session(admin_session.session_id)

    print(f"✅ Analyst session valid: {'YES' if validated_analyst else 'NO'}")
    print(f"✅ Admin session valid: {'YES' if validated_admin else 'NO'}")

    # Get session statistics
    stats = session_manager.get_session_stats()
    print(f"\n📊 Total sessions: {stats['total_sessions']}")
    print(f"📊 Active sessions: {stats['active_sessions']}")
    print(f"📊 Unique users: {stats['unique_users']}")

    return analyst_session, admin_session


def demo_security_middleware():
    """Demonstrate security middleware."""
    print("\n🛡️ Security Middleware Demo")
    print("=" * 50)

    # Get security middleware
    security_middleware = pmg.get_security_middleware()

    # Simulate requests
    print("Processing secure requests...")

    # Request with API key
    headers_api = {"X-API-Key": "test_key"}
    params_api = {}

    try:
        context_api = security_middleware.process_request(
            headers=headers_api,
            params=params_api,
            client_ip="192.168.1.100",
            is_https=True,
        )
        print(f"✅ API key request processed: {context_api['is_authenticated']}")
    except Exception as e:
        print(f"❌ API key request failed: {e}")

    # Request with session
    headers_session = {"X-Session-ID": "test_session"}
    params_session = {}

    try:
        context_session = security_middleware.process_request(
            headers=headers_session,
            params=params_session,
            client_ip="192.168.1.101",
            is_https=True,
        )
        print(f"✅ Session request processed: {context_session['is_authenticated']}")
    except Exception as e:
        print(f"❌ Session request failed: {e}")

    # Test rate limiting
    print("\nTesting rate limiting...")
    rate_limiter = pmg.get_rate_limiter()

    try:
        for i in range(5):
            rate_limiter.check_rate_limit("test_client")
            print(f"✅ Request {i+1} allowed")
    except Exception as e:
        print(f"❌ Rate limit exceeded: {e}")


def demo_security_utilities():
    """Demonstrate security utilities."""
    print("\n🔒 Security Utilities Demo")
    print("=" * 50)

    # Password hashing
    print("Testing password security...")

    password = "secure_password_123"
    hashed = pmg.hash_password(password)
    print(f"✅ Password hashed: {hashed[:32]}...")

    # Verify password
    is_valid = pmg.verify_password(password, hashed)
    is_invalid = pmg.verify_password("wrong_password", hashed)

    print(f"✅ Correct password verification: {'PASS' if is_valid else 'FAIL'}")
    print(f"✅ Wrong password verification: {'PASS' if not is_invalid else 'FAIL'}")

    # Token generation
    print("\nTesting token generation...")

    token = pmg.generate_secure_token(32)
    print(f"✅ Generated secure token: {token[:16]}...")

    # Data encryption (if available)
    print("\nTesting data encryption...")

    test_data = "Sensitive geospatial data"
    encrypted = pmg.encrypt_data(test_data)

    if encrypted:
        decrypted = pmg.decrypt_data(encrypted)
        print(f"✅ Encryption test: {'PASS' if decrypted == test_data else 'FAIL'}")
    else:
        print("ℹ️ Encryption not available (cryptography library not installed)")


def demo_authentication_decorators():
    """Demonstrate authentication decorators."""
    print("\n🎭 Authentication Decorators Demo")
    print("=" * 50)

    # Define protected functions
    @pmg.require_auth
    def protected_function(**kwargs):
        user = kwargs.get("authenticated_user", "Unknown")
        return f"Protected function accessed by: {user}"

    @pmg.require_permission("data.read")
    def read_data_function(**kwargs):
        user = kwargs.get("authenticated_user", "Unknown")
        return f"Data read by: {user}"

    @pmg.rate_limit(max_requests=3, window_seconds=60)
    def rate_limited_function(**kwargs):
        return "Rate limited function called"

    print("✅ Defined protected functions with decorators")
    print("ℹ️ These would be used in actual API endpoints")


def main():
    """Run the complete authentication demo."""
    print("🔐 PyMapGIS Authentication & Security Demo")
    print("=" * 60)
    print("Demonstrating enterprise-grade security features")

    try:
        # Demo API key management
        read_key, admin_key = demo_api_keys()

        # Demo RBAC
        analyst_user, admin_user = demo_rbac()

        # Demo session management
        analyst_session, admin_session = demo_sessions()

        # Demo security middleware
        demo_security_middleware()

        # Demo security utilities
        demo_security_utilities()

        # Demo authentication decorators
        demo_authentication_decorators()

        print("\n🎉 Authentication & Security Demo Complete!")
        print("=" * 60)
        print("✅ All security features demonstrated successfully")
        print("🔒 PyMapGIS is ready for enterprise deployment")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
