"""Unit tests for EatWithAi configuration."""

import os
import tempfile
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
    load_env_file,
    load_env,
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

    def test_load_env_override_default(self):
        """Verifies that load_env overrides existing environment variables by default."""
        test_key = "EATWITHAI_TEST_OVERRIDE_VAR"
        os.environ[test_key] = "initial_value"

        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write(f"{test_key}=overridden_value\n")
            temp_path = Path(f.name)

        try:
            load_env(temp_path)
            self.assertEqual(os.environ[test_key], "overridden_value")
        finally:
            if temp_path.exists():
                temp_path.unlink()
            os.environ.pop(test_key, None)


if __name__ == "__main__":
    unittest.main()
