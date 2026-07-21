import os
import base64
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import logging
import yaml
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class EncryptionManager:
    """Manages encryption and decryption of sensitive data."""

    def __init__(self, config_path: str = "security/guardrails_config.yaml"):
        """Initialize encryption manager.

        Args:
            config_path: Path to guardrails configuration file
        """
        self.config = self._load_config(config_path)
        self.master_key = self._get_or_create_master_key()
        self.sensitive_fields = self.config.get("encryption", {}).get(
            "sensitive_fields", []
        )
        self.key_rotation_days = self.config.get("encryption", {}).get(
            "key_rotation_days", 90
        )
        self.last_key_rotation = self._load_last_rotation_time()

    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file.

        Args:
            config_path: Path to configuration file

        Returns:
            Configuration dictionary
        """
        if not os.path.exists(config_path):
            return {"encryption": {"enabled": True, "algorithm": "AES-256-GCM"}}

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        return config

    def _get_or_create_master_key(self) -> bytes:
        """Get or create master encryption key.

        Returns:
            Master encryption key (32 bytes for AES-256)
        """
        key_file = ".encryption_key"

        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()

        master_key = os.urandom(32)
        with open(key_file, "wb") as f:
            f.write(master_key)
        os.chmod(key_file, 0o600)
        logger.info("Master encryption key created")

        return master_key

    def _load_last_rotation_time(self) -> datetime:
        """Load last key rotation timestamp.

        Returns:
            Last rotation datetime or current time if not found
        """
        rotation_file = ".key_rotation_time"

        if os.path.exists(rotation_file):
            with open(rotation_file, "r") as f:
                timestamp_str = f.read().strip()
                return datetime.fromisoformat(timestamp_str)

        return datetime.utcnow()

    def _save_rotation_time(self) -> None:
        """Save current key rotation timestamp."""
        rotation_file = ".key_rotation_time"
        with open(rotation_file, "w") as f:
            f.write(datetime.utcnow().isoformat())

    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext using AES-256-GCM.

        Args:
            plaintext: Text to encrypt

        Returns:
            Base64-encoded ciphertext with nonce and tag
        """
        if not self.config.get("encryption", {}).get("enabled", False):
            return plaintext

        nonce = os.urandom(12)
        cipher = AESGCM(self.master_key)
        ciphertext = cipher.encrypt(nonce, plaintext.encode(), None)

        encrypted_data = nonce + ciphertext
        return base64.b64encode(encrypted_data).decode()

    def decrypt(self, encrypted_text: str) -> str:
        """Decrypt AES-256-GCM encrypted text.

        Args:
            encrypted_text: Base64-encoded encrypted text

        Returns:
            Decrypted plaintext

        Raises:
            ValueError: If decryption fails
        """
        if not self.config.get("encryption", {}).get("enabled", False):
            return encrypted_text

        try:
            encrypted_data = base64.b64decode(encrypted_text)
            nonce = encrypted_data[:12]
            ciphertext = encrypted_data[12:]

            cipher = AESGCM(self.master_key)
            plaintext = cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError("Decryption failed") from e

    def encrypt_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encrypt sensitive fields in a dictionary.

        Args:
            data: Dictionary with potential sensitive fields

        Returns:
            Dictionary with sensitive fields encrypted
        """
        encrypted_data = data.copy()

        for field in self.sensitive_fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt(str(encrypted_data[field]))

        return encrypted_data

    def decrypt_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Decrypt sensitive fields in a dictionary.

        Args:
            data: Dictionary with encrypted sensitive fields

        Returns:
            Dictionary with sensitive fields decrypted
        """
        decrypted_data = data.copy()

        for field in self.sensitive_fields:
            if field in decrypted_data and decrypted_data[field]:
                try:
                    decrypted_data[field] = self.decrypt(str(decrypted_data[field]))
                except ValueError:
                    logger.warning(f"Failed to decrypt field: {field}")

        return decrypted_data

    def should_rotate_key(self) -> bool:
        """Check if key rotation is due.

        Returns:
            True if key rotation is needed
        """
        rotation_due = datetime.utcnow() - self.last_key_rotation
        return rotation_due.days >= self.key_rotation_days

    def rotate_key(self) -> None:
        """Rotate encryption key."""
        logger.info("Rotating encryption key")
        self.master_key = os.urandom(32)
        key_file = ".encryption_key"
        with open(key_file, "wb") as f:
            f.write(self.master_key)
        os.chmod(key_file, 0o600)
        self._save_rotation_time()
        self.last_key_rotation = datetime.utcnow()
        logger.info("Encryption key rotated successfully")

    def hash_password(self, password: str, salt: Optional[bytes] = None) -> tuple:
        """Hash password using PBKDF2.

        Args:
            password: Password to hash
            salt: Optional salt (generated if not provided)

        Returns:
            Tuple of (hashed_password, salt) both base64-encoded
        """
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        hashed = kdf.derive(password.encode())

        return (
            base64.b64encode(hashed).decode(),
            base64.b64encode(salt).decode(),
        )

    def verify_password(self, password: str, hashed_password: str, salt: str) -> bool:
        """Verify password against hash.

        Args:
            password: Password to verify
            hashed_password: Base64-encoded hashed password
            salt: Base64-encoded salt

        Returns:
            True if password matches
        """
        try:
            salt_bytes = base64.b64decode(salt)
            new_hash, _ = self.hash_password(password, salt_bytes)
            return new_hash == hashed_password
        except Exception as e:
            logger.error(f"Password verification failed: {e}")
            return False