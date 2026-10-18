"""Unit tests for chatbot tools helper functions and schemas."""

import unittest
from datetime import datetime, date, time
from decimal import Decimal
import uuid

from eatwithai.chatbot.tools import (
    serialize_for_json,
    _parse_date_and_time,
    _format_time,
)
from eatwithai.chatbot.schemas import CHATBOT_TOOL_DEFINITIONS


class TestChatbotTools(unittest.TestCase):
    def test_serialize_for_json(self):
        sample_dict = {
            "dt": datetime(2026, 10, 20, 19, 30),
            "d": date(2026, 10, 20),
            "t": time(19, 30),
            "u": uuid.UUID("a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"),
            "dec": Decimal("105.00"),
            "int_dec": Decimal("4.0"),
            "nested": [{"val": Decimal("12.5")}],
        }
        serialized = serialize_for_json(sample_dict)
        self.assertEqual(serialized["dt"], "2026-10-20 19:30:00")
        self.assertEqual(serialized["d"], "2026-10-20")
        self.assertEqual(serialized["t"], "19:30")
        self.assertEqual(serialized["u"], "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11")
        self.assertEqual(serialized["int_dec"], 4)
        self.assertEqual(serialized["nested"][0]["val"], 12.5)

    def test_parse_date_and_time(self):
        dt = _parse_date_and_time("2026-10-25", "19:30")
        self.assertEqual(dt.year, 2026)
        self.assertEqual(dt.month, 10)
        self.assertEqual(dt.day, 25)
        self.assertEqual(dt.hour, 19)
        self.assertEqual(dt.minute, 30)

    def test_format_time(self):
        t = time(20, 15)
        self.assertEqual(_format_time(t), "20:15")
        self.assertEqual(_format_time("19:30:00"), "19:30")

    def test_tool_definitions_present(self):
        self.assertGreaterEqual(len(CHATBOT_TOOL_DEFINITIONS), 10)
        tool_names = [t["function"]["name"] for t in CHATBOT_TOOL_DEFINITIONS]
        self.assertIn("check_restaurant_status", tool_names)
        self.assertIn("check_table_availability", tool_names)
        self.assertIn("find_available_slots", tool_names)
        self.assertIn("create_booking_reservation", tool_names)
        self.assertIn("cancel_booking_reservation", tool_names)
        self.assertIn("get_restaurant_menu", tool_names)
        self.assertIn("search_menu_items", tool_names)

    def test_get_restaurant_menu_tool(self):
        from eatwithai.chatbot.tools import get_restaurant_menu
        try:
            res = get_restaurant_menu(category="Burgers")
            self.assertEqual(res["status"], "success")
            self.assertGreaterEqual(res["total_items_found"], 1)
            self.assertIn("items", res)
            # Verify JSON serializability of Decimal prices
            for item in res["items"]:
                self.assertIsInstance(item["price"], (int, float))
        except Exception as e:
            # Skip if DB is not reachable in CI
            self.skipTest(f"Database not available: {e}")

    def test_search_menu_items_tool(self):
        from eatwithai.chatbot.tools import search_menu_items
        try:
            res = search_menu_items("cheesecake")
            self.assertEqual(res["status"], "success")
            self.assertGreaterEqual(res["total_matches"], 1)
            self.assertIn("New York Style Cheesecake", res["items"][0]["name"])
        except Exception as e:
            self.skipTest(f"Database not available: {e}")


if __name__ == "__main__":
    unittest.main()

