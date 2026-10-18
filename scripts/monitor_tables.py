#!/usr/bin/env python3
"""
EatWithAi - Real-Time Table Occupancy Monitor Daemon.

Continuously checks table occupancy against active PostgreSQL bookings.
If a table has an active reservation ongoing right now, its 'available'
column in the database is set to FALSE.
If a table is free (and active), its 'available' column is set to TRUE.

Usage:
    python3 scripts/monitor_tables.py              # Run continuous daemon (every 5s)
    python3 scripts/monitor_tables.py --interval 10 # Poll every 10 seconds
    python3 scripts/monitor_tables.py --once        # Run single check and exit
    python3 scripts/monitor_tables.py --at "2026-10-18 20:30" # Check specific timestamp
"""

import sys
import time
import signal
import argparse
from datetime import datetime, timezone
from pathlib import Path

# Ensure src is on sys.path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from eatwithai.db import get_connection, update_tables_occupancy, get_tables_status

# Terminal color constants
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
GRAY = "\033[90m"


def format_table_display(tables, target_time: datetime, iteration: int = 1):
    """Prints a styled terminal table showing current occupancy status."""
    time_str = target_time.strftime("%Y-%m-%d %H:%M:%S")
    
    occupied_count = sum(1 for t in tables if not t["available"] and t["active"])
    available_count = sum(1 for t in tables if t["available"])
    inactive_count = sum(1 for t in tables if not t["active"])

    print("\n" + "=" * 96)
    print(f"{BOLD}{CYAN} EATWITHAI ORBITAL PLATFORM - REAL-TIME TABLE OCCUPANCY MONITOR{RESET}")
    print(f" Reference Time: {time_str} | Cycle #{iteration} | DB Sync Status: {GREEN}SYNCHRONIZED{RESET}")
    print("=" * 96)
    print(f"{BOLD}{'TABLE':<8} {'ZONE':<14} {'SEATS':<8} {'AVAILABLE':<12} {'STATE':<12} {'ACTIVE BOOKING DETAILS'}{RESET}")
    print("-" * 96)

    for t in tables:
        name = t["name"]
        area = t["area"]
        seats = f"{t['seats_min']}-{t['seats_max']}"
        is_avail = t["available"]
        is_active = t["active"]

        if not is_active:
            avail_str = f"{GRAY}False{RESET}"
            state_str = f"{GRAY}[MAINTENANCE]{RESET}"
            details = f"{GRAY}Table inactive / disabled for service{RESET}"
        elif not is_avail:
            avail_str = f"{RED}False{RESET}"
            state_str = f"{RED}[OCCUPIED]{RESET}"
            # Extract booking details
            b_id = (t.get("booking_id") or "")[:8]
            cust = t.get("customer_name") or "Unknown"
            start_str = t["start_time"].strftime("%H:%M") if t.get("start_time") else "?"
            end_str = t["end_time"].strftime("%H:%M") if t.get("end_time") else "?"
            party = t.get("party_size") or "?"
            
            # Remaining time
            if t.get("end_time"):
                end_dt = t["end_time"]
                # Convert target_time to comparable
                if end_dt.tzinfo and not target_time.tzinfo:
                    target_cmp = target_time.replace(tzinfo=end_dt.tzinfo)
                else:
                    target_cmp = target_time
                rem_mins = max(0, int((end_dt - target_cmp).total_seconds() // 60))
                time_info = f"{rem_mins}m remaining (until {end_str})"
            else:
                time_info = f"ends {end_str}"

            details = f"Guest: {BOLD}{cust}{RESET} ({party}p) | Ref: #{b_id} | {time_info}"
        else:
            avail_str = f"{GREEN}True{RESET}"
            state_str = f"{GREEN}[FREE]{RESET}"
            details = f"{GREEN}Available for seating{RESET}"

        print(f" {name:<7} {area:<14} {seats:<8} {avail_str:<21} {state_str:<21} {details}")

    print("-" * 96)
    print(f" Summary: {RED}{occupied_count} Occupied (available=False){RESET} | "
          f"{GREEN}{available_count} Free (available=True){RESET} | "
          f"{GRAY}{inactive_count} Inactive{RESET} | Total: {len(tables)} tables")
    print("=" * 96)


def monitor_loop(interval: int = 5, once: bool = False, at_time_str: str = None):
    """Main execution loop for checking table occupancy."""
    specific_time = None
    if at_time_str:
        specific_time = datetime.strptime(at_time_str, "%Y-%m-%d %H:%M")

    iteration = 0
    running = True

    def sig_handler(sig, frame):
        nonlocal running
        print(f"\n{YELLOW}Stopping Table Occupancy Monitor...{RESET}")
        running = False

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    print(f"{BOLD}Initializing Table Occupancy Checker (Interval: {interval}s)...{RESET}")

    while running:
        iteration += 1
        ref_time = specific_time or datetime.now()

        try:
            with get_connection() as conn:
                tables = update_tables_occupancy(conn, at_time=specific_time)
            
            format_table_display(tables, target_time=ref_time, iteration=iteration)
        except Exception as exc:
            print(f"{RED}[ERROR] Failed to query/update table occupancy: {exc}{RESET}")

        if once or specific_time:
            break

        # Sleep interval in small chunks for responsive CTRL+C
        for _ in range(int(interval * 10)):
            if not running:
                break
            time.sleep(0.1)

    print("Table Occupancy Monitor stopped gracefully.")


def main():
    parser = argparse.ArgumentParser(
        description="EatWithAi - Continuous Table Occupancy Checker Daemon",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=5,
        help="Polling interval in seconds (default: 5)"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once to sync and print table occupancy, then exit"
    )
    parser.add_argument(
        "--at",
        type=str,
        default=None,
        help="Check occupancy at a specific date and time (format: 'YYYY-MM-DD HH:MM')"
    )
    args = parser.parse_args()

    monitor_loop(interval=args.interval, once=args.once, at_time_str=args.at)


if __name__ == "__main__":
    main()
