"""Unit tests for EatWithAi domain models."""

import unittest
from datetime import datetime
from eatwithai.models import (
    Customer,
    RestaurantTable,
    OpeningShift,
    Closure,
    DiningRule,
    Booking,
    MenuCategory,
    MenuItem,
)
from decimal import Decimal


class TestModels(unittest.TestCase):
    def test_customer_creation(self):
        c = Customer(
            customer_id="uuid-1234",
            name="Mario",
            surname="Rossi",
            phone="+39 333 1234567",
            email="mario@example.com",
        )
        self.assertEqual(c.customer_id, "uuid-1234")
        self.assertEqual(c.name, "Mario")
        self.assertEqual(c.email, "mario@example.com")

    def test_restaurant_table_creation(self):
        t = RestaurantTable(
            table_id=1,
            name="T01",
            seats_min=1,
            seats_max=2,
            area="indoor",
            active=True,
            combinable_with=["T02"],
        )
        self.assertEqual(t.name, "T01")
        self.assertEqual(t.combinable_with, ["T02"])
        self.assertTrue(t.available)

        # Test occupied table
        t_occupied = RestaurantTable(
            table_id=2,
            name="T02",
            seats_min=1,
            seats_max=2,
            area="indoor",
            active=True,
            available=False,
        )
        self.assertFalse(t_occupied.available)

    def test_booking_creation(self):
        now = datetime.now()
        b = Booking(
            booking_id="book-123",
            customer_id="cust-456",
            start_time=now,
            end_time=now,
            party_size=4,
            status="confirmed",
            source="chatbot",
            assigned_tables=["T04"],
        )
        self.assertEqual(b.party_size, 4)
        self.assertEqual(b.status, "confirmed")
        self.assertEqual(b.assigned_tables, ["T04"])

    def test_menu_category_and_item_creation(self):
        cat = MenuCategory(
            category_id=2,
            name="Handcrafted Burgers",
            description="Prime beef burgers",
            display_order=2,
        )
        self.assertEqual(cat.name, "Handcrafted Burgers")
        self.assertEqual(cat.display_order, 2)

        item = MenuItem(
            item_id=7,
            category_id=2,
            category_name="Handcrafted Burgers",
            name="The Classic American Cheeseburger",
            description="Angus beef patty with American cheese on brioche",
            price=Decimal("16.50"),
            calories=890,
            spicy_level=0,
            is_vegetarian=False,
            is_vegan=False,
            is_gluten_free=False,
            allergens="Dairy, Gluten, Eggs",
        )
        self.assertEqual(item.name, "The Classic American Cheeseburger")
        self.assertEqual(item.price, Decimal("16.50"))
        self.assertFalse(item.is_vegetarian)


if __name__ == "__main__":
    unittest.main()

