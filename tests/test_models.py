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
)


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


if __name__ == "__main__":
    unittest.main()
