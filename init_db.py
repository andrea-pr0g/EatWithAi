#!/usr/bin/env python3
"""
CLI script to initialize and seed the Restaurant database.
Runs schema.sql and seed_data.sql, followed by validation checks.
"""

import os
from datetime import datetime
from pathlib import Path
from database import (
    DEFAULT_DB_PATH,
    get_connection,
    init_db,
    seed_db,
    get_dining_duration,
    get_available_tables,
    create_booking,
)


def main():
    db_file = DEFAULT_DB_PATH
    print(f"==> Target Database: {db_file}")

    # Remove existing db file if present for a clean re-initialization
    if db_file.exists():
        print("  * Removing existing database for fresh start...")
        os.remove(db_file)

    print("  * Initializing database schema (schema.sql)...")
    init_db(db_file)

    print("  * Seeding sample data (seed_data.sql)...")
    seed_db(db_file)

    print("\n" + "=" * 60)
    print(" DATABASE INITIALIZATION & SEEDING COMPLETED SUCCESSFULLY ")
    print("=" * 60)

    # Verification queries
    with get_connection(db_file) as conn:
        cursor = conn.cursor()

        # Count records in all tables
        tables = [
            "customers",
            "tables",
            "table_combinations",
            "opening_shifts",
            "closures",
            "dining_rules",
            "bookings",
            "booking_tables",
        ]
        print("\n--- Record Counts by Table ---")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) AS cnt FROM {table};")
            count = cursor.fetchone()["cnt"]
            print(f"  {table:20s}: {count:3d} records")

        # Display Dining Rules
        print("\n--- Dining Rules (Stay Duration by Party Size) ---")
        cursor.execute("SELECT party_size_from, party_size_to, duration_minutes, description FROM dining_rules;")
        for row in cursor.fetchall():
            print(f"  Party {row['party_size_from']}-{row['party_size_to']:2d} people -> {row['duration_minutes']:3d} min ({row['description']})")

        # Display Tables with Adjacency/Combinations
        print("\n--- Tables & Combinable Adjacencies ---")
        cursor.execute("SELECT table_id, name, seats_min, seats_max, area, combinable_with FROM v_tables_with_combinations;")
        for row in cursor.fetchall():
            print(f"  [{row['area']:12s}] {row['name']} (seats: {row['seats_min']}-{row['seats_max']}) | Combinable with: {row['combinable_with']}")

        # Display Bookings Overview
        print("\n--- Current Bookings Sample ---")
        cursor.execute(
            """
            SELECT booking_id, customer_name, party_size, start_time, end_time, 
                   duration_minutes, status, source, assigned_tables
            FROM v_booking_details
            ORDER BY start_time ASC;
            """
        )
        for row in cursor.fetchall():
            print(
                f"  [{row['status'].upper():9s}] {row['start_time']} -> {row['end_time']} "
                f"({row['duration_minutes']}m) | Party of {row['party_size']} | {row['customer_name']:18s} "
                f"| Tables: {row['assigned_tables'] or 'None'} | Source: {row['source']}"
            )

        # Interactive Python logic verification
        print("\n--- Python Logic Verification ---")
        test_party = 4
        duration = get_dining_duration(conn, test_party)
        print(f"  * Looked up duration rule for party of {test_party}: {duration} minutes")

        test_start = datetime(2026, 10, 19, 19, 30)
        test_end = datetime(2026, 10, 19, 21, 15)
        avail = get_available_tables(conn, test_start, test_end, area="indoor")
        print(f"  * Available indoor tables on {test_start.strftime('%Y-%m-%d %H:%M')}: {[t['name'] for t in avail]}")

    print("\n[SUCCESS] Setup is ready for Python development.\n")


if __name__ == "__main__":
    main()
