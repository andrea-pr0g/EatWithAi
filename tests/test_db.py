"""Integration / unit tests for database and repository functions."""

import unittest
from datetime import datetime, timedelta
from eatwithai.db import (
    get_connection,
    get_dining_duration,
    get_available_tables,
)


class TestDatabaseIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.conn = get_connection()
        except Exception as e:
            cls.conn = None

    @classmethod
    def tearDownClass(cls):
        if cls.conn:
            cls.conn.close()

    def test_dining_duration_rules(self):
        if not self.conn:
            self.skipTest("PostgreSQL not accessible in test environment")
        d2 = get_dining_duration(self.conn, 2)
        d4 = get_dining_duration(self.conn, 4)
        d6 = get_dining_duration(self.conn, 6)
        self.assertEqual(d2, 90)
        self.assertEqual(d4, 105)
        self.assertEqual(d6, 120)

    def test_available_tables_query(self):
        if not self.conn:
            self.skipTest("PostgreSQL not accessible in test environment")
        future_start = datetime(2030, 1, 1, 19, 30)
        future_end = future_start + timedelta(minutes=105)
        tables = get_available_tables(self.conn, future_start, future_end, area="indoor")
        self.assertIsInstance(tables, list)
        self.assertGreater(len(tables), 0)
        table_names = [t["name"] for t in tables]
        self.assertIn("T01", table_names)


if __name__ == "__main__":
    unittest.main()
