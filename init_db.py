#!/usr/bin/env python3
"""
CLI script to initialize and seed the PostgreSQL Restaurant database.
Reads connection credentials from .env and applies schema.sql and seed_data.sql.
"""

import sys
from datetime import datetime
from config import get_db_config, ENV_PATH

try:
    from database import (
        get_connection,
        init_db,
        seed_db,
        get_dining_duration,
        get_available_tables,
        check_psycopg2_installed,
    )
except ImportError as e:
    print(e)
    sys.exit(1)


def main():
    cfg = get_db_config()
    print("=" * 65)
    print(" RESTAURANT DATABASE INITIALIZER (PostgreSQL) ")
    print("=" * 65)
    print(f"Credentials source : {ENV_PATH}")
    print(f"Host               : {cfg['host']}")
    print(f"Port               : {cfg['port']}")
    print(f"Database           : {cfg['dbname']}")
    print(f"User               : {cfg['user']}")
    print(f"SSL Mode           : {cfg['sslmode']}")
    print("-" * 65)

    try:
        check_psycopg2_installed()
    except ImportError as e:
        print(e)
        sys.exit(1)

    print("Connecting to PostgreSQL...")
    try:
        conn = get_connection()
    except Exception as exc:
        print(f"\n[ERROR] Could not connect to PostgreSQL: {exc}")
        print("\nTroubleshooting Checklist:")
        print("1. Ensure PostgreSQL is running on your machine or container.")
        print(f"2. Check that the database '{cfg['dbname']}' exists, or create it with:")
        print(f"       createdb {cfg['dbname']}")
        print(f"   or: psql -U {cfg['user']} -c \"CREATE DATABASE {cfg['dbname']};\"")
        print("3. Verify your host, port, username, and password in .env")
        sys.exit(1)

    with conn:
        print("  * Initializing schema (schema.sql)...")
        init_db()

        print("  * Seeding sample data (seed_data.sql)...")
        seed_db()

        print("\n" + "=" * 65)
        print(" DATABASE INITIALIZATION & SEEDING COMPLETED SUCCESSFULLY ")
        print("=" * 65)

        with conn.cursor() as cur:
            # Table counts
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
                cur.execute(f"SELECT COUNT(*) AS cnt FROM {table};")
                count = cur.fetchone()["cnt"]
                print(f"  {table:20s}: {count:3d} records")

            # Dining rules
            print("\n--- Dining Rules (Stay Duration by Party Size) ---")
            cur.execute("SELECT party_size_from, party_size_to, duration_minutes, description FROM dining_rules ORDER BY party_size_from;")
            for row in cur.fetchall():
                print(f"  Party {row['party_size_from']}-{row['party_size_to']:2d} people -> {row['duration_minutes']:3d} min ({row['description']})")

            # Tables & Combinations
            print("\n--- Tables & Combinable Adjacencies ---")
            cur.execute("SELECT table_id, name, seats_min, seats_max, area, combinable_with FROM v_tables_with_combinations ORDER BY table_id;")
            for row in cur.fetchall():
                print(f"  [{row['area']:12s}] {row['name']} (seats: {row['seats_min']}-{row['seats_max']}) | Combinable with: {row['combinable_with']}")

            # Bookings Overview
            print("\n--- Current Bookings Sample ---")
            cur.execute(
                """
                SELECT booking_id, customer_name, party_size, start_time, end_time, 
                       duration_minutes, status, source, assigned_tables
                FROM v_booking_details
                ORDER BY start_time ASC;
                """
            )
            for row in cur.fetchall():
                print(
                    f"  [{row['status'].upper():9s}] {row['start_time']} -> {row['end_time']} "
                    f"({int(row['duration_minutes'])}m) | Party of {row['party_size']} | {row['customer_name']:18s} "
                    f"| Tables: {row['assigned_tables']} | Source: {row['source']}"
                )

        # Logic test
        print("\n--- Python Logic Verification ---")
        test_party = 4
        duration = get_dining_duration(conn, test_party)
        print(f"  * Looked up duration rule for party of {test_party}: {duration} minutes")

        test_start = datetime(2026, 10, 19, 19, 30)
        test_end = datetime(2026, 10, 19, 21, 15)
        avail = get_available_tables(conn, test_start, test_end, area="indoor")
        print(f"  * Available indoor tables on {test_start.strftime('%Y-%m-%d %H:%M')}: {[t['name'] for t in avail]}")

    print("\n[SUCCESS] PostgreSQL setup is complete and ready for Python development.\n")


if __name__ == "__main__":
    main()
