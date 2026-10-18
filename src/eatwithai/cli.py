"""
Unified Command-Line Interface for EatWithAi.
Provides entry points for database initialization and launching the chatbot.
"""

import sys
import argparse
from datetime import datetime

from eatwithai.config import get_db_config, get_gemini_config, ENV_PATH
from eatwithai.db import (
    get_connection,
    init_db,
    seed_db,
    get_dining_duration,
    get_available_tables,
    check_psycopg2_installed,
)


def init_db_main():
    """Initializes and seeds the PostgreSQL database."""
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
        print("  * Initializing schema (sql/schema.sql)...")
        init_db()

        print("  * Seeding sample data (sql/seed_data.sql)...")
        seed_db()

        print("\n" + "=" * 65)
        print(" DATABASE INITIALIZATION & SEEDING COMPLETED SUCCESSFULLY ")
        print("=" * 65)

        with conn.cursor() as cur:
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

            print("\n--- Dining Rules (Stay Duration by Party Size) ---")
            cur.execute("SELECT party_size_from, party_size_to, duration_minutes, description FROM dining_rules ORDER BY party_size_from;")
            for row in cur.fetchall():
                print(f"  Party {row['party_size_from']}-{row['party_size_to']:2d} people -> {row['duration_minutes']:3d} min ({row['description']})")

            print("\n--- Tables & Combinable Adjacencies ---")
            cur.execute("SELECT table_id, name, seats_min, seats_max, area, combinable_with FROM v_tables_with_combinations ORDER BY table_id;")
            for row in cur.fetchall():
                print(f"  [{row['area']:12s}] {row['name']} (seats: {row['seats_min']}-{row['seats_max']}) | Combinable with: {row['combinable_with']}")

        print("\n--- Python Logic Verification ---")
        test_party = 4
        duration = get_dining_duration(conn, test_party)
        print(f"  * Looked up duration rule for party of {test_party}: {duration} minutes")

        test_start = datetime.now().replace(hour=19, minute=30, second=0, microsecond=0)
        test_end = test_start.replace(hour=21, minute=15)
        avail = get_available_tables(conn, test_start, test_end, area="indoor")
        print(f"  * Available indoor tables on {test_start.strftime('%Y-%m-%d %H:%M')}: {[t['name'] for t in avail]}")

    print("\n[SUCCESS] PostgreSQL setup is complete and ready for Python development.\n")


def status_main():
    """Checks and prints system configuration and connectivity status."""
    db_cfg = get_db_config()
    gemini_cfg = get_gemini_config()
    print("=" * 65)
    print(" EATWITHAI SYSTEM STATUS ")
    print("=" * 65)
    print(f"Config path        : {ENV_PATH}")
    print(f"PostgreSQL target  : {db_cfg['user']}@{db_cfg['host']}:{db_cfg['port']}/{db_cfg['dbname']}")
    print(f"Gemini Model       : {gemini_cfg['model']}")
    print(f"Gemini Key set     : {'Yes' if gemini_cfg['api_key'] else 'No'}")
    print("-" * 65)

    print("Checking database connection...")
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS total FROM bookings;")
            bookings_count = cur.fetchone()["total"]
        conn.close()
        print(f"[OK] PostgreSQL is reachable. Total bookings recorded: {bookings_count}")
    except Exception as err:
        print(f"[WARN] Database connection failed: {err}")

    print("=" * 65)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="EatWithAi - AI Restaurant Reservation Platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # init-db command
    subparsers.add_parser("init-db", help="Initialize and seed PostgreSQL database")

    # chat command
    subparsers.add_parser("chat", help="Start interactive AI reservation chatbot")

    # status command
    subparsers.add_parser("status", help="Show system configuration and connection status")

    args = parser.parse_args()

    if args.command == "init-db":
        init_db_main()
    elif args.command == "chat":
        from eatwithai.chatbot.agent import run_cli
        run_cli()
    elif args.command == "status":
        status_main()
    else:
        # Default to printing help or running chat if no command
        parser.print_help()


if __name__ == "__main__":
    main()
