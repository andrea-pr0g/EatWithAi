"""Unit tests for EatWithAi configuration."""

import unittest
from pathlib import Path
from eatwithai.config import (
    PROJECT_ROOT,
    SQL_DIR,
    SCHEMA_PATH,
    SEED_PATH,
    get_db_config,
    get_gemini_config,
    get_connection_uri,
)


class TestConfig(unittest.TestCase):
    def test_canonical_paths_exist(self):
        """Checks that project root, sql dir, and sql files are properly resolved."""
        self.assertTrue(PROJECT_ROOT.exists(), f"PROJECT_ROOT does not exist: {PROJECT_ROOT}")
        self.assertTrue(SQL_DIR.exists(), f"SQL_DIR does not exist: {SQL_DIR}")
        self.assertTrue(SCHEMA_PATH.exists(), f"SCHEMA_PATH does not exist: {SCHEMA_PATH}")
        self.assertTrue(SEED_PATH.exists(), f"SEED_PATH does not exist: {SEED_PATH}")

    def test_db_config_structure(self):
        """Checks that db_config returns all required connection keys."""
        cfg = get_db_config()
        self.assertIn("host", cfg)
        self.assertIn("port", cfg)
        self.assertIn("dbname", cfg)
        self.assertIn("user", cfg)
        self.assertIn("password", cfg)
        self.assertIn("sslmode", cfg)
        self.assertIsInstance(cfg["port"], int)

    def test_gemini_config_structure(self):
        """Checks that gemini_config returns api_key and model keys."""
        cfg = get_gemini_config()
        self.assertIn("api_key", cfg)
        self.assertIn("model", cfg)

    def test_connection_uri(self):
        """Checks that connection URI starts with postgresql:// and includes dbname."""
        uri = get_connection_uri()
        self.assertTrue(uri.startswith("postgresql://"))
        self.assertIn("sslmode=", uri)


if __name__ == "__main__":
    unittest.main()
