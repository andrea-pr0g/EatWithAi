"""Integration / unit tests for database and repository functions."""

import unittest
from datetime import datetime, timedelta
from eatwithai.db import (
    get_connection,
    get_dining_duration,
    get_available_tables,
    get_menu_categories,
    get_menu_items,
    get_menu_item_by_name,
    search_menu,
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

    def test_get_menu_categories(self):
        if not self.conn:
            self.skipTest("PostgreSQL not accessible in test environment")
        categories = get_menu_categories(self.conn)
        self.assertGreaterEqual(len(categories), 8)
        names = [c["name"] for c in categories]
        self.assertIn("Handcrafted Burgers", names)
        self.assertIn("Steaks & Prime Cuts", names)
        self.assertIn("Texas & Southern BBQ", names)

    def test_get_menu_items_filtering(self):
        if not self.conn:
            self.skipTest("PostgreSQL not accessible in test environment")
        # Filter by category
        burgers = get_menu_items(self.conn, category="Burgers")
        self.assertGreaterEqual(len(burgers), 3)
        burger_names = [b["name"] for b in burgers]
        self.assertTrue(any("Cheeseburger" in name for name in burger_names))

        # Filter by dietary preference
        veg_items = get_menu_items(self.conn, is_vegetarian=True)
        self.assertGreater(len(veg_items), 0)
        for item in veg_items:
            self.assertTrue(item["is_vegetarian"])

    def test_search_menu(self):
        if not self.conn:
            self.skipTest("PostgreSQL not accessible in test environment")
        results = search_menu(self.conn, "brisket")
        self.assertGreaterEqual(len(results), 1)
        self.assertIn("Texas Oak-Smoked Beef Brisket", results[0]["name"])

    def test_get_menu_item_by_name(self):
        if not self.conn:
            self.skipTest("PostgreSQL not accessible in test environment")
        item = get_menu_item_by_name(self.conn, "Buffalo Chicken Wings")
        self.assertIsNotNone(item)
        self.assertEqual(item["spicy_level"], 2)
        self.assertTrue(item["is_gluten_free"])


if __name__ == "__main__":
    unittest.main()

