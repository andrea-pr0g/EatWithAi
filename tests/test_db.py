"""Integration / unit tests for database, repository functions, and transaction atomicity."""

from concurrent.futures import ThreadPoolExecutor
import unittest
from unittest.mock import patch
import uuid
from datetime import datetime, timedelta
from eatwithai.db import (
    create_booking,
    create_customer,
    create_customer_and_booking,
    get_connection,
    get_dining_duration,
    get_available_tables,
    get_menu_categories,
    get_menu_items,
    get_menu_item_by_name,
    search_menu,
    transaction,
)
from eatwithai.chatbot.tools import create_booking_reservation, cancel_booking_reservation


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

    def test_connection_context_manager_closes_connection(self):
        """Verifies that `with get_connection() as conn:` closes the connection on exit."""
        if not self.conn:
            self.skipTest("PostgreSQL not accessible in test environment")

        with get_connection() as temp_conn:
            self.assertFalse(bool(temp_conn.closed))
            with temp_conn.cursor() as cur:
                cur.execute("SELECT 1 AS val;")
                self.assertEqual(cur.fetchone()["val"], 1)
        self.assertTrue(bool(temp_conn.closed), "Connection should be closed upon exiting `with` block")

        # Also verify closure on exception
        err_conn = None
        with self.assertRaises(RuntimeError):
            with get_connection() as err_conn:
                raise RuntimeError("Simulated error inside context manager")
        self.assertIsNotNone(err_conn)
        self.assertTrue(bool(err_conn.closed), "Connection should be closed even when an exception occurs")

    def test_atomic_rollback_across_customer_and_booking(self):
        """
        Verifies that when create_customer and create_booking are grouped inside
        `with transaction(conn):` or `create_customer_and_booking`, a failure in
        create_booking rolls back the customer creation as well.
        """
        if not self.conn:
            self.skipTest("PostgreSQL not accessible in test environment")

        unique_email = f"rollback_{uuid.uuid4().hex[:10]}@example.com"
        unique_phone = f"+1555{uuid.uuid4().int % 10000000:07d}"

        # Attempt to create customer + booking on an inactive table (T99, table_id=16)
        with self.assertRaises(ValueError):
            with transaction(self.conn):
                cust_id = create_customer(
                    self.conn,
                    name="Atomic",
                    surname="Test",
                    phone=unique_phone,
                    email=unique_email,
                )
                create_booking(
                    self.conn,
                    customer_id=cust_id,
                    start_time=datetime(2031, 5, 10, 19, 30),
                    party_size=2,
                    table_ids=[16],  # T99 is inactive
                )

        # Verify customer was rolled back and does not exist in DB
        with self.conn.cursor() as cur:
            cur.execute("SELECT customer_id FROM customers WHERE email = %s;", (unique_email,))
            self.assertIsNone(cur.fetchone(), "Customer record must be rolled back when booking fails")

        # Also test create_customer_and_booking convenience helper rollback
        unique_email_2 = f"rollback2_{uuid.uuid4().hex[:10]}@example.com"
        unique_phone_2 = f"+1555{uuid.uuid4().int % 10000000:07d}"
        with self.assertRaises(ValueError):
            create_customer_and_booking(
                self.conn,
                name="Atomic",
                surname="Helper",
                phone=unique_phone_2,
                email=unique_email_2,
                start_time=datetime(2031, 5, 10, 19, 30),
                party_size=2,
                table_ids=[999999],  # Non-existent table
            )

        with self.conn.cursor() as cur:
            cur.execute("SELECT customer_id FROM customers WHERE email = %s;", (unique_email_2,))
            self.assertIsNone(cur.fetchone(), "Customer record from helper must be rolled back on failure")

    def test_booking_rolls_back_if_occupancy_update_fails(self):
        """
        Verifies that if update_tables_occupancy fails during create_booking_reservation,
        neither the booking nor the new customer is committed.
        """
        if not self.conn:
            self.skipTest("PostgreSQL not accessible in test environment")

        unique_email = f"occ_fail_{uuid.uuid4().hex[:10]}@example.com"
        unique_phone = f"+1555{uuid.uuid4().int % 10000000:07d}"

        with patch("eatwithai.chatbot.tools.update_tables_occupancy", side_effect=RuntimeError("Occupancy DB error")):
            with self.assertRaises(RuntimeError):
                create_booking_reservation(
                    name="Rollback",
                    surname="User",
                    phone=unique_phone,
                    email=unique_email,
                    date_str="2031-06-15",
                    time_str="19:30",
                    party_size=2,
                    area="indoor",
                )

        with get_connection() as check_conn:
            with check_conn.cursor() as cur:
                cur.execute("SELECT customer_id FROM customers WHERE email = %s;", (unique_email,))
                self.assertIsNone(cur.fetchone(), "Customer should not be committed if occupancy update fails")

    def test_overlapping_booking_rejected_and_concurrent_bookings_serialized(self):
        """
        Verifies:
        1. Direct overlapping bookings on the same table are rejected by both create_booking and DB trigger.
        2. Concurrent calls to create_booking_reservation for the same single-table zone slot
           serialize via FOR UPDATE locks and never double-book a table.
        """
        if not self.conn:
            self.skipTest("PostgreSQL not accessible in test environment")

        # Private room has only 1 table (P01, table_id=15, seats 8-16)
        target_date = "2032-08-20"  # Friday
        target_time = "19:30"

        def attempt_booking(idx: int):
            uid = uuid.uuid4().hex[:8]
            phone_digits = f"+1555{uuid.uuid4().int % 10000000:07d}"
            return create_booking_reservation(
                name=f"Concurrent{idx}",
                surname="Guest",
                phone=phone_digits,
                email=f"conc_{idx}_{uid}@example.com",
                date_str=target_date,
                time_str=target_time,
                party_size=10,
                area="private_room",
            )

        created_booking_id = None
        try:
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(attempt_booking, [1, 2]))

            successes = [r for r in results if r["success"]]
            failures = [r for r in results if not r["success"]]

            self.assertEqual(len(successes), 1, "Exactly one concurrent booking should succeed for the single private room")
            self.assertEqual(len(failures), 1, "The second concurrent booking must fail cleanly without double-booking")
            created_booking_id = successes[0]["booking_id"]

            # Also verify that create_booking directly rejects overlapping booking on table 15
            with get_connection() as verify_conn:
                with verify_conn.cursor() as cur:
                    cur.execute("SELECT customer_id, start_time FROM bookings WHERE booking_id = %s;", (created_booking_id,))
                    row = cur.fetchone()
                with self.assertRaises(ValueError):
                    create_booking(
                        verify_conn,
                        customer_id=str(row["customer_id"]),
                        start_time=row["start_time"],
                        party_size=10,
                        table_ids=[15],
                    )
        finally:
            if created_booking_id:
                with get_connection() as cleanup_conn:
                    with cleanup_conn.cursor() as cur:
                        cur.execute("SELECT customer_id FROM bookings WHERE booking_id = %s;", (created_booking_id,))
                        row = cur.fetchone()
                        cur.execute("DELETE FROM booking_tables WHERE booking_id = %s;", (created_booking_id,))
                        cur.execute("DELETE FROM bookings WHERE booking_id = %s;", (created_booking_id,))
                        if row:
                            cur.execute("DELETE FROM customers WHERE customer_id = %s;", (row["customer_id"],))


if __name__ == "__main__":
    unittest.main()

