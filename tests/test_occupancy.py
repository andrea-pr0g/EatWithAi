"""Unit and integration tests for table available column and live occupancy monitoring."""

import unittest
import uuid
from datetime import datetime, timedelta, timezone
from eatwithai.db import (
    get_connection,
    update_tables_occupancy,
    get_tables_status,
    create_customer,
    create_booking,
)
from eatwithai.chatbot.tools import cancel_booking_reservation


class TestTableOccupancy(unittest.TestCase):
    def setUp(self):
        try:
            self.conn = get_connection()
        except Exception:
            self.conn = None

    def tearDown(self):
        if self.conn:
            self.conn.close()

    def test_tables_has_available_column(self):
        """Verifies that the tables table contains the 'available' boolean column."""
        if not self.conn:
            self.skipTest("PostgreSQL not accessible in test environment")
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT column_name, data_type, column_default
                FROM information_schema.columns 
                WHERE table_name = 'tables' AND column_name = 'available';
                """
            )
            col = cur.fetchone()
            self.assertIsNotNone(col, "Column 'available' not found on table 'tables'")
            self.assertEqual(col["data_type"], "boolean")

    def test_update_tables_occupancy_logic(self):
        """Tests that update_tables_occupancy accurately sets available=False for occupied and True for free."""
        if not self.conn:
            self.skipTest("PostgreSQL not accessible in test environment")

        tables = update_tables_occupancy(self.conn)
        self.assertIsInstance(tables, list)
        self.assertGreater(len(tables), 0)

        # Inactive table (e.g. T99) should always have available=False
        t99 = next((t for t in tables if t["name"] == "T99"), None)
        if t99:
            self.assertFalse(t99["active"])
            self.assertFalse(t99["available"])

        # Check that all tables have 'available' key
        for t in tables:
            self.assertIn("available", t)
            self.assertIsInstance(t["available"], bool)

    def test_booking_occupancy_lifecycle(self):
        """
        Creates a temporary customer and booking active RIGHT NOW,
        verifies the table becomes occupied (available=False),
        then cancels the booking and verifies the table becomes free (available=True).
        """
        if not self.conn:
            self.skipTest("PostgreSQL not accessible in test environment")

        # Pick Table T05 (which is free in seed data)
        target_table_name = "T05"
        with self.conn.cursor() as cur:
            cur.execute("SELECT table_id FROM tables WHERE name = %s;", (target_table_name,))
            target_table_id = cur.fetchone()["table_id"]

        # Ensure table is currently free
        update_tables_occupancy(self.conn)
        with self.conn.cursor() as cur:
            cur.execute("SELECT available FROM tables WHERE table_id = %s;", (target_table_id,))
            self.assertTrue(cur.fetchone()["available"], f"Table {target_table_name} should initially be available")

        # 1. Create a customer with unique email
        uid_suffix = uuid.uuid4().hex[:8]
        cust_phone = f"+1 555 {uid_suffix[:4]} {uid_suffix[4:]}"
        cust_email = f"occupancy_{uid_suffix}@space.orbit"
        cust_id = create_customer(
            self.conn,
            name="Neil",
            surname="Armstrong",
            phone=cust_phone,
            email=cust_email,
        )

        # 2. Create a booking that starts 10 minutes ago and ends in 50 minutes (actively ongoing right now)
        now = datetime.now(timezone.utc)
        booking_start = now - timedelta(minutes=10)

        booking_id = create_booking(
            self.conn,
            customer_id=cust_id,
            start_time=booking_start,
            party_size=4,
            table_ids=[target_table_id],
            source="staff",
            status="confirmed",
            special_requests="Test Table Occupancy",
        )

        try:
            # 3. Check table status in DB: Table T05 MUST be occupied (available = False)
            with self.conn.cursor() as cur:
                cur.execute("SELECT available FROM tables WHERE table_id = %s;", (target_table_id,))
                avail = cur.fetchone()["available"]
                self.assertFalse(avail, f"Table {target_table_name} should now be occupied (available=False)")

            # 4. Cancel the booking
            cancel_res = cancel_booking_reservation(booking_id, cust_phone)
            self.assertTrue(cancel_res["success"], "Cancellation should succeed")

            # 5. Check table status in DB: Table T05 MUST be free again (available = True)
            with self.conn.cursor() as cur:
                cur.execute("SELECT available FROM tables WHERE table_id = %s;", (target_table_id,))
                avail_after = cur.fetchone()["available"]
                self.assertTrue(avail_after, f"Table {target_table_name} should now be free (available=True) after cancellation")

        finally:
            # Clean up test records
            with self.conn.cursor() as cur:
                cur.execute("DELETE FROM booking_tables WHERE booking_id = %s;", (booking_id,))
                cur.execute("DELETE FROM bookings WHERE booking_id = %s;", (booking_id,))
                cur.execute("DELETE FROM customers WHERE customer_id = %s;", (cust_id,))
            self.conn.commit()
            update_tables_occupancy(self.conn)


if __name__ == "__main__":
    unittest.main()
