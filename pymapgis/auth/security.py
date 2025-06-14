"""
Security Utilities

Provides encryption, hashing, and security configuration utilities
for PyMapGIS authentication and security features.
"""

import secrets
import hashlib
import base64
import logging
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Optional imports for advanced security features
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    logger.warning("cryptography not available - advanced encryption features disabled")

try:
    import bcrypt

    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    logger.warning("bcrypt not available - using fallback password hashing")


@dataclass
class SecurityConfig:
    """Security configuration."""

    encryption_key: Optional[str] = None
    password_salt_rounds: int = 12
    token_length: int = 32
    session_timeout: int = 3600
    max_login_attempts: int = 5
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600
    require_https: bool = True
    secure_cookies: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "password_salt_rounds": self.password_salt_rounds,
            "token_length": self.token_length,
            "session_timeout": self.session_timeout,
            "max_login_attempts": self.max_login_attempts,
            "rate_limit_requests": self.rate_limit_requests,
            "rate_limit_window": self.rate_limit_window,
            "require_https": self.require_https,
            "secure_cookies": self.secure_cookies,
        }


class SecurityManager:
    """Security utilities manager."""

    def __init__(self, config: Optional[SecurityConfig] = None):
        """
        Initialize Security Manager.

        Args:
            config: Security configuration
        """
        self.config = config or SecurityConfig()
        self._encryption_key = None

        if self.config.encryption_key:
            self._encryption_key = self.config.encryption_key.encode()
        elif CRYPTOGRAPHY_AVAILABLE:
            self._encryption_key = Fernet.generate_key()

    def generate_secure_token(self, length: Optional[int] = None) -> str:
        """
        Generate a secure random token.

        Args:
            length: Token length (defaults to config value)

        Returns:
            Secure random token
        """
        token_length = length or self.config.token_length
        return secrets.token_urlsafe(token_length)

    def hash_password(self, password: str) -> str:
        """
        Hash a password securely.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        if BCRYPT_AVAILABLE:
            # Use bcrypt for secure password hashing
            salt = bcrypt.gensalt(rounds=self.config.password_salt_rounds)
            hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
            return hashed.decode("utf-8")
        else:
            # Fallback to PBKDF2 with SHA-256
            salt = secrets.token_bytes(32)
            pwdhash = hashlib.pbkdf2_hmac(
                "sha256", password.encode("utf-8"), salt, 100000
            )  # 100k iterations
            return base64.b64encode(salt + pwdhash).decode("utf-8")

    def verify_password(self, password: str, hashed: str) -> bool:
        """
        Verify a password against its hash.

        Args:
            password: Plain text password
            hashed: Hashed password

        Returns:
            bool: True if password matches
        """
        try:
            if BCRYPT_AVAILABLE and hashed.startswith("$2"):
                # bcrypt hash
                return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
            else:
                # PBKDF2 hash
                decoded = base64.b64decode(hashed.encode("utf-8"))
                salt = decoded[:32]
                stored_hash = decoded[32:]
                pwdhash = hashlib.pbkdf2_hmac(
                    "sha256", password.encode("utf-8"), salt, 100000
                )
                return pwdhash == stored_hash
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False

    def encrypt_data(self, data: Union[str, bytes]) -> Optional[str]:
        """
        Encrypt data using symmetric encryption.

        Args:
            data: Data to encrypt

        Returns:
            Encrypted data as base64 string, or None if encryption unavailable
        """
        if not CRYPTOGRAPHY_AVAILABLE or not self._encryption_key:
            logger.warning("Encryption not available")
            return None

        try:
            if isinstance(data, str):
                data = data.encode("utf-8")

            fernet = Fernet(self._encryption_key)
            encrypted = fernet.encrypt(data)
            return base64.b64encode(encrypted).decode("utf-8")
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            return None

    def decrypt_data(self, encrypted_data: str) -> Optional[str]:
        """
        Decrypt data using symmetric encryption.

        Args:
            encrypted_data: Encrypted data as base64 string

        Returns:
            Decrypted data as string, or None if decryption failed
        """
        if not CRYPTOGRAPHY_AVAILABLE or not self._encryption_key:
            logger.warning("Decryption not available")
            return None

        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode("utf-8"))
            fernet = Fernet(self._encryption_key)
            decrypted = fernet.decrypt(encrypted_bytes)
            return decrypted.decode("utf-8")
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            return None

    def generate_key_pair(self) -> Optional[tuple[str, str]]:
        """
        Generate a new encryption key pair.

        Returns:
            tuple: (public_key, private_key) or None if unavailable
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            return None

        try:
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization

            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )

            # Get public key
            public_key = private_key.public_key()

            # Serialize keys
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )

            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )

            return public_pem.decode("utf-8"), private_pem.decode("utf-8")
        except Exception as e:
            logger.error(f"Key generation error: {e}")
            return None

    def hash_data(self, data: Union[str, bytes], algorithm: str = "sha256") -> str:
        """
        Hash data using specified algorithm.

        Args:
            data: Data to hash
            algorithm: Hash algorithm (sha256, sha512, md5)

        Returns:
            Hex digest of hash
        """
        if isinstance(data, str):
            data = data.encode("utf-8")

        if algorithm == "sha256":
            return hashlib.sha256(data).hexdigest()
        elif algorithm == "sha512":
            return hashlib.sha512(data).hexdigest()
        elif algorithm == "md5":
            return hashlib.md5(data).hexdigest()
        else:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    def constant_time_compare(self, a: str, b: str) -> bool:
        """
        Compare two strings in constant time to prevent timing attacks.

        Args:
            a: First string
            b: Second string

        Returns:
            bool: True if strings are equal
        """
        return secrets.compare_digest(a, b)

    def get_encryption_key(self) -> Optional[str]:
        """Get the encryption key (for backup/restore)."""
        if self._encryption_key:
            return base64.b64encode(self._encryption_key).decode("utf-8")
        return None

    def set_encryption_key(self, key: str) -> None:
        """Set the encryption key from base64 string."""
        self._encryption_key = base64.b64decode(key.encode("utf-8"))


# Global security manager instance
_security_manager = None


def get_security_manager() -> SecurityManager:
    """Get the global security manager instance."""
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager


# Convenience functions
def generate_secure_token(length: Optional[int] = None) -> str:
    """Generate a secure random token."""
    return get_security_manager().generate_secure_token(length)


def hash_password(password: str) -> str:
    """Hash a password securely."""
    return get_security_manager().hash_password(password)


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash."""
    return get_security_manager().verify_password(password, hashed)


def encrypt_data(data: Union[str, bytes]) -> Optional[str]:
    """Encrypt data using symmetric encryption."""
    return get_security_manager().encrypt_data(data)


def decrypt_data(encrypted_data: str) -> Optional[str]:
    """Decrypt data using symmetric encryption."""
    return get_security_manager().decrypt_data(encrypted_data)
