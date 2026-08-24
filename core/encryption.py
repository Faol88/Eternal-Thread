"""
core.encryption
~~~~~~~~~~~~~~~~
Optional AES/Fernet encryption layer for the Living Memory Core.
Secures stored memory documents and metadata at rest.
"""

import base64
import hashlib
from typing import Optional

try:
    from cryptography.fernet import Fernet, InvalidToken
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False
    Fernet = None
    InvalidToken = Exception

from .logging_config import logger
from .exceptions import EncryptionError


class EncryptionLayer:
    """Handles transparent symmetric encryption and decryption of memory content."""

    def __init__(self, key: Optional[str] = None):
        self.enabled = False
        self._fernet = None
        if key:
            self.setup_key(key)

    def setup_key(self, raw_key: str) -> None:
        """Initializes Fernet cipher using SHA-256 derived key."""
        if not raw_key:
            self.enabled = False
            self._fernet = None
            return

        if not HAS_CRYPTOGRAPHY:
            raise EncryptionError("The 'cryptography' package is required for memory encryption. Install via: pip install cryptography")

        try:
            derived = base64.urlsafe_b64encode(hashlib.sha256(raw_key.encode("utf-8")).digest())
            self._fernet = Fernet(derived)
            self.enabled = True
            logger.info("Memory encryption layer enabled (Fernet AES-128-CBC + HMAC-SHA256).")
        except Exception as e:
            raise EncryptionError(f"Failed to initialize encryption key: {e}") from e

    def encrypt(self, plain_text: str) -> str:
        """Encrypts plain text string if encryption is enabled."""
        if not self.enabled or not plain_text or not self._fernet:
            return plain_text
        try:
            encrypted_bytes = self._fernet.encrypt(plain_text.encode("utf-8"))
            return "ENC:" + encrypted_bytes.decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to encrypt text payload: {e}")
            raise EncryptionError(f"Encryption failed: {e}") from e

    def decrypt(self, cipher_text: str) -> str:
        """Decrypts ciphertext string. Handles unencrypted text gracefully."""
        if not cipher_text:
            return cipher_text
        if not cipher_text.startswith("ENC:"):
            return cipher_text
        if not self.enabled or not self._fernet:
            return "[ENCRYPTED MEMORY - KEY REQUIRED]"
        try:
            raw_cipher = cipher_text[4:]
            decrypted_bytes = self._fernet.decrypt(raw_cipher.encode("utf-8"))
            return decrypted_bytes.decode("utf-8")
        except InvalidToken:
            logger.warning("Decryption failed: Invalid token or incorrect encryption key.")
            return "[DECRYPTION FAILED - INVALID KEY]"
        except Exception as e:
            logger.error(f"Unexpected decryption error: {e}")
            return "[DECRYPTION ERROR]"
