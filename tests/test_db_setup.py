"""Unit tests for database/db_setup.py module."""

import os
import unittest
from unittest.mock import patch, MagicMock
from database.db_setup import DatabaseConfig


class TestDatabaseConfig(unittest.TestCase):
    """Test cases for DatabaseConfig class."""

    @patch.dict(os.environ, {"DATABASE_URL": "postgresql://user:pass@localhost:5432/testdb"})
    def test_get_database_urls_standard_postgresql(self):
        """Test standard postgresql:// URL processing."""
        original, sync_url, async_url = DatabaseConfig.get_database_urls()
        
        self.assertEqual(original, "postgresql://user:pass@localhost:5432/testdb")
        self.assertIn("postgresql+psycopg2://", sync_url)
        self.assertIn("postgresql+asyncpg://", async_url)

    @patch.dict(os.environ, {"DATABASE_URL": "postgres://user:pass@localhost:5432/testdb"})
    def test_get_database_urls_legacy_postgres_scheme(self):
        """Test that legacy postgres:// scheme is normalized to postgresql://."""
        original, sync_url, async_url = DatabaseConfig.get_database_urls()
        
        # The original URL should be normalized
        self.assertEqual(original, "postgresql://user:pass@localhost:5432/testdb")
        self.assertIn("postgresql+psycopg2://", sync_url)
        self.assertIn("postgresql+asyncpg://", async_url)
        self.assertNotIn("postgres://", original)
        self.assertNotIn("postgres://", sync_url)
        self.assertNotIn("postgres://", async_url)

    @patch.dict(os.environ, {"DATABASE_URL": "postgresql+psycopg2://user:pass@localhost:5432/testdb"})
    def test_get_database_urls_with_psycopg2(self):
        """Test URL with psycopg2 driver already specified."""
        original, sync_url, async_url = DatabaseConfig.get_database_urls()
        
        self.assertEqual(original, "postgresql+psycopg2://user:pass@localhost:5432/testdb")
        self.assertEqual(sync_url, "postgresql+psycopg2://user:pass@localhost:5432/testdb")
        self.assertIn("postgresql+asyncpg://", async_url)

    @patch.dict(os.environ, {"DATABASE_URL": "postgresql+asyncpg://user:pass@localhost:5432/testdb"})
    def test_get_database_urls_with_asyncpg(self):
        """Test URL with asyncpg driver already specified."""
        original, sync_url, async_url = DatabaseConfig.get_database_urls()
        
        self.assertEqual(original, "postgresql+asyncpg://user:pass@localhost:5432/testdb")
        self.assertIn("postgresql+psycopg2://", sync_url)
        self.assertEqual(async_url, "postgresql+asyncpg://user:pass@localhost:5432/testdb")

    @patch.dict(os.environ, {"DATABASE_URL": "postgres://user:pass@localhost:5432/testdb?sslmode=require"})
    def test_get_database_urls_legacy_postgres_with_ssl(self):
        """Test legacy postgres:// scheme with SSL parameters."""
        original, sync_url, async_url = DatabaseConfig.get_database_urls()
        
        # The original URL should be normalized
        self.assertTrue(original.startswith("postgresql://"))
        self.assertNotIn("postgres://", original)
        self.assertIn("postgresql+psycopg2://", sync_url)
        self.assertIn("postgresql+asyncpg://", async_url)
        # SSL mode should be removed from async URL
        self.assertNotIn("sslmode=require", async_url)
        self.assertIn("sslmode=require", sync_url)

    @patch.dict(os.environ, {}, clear=True)
    def test_get_database_urls_missing_env_var(self):
        """Test that missing DATABASE_URL raises an error."""
        with self.assertRaises(OSError) as exc_info:
            DatabaseConfig.get_database_urls()
        # Check for either error message format
        error_msg = str(exc_info.exception)
        self.assertTrue(
            "DATABASE_URL environment variable not set" in error_msg or
            "Missing required environment variables: DATABASE_URL" in error_msg,
            f"Expected DATABASE_URL error message, got: {error_msg}"
        )

    @patch.dict(os.environ, {"DATABASE_URL": "postgres://user@localhost/testdb"})
    def test_get_database_urls_legacy_postgres_without_password(self):
        """Test legacy postgres:// scheme without password."""
        original, sync_url, async_url = DatabaseConfig.get_database_urls()
        
        self.assertEqual(original, "postgresql://user@localhost/testdb")
        self.assertNotIn("postgres://", original)
        self.assertIn("postgresql+psycopg2://", sync_url)
        self.assertIn("postgresql+asyncpg://", async_url)

    @patch("database.db_setup.logger")
    @patch.dict(os.environ, {"DATABASE_URL": "postgres://user:pass@localhost:5432/testdb"})
    def test_get_database_urls_logs_normalization(self, mock_logger):
        """Test that normalization of postgres:// scheme is logged."""
        DatabaseConfig.get_database_urls()
        
        # Check that the normalization was logged
        mock_logger.info.assert_any_call("Normalized legacy postgres:// scheme to postgresql://")


if __name__ == "__main__":
    unittest.main()