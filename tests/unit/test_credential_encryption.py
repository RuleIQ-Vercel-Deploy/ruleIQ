"""
Unit tests for credential encryption system
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from core.security.credential_encryption import (
    CredentialEncryption,
    encrypt_credentials,
    decrypt_credentials,
    verify_encryption_health,
    CredentialEncryptionError,
    InvalidEncryptionKeyError,
    CredentialDecryptionError,
)

class TestCredentialEncryption:
    """Test cases for CredentialEncryption class"""

    def test_encryption_initialization(self):
        """Test encryption system initialization"""
        with patch.dict(
            "os.environ",
            {"CREDENTIAL_MASTER_KEY": "test-key-32-characters-long-abc123"},
        ):
            encryption = CredentialEncryption()
            assert encryption.master_key == "test-key-32-characters-long-abc123"
            assert encryption.encryption_key is not None
            assert encryption.cipher is not None

    def test_encryption_initialization_missing_key(self):
        """Test encryption fails without master key"""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(InvalidEncryptionKeyError):
                CredentialEncryption()

    def test_encryption_initialization_short_key(self):
        """Test encryption fails with short key"""
        with patch.dict("os.environ", {"CREDENTIAL_MASTER_KEY": "short"}):
            with pytest.raises(InvalidEncryptionKeyError):
                CredentialEncryption()

    def test_encrypt_decrypt_credentials(self):
        """Test basic encryption and decryption"""
        with patch.dict(
            "os.environ",
            {"CREDENTIAL_MASTER_KEY": "test-key-32-characters-long-abc123"},
        ):
            encryption = CredentialEncryption()

            test_credentials = {
                "access_key_id": "MOCK_AWS_ACCESS_KEY",
                "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
                "region": "us-east-1",
            }

            # Encrypt
            encrypted = encryption.encrypt_credentials(test_credentials)
            assert isinstance(encrypted, str)
            assert len(encrypted) > 0

            # Decrypt
            decrypted = encryption.decrypt_credentials(encrypted)
            assert decrypted == test_credentials

    def test_encrypt_empty_credentials(self):
        """Test encryption fails with empty credentials"""
        with patch.dict(
            "os.environ",
            {"CREDENTIAL_MASTER_KEY": "test-key-32-characters-long-abc123"},
        ):
            encryption = CredentialEncryption()

            with pytest.raises(CredentialEncryptionError):
                encryption.encrypt_credentials({})

    def test_encrypt_invalid_type(self):
        """Test encryption fails with invalid type"""
        with patch.dict(
            "os.environ",
            {"CREDENTIAL_MASTER_KEY": "test-key-32-characters-long-abc123"},
        ):
            encryption = CredentialEncryption()

            with pytest.raises(CredentialEncryptionError):
                encryption.encrypt_credentials("not a dict")

    def test_decrypt_invalid_data(self):
        """Test decryption fails with invalid data"""
        with patch.dict(
            "os.environ",
            {"CREDENTIAL_MASTER_KEY": "test-key-32-characters-long-abc123"},
        ):
            encryption = CredentialEncryption()

            with pytest.raises(CredentialDecryptionError):
                encryption.decrypt_credentials("invalid-encrypted-data")

    def test_decrypt_empty_string(self):
        """Test decryption fails with empty string"""
        with patch.dict(
            "os.environ",
            {"CREDENTIAL_MASTER_KEY": "test-key-32-characters-long-abc123"},
        ):
            encryption = CredentialEncryption()

            with pytest.raises(CredentialDecryptionError):
                encryption.decrypt_credentials("")

    def test_credential_integrity_check(self):
        """Test credential integrity checking"""
        with patch.dict(
            "os.environ",
            {"CREDENTIAL_MASTER_KEY": "test-key-32-characters-long-abc123"},
        ):
            encryption = CredentialEncryption()

            test_credentials = {
                "api_token": "test-token-123",
                "domain": "example.okta.com",
            }

            # Encrypt
            encrypted = encryption.encrypt_credentials(test_credentials)

            # Decrypt and verify integrity
            decrypted = encryption.decrypt_credentials(encrypted)
            assert decrypted == test_credentials

    def test_encryption_versioning(self):
        """Test encryption includes versioning metadata"""
        with patch.dict(
            "os.environ",
            {"CREDENTIAL_MASTER_KEY": "test-key-32-characters-long-abc123"},
        ):
            encryption = CredentialEncryption()

            test_credentials = {"key": "value"}
            encrypted = encryption.encrypt_credentials(test_credentials)

            # Decrypt and check that it includes versioning
            decrypted = encryption.decrypt_credentials(encrypted)
            assert decrypted == test_credentials

    def test_key_rotation(self):
        """Test key rotation functionality"""
        with patch.dict(
            "os.environ",
            {"CREDENTIAL_MASTER_KEY": "test-key-32-characters-long-abc123"},
        ):
            encryption1 = CredentialEncryption()

            test_credentials = {"key": "value"}
            encrypted_old = encryption1.encrypt_credentials(test_credentials)

            # Rotate key
            new_key = "new-key-32-characters-long-def456"
            encryption2 = encryption1.rotate_encryption_key(new_key)

            # Old encryption should still work
            decrypted_old = encryption1.decrypt_credentials(encrypted_old)
            assert decrypted_old == test_credentials

            # New encryption should work
            encrypted_new = encryption2.encrypt_credentials(test_credentials)
            decrypted_new = encryption2.decrypt_credentials(encrypted_new)
            assert decrypted_new == test_credentials

    def test_encryption_health_check(self):
        """Test encryption health verification"""
        with patch.dict(
            "os.environ",
            {"CREDENTIAL_MASTER_KEY": "test-key-32-characters-long-abc123"},
        ):
            encryption = CredentialEncryption()

            health = encryption.verify_encryption_health()

            assert health["status"] == "healthy"
            assert "response_time" in health
            assert "encryption_algorithm" in health
            assert "key_derivation" in health
            assert health["encryption_algorithm"] == "AES-256"
            assert health["key_derivation"] == "PBKDF2-SHA256"

class TestConvenienceFunctions:
    """Test convenience functions"""

    def test_encrypt_credentials_function(self):
        """Test encrypt_credentials convenience function"""
        with patch.dict(
            "os.environ",
            {"CREDENTIAL_MASTER_KEY": "test-key-32-characters-long-abc123"},
        ):
            test_credentials = {"key": "value"}
            encrypted = encrypt_credentials(test_credentials)

            assert isinstance(encrypted, str)
            assert len(encrypted) > 0

    def test_decrypt_credentials_function(self):
        """Test decrypt_credentials convenience function"""
        with patch.dict(
            "os.environ",
            {"CREDENTIAL_MASTER_KEY": "test-key-32-characters-long-abc123"},
        ):
            test_credentials = {"key": "value"}

            encrypted = encrypt_credentials(test_credentials)
            decrypted = decrypt_credentials(encrypted)

            assert decrypted == test_credentials

    def test_verify_encryption_health_function(self):
        """Test verify_encryption_health convenience function"""
        with patch.dict(
            "os.environ",
            {"CREDENTIAL_MASTER_KEY": "test-key-32-characters-long-abc123"},
        ):
            health = verify_encryption_health()

            assert health["status"] == "healthy"
            assert "response_time" in health

class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_large_credentials(self):
        """Test encryption with large credential data"""
        with patch.dict(
            "os.environ",
            {"CREDENTIAL_MASTER_KEY": "test-key-32-characters-long-abc123"},
        ):
            encryption = CredentialEncryption()

            # Create large credential data
            large_credentials = {
                "large_field": "x" * 10000,
                "another_field": "y" * 5000,
                "json_field": json.dumps({"nested": {"data": "z" * 1000}}),
            }

            encrypted = encryption.encrypt_credentials(large_credentials)
            decrypted = encryption.decrypt_credentials(encrypted)

            assert decrypted == large_credentials

    def test_unicode_credentials(self):
        """Test encryption with unicode characters"""
        with patch.dict(
            "os.environ",
            {"CREDENTIAL_MASTER_KEY": "test-key-32-characters-long-abc123"},
        ):
            encryption = CredentialEncryption()

            unicode_credentials = {
                "unicode_field": "test-データ-测试-тест-🔐",
                "emoji_field": "🔑🔒🛡️⚡",
                "mixed": "English-日本語-中文-Русский",
            }

            encrypted = encryption.encrypt_credentials(unicode_credentials)
            decrypted = encryption.decrypt_credentials(encrypted)

            assert decrypted == unicode_credentials

    def test_special_characters(self):
        """Test encryption with special characters"""
        with patch.dict(
            "os.environ",
            {"CREDENTIAL_MASTER_KEY": "test-key-32-characters-long-abc123"},
        ):
            encryption = CredentialEncryption()

            special_credentials = {
                "special_chars": "!@#$%^&*()_+-=[]{}|;:,.<>?",
                "quotes": "\"'`",
                "newlines": "line1\nline2\r\nline3",
                "tabs": "field1\tfield2\tfield3",
            }

            encrypted = encryption.encrypt_credentials(special_credentials)
            decrypted = encryption.decrypt_credentials(encrypted)

            assert decrypted == special_credentials

class TestSecurityProperties:
    """Test security properties of the encryption system"""

    def test_different_keys_produce_different_ciphertexts(self):
        """Test that different keys produce different encrypted outputs"""
        test_credentials = {"key": "value"}

        with patch.dict(
            "os.environ", {"CREDENTIAL_MASTER_KEY": "test-key-1-32-characters-long-abc"}
        ):
            encryption1 = CredentialEncryption()
            encrypted1 = encryption1.encrypt_credentials(test_credentials)

        with patch.dict(
            "os.environ", {"CREDENTIAL_MASTER_KEY": "test-key-2-32-characters-long-def"}
        ):
            encryption2 = CredentialEncryption()
            encrypted2 = encryption2.encrypt_credentials(test_credentials)

        # Different keys should produce different ciphertexts
        assert encrypted1 != encrypted2

    def test_same_data_different_ciphertexts(self):
        """Test that same data produces different ciphertexts (due to nonce)"""
        with patch.dict(
            "os.environ",
            {"CREDENTIAL_MASTER_KEY": "test-key-32-characters-long-abc123"},
        ):
            encryption = CredentialEncryption()

            test_credentials = {"key": "value"}

            encrypted1 = encryption.encrypt_credentials(test_credentials)
            encrypted2 = encryption.encrypt_credentials(test_credentials)

            # Same data should produce different ciphertexts (due to Fernet nonce)
            assert encrypted1 != encrypted2

            # But both should decrypt to same data
            decrypted1 = encryption.decrypt_credentials(encrypted1)
            decrypted2 = encryption.decrypt_credentials(encrypted2)

            assert decrypted1 == decrypted2 == test_credentials

    def test_tampered_ciphertext_detection(self):
        """Test that tampered ciphertexts are detected"""
        with patch.dict(
            "os.environ",
            {"CREDENTIAL_MASTER_KEY": "test-key-32-characters-long-abc123"},
        ):
            encryption = CredentialEncryption()

            test_credentials = {"key": "value"}
            encrypted = encryption.encrypt_credentials(test_credentials)

            # Tamper with the encrypted data
            tampered = encrypted[:-10] + "tampered!!"

            # Should fail to decrypt
            with pytest.raises(CredentialDecryptionError):
                encryption.decrypt_credentials(tampered)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
