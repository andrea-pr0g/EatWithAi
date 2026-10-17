"""
Database management module for the Restaurant Reservation System.
Uses Python's standard sqlite3 library with full Foreign Key enforcement.
"""

import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

DEFAULT_DB_PATH = Path(__file__).parent / "restaurant.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"
SEED_PATH = Path(__file__).parent / "seed_data.sql"


def get_connection(db_path: Path = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """
    Returns a configured sqlite3 connection with Foreign Keys and Row factory enabled.
    """
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def init_db(db_path: Path = DEFAULT_DB_PATH, schema_file: Path = SCHEMA_PATH) -> None:
    """
    Executes schema.sql DDL to create tables, indexes, views, and triggers.
    """
    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with get_connection(db_path) as conn:
        conn.executescript(schema_sql)


def seed_db(db_path: Path = DEFAULT_DB_PATH, seed_file: Path = SEED_PATH) -> None:
    """
    Executes seed_data.sql to populate tables with sample dataset.
    """
    with open(seed_file, "r", encoding="utf-8") as f:
        seed_sql = f.read()

    with get_connection(db_path) as conn:
        conn.executescript(seed_sql)


def get_dining_duration(conn: sqlite3.Connection, party_size: int) -> int:
    """
    Determines the allocated dining duration in minutes based on dining_rules.
    Falls back to 120 minutes if no matching rule is found.
    """
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT duration_minutes 
        FROM dining_rules 
        WHERE ? BETWEEN party_size_from AND party_size_to
        ORDER BY duration_minutes ASC
        LIMIT 1;
        """,
        (party_size,)
    )
    row = cursor.fetchone()
    if row:
        return int(row["duration_minutes"])
    
    # Fallback to max duration rule if party_size exceeds highest range
    cursor.execute("SELECT duration_minutes FROM dining_rules ORDER BY party_size_to DESC LIMIT 1;")
    max_row = cursor.fetchone()
    return int(max_row["duration_minutes"]) if max_row else 120


def create_customer(
    conn: sqlite3.Connection,
    name: str,
    surname: str,
    phone: str,
    email: Optional[str] = None
) -> str:
    """
    Inserts a new customer with an auto-generated UUIDv4 and returns the customer_id.
    """
    customer_id = str(uuid.uuid4())
    conn.execute(
        """
        INSERT INTO customers (customer_id, name, surname, phone, email)
        VALUES (?, ?, ?, ?, ?);
        """,
        (customer_id, name, surname, phone, email)
    )
    conn.commit()
    return customer_id


def create_booking(
    conn: sqlite3.Connection,
    customer_id: str,
    start_time: datetime,
    party_size: int,
    table_ids: List[int],
    source: str = "chatbot",
    status: str = "confirmed",
    special_requests: Optional[str] = None
) -> str:
    """
    Creates a booking, calculates end_time based on dining_rules, and associates tables.
    """
    duration = get_dining_duration(conn, party_size)
    end_time = start_time + timedelta(minutes=duration)
    booking_id = str(uuid.uuid4())

    start_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_str = end_time.strftime("%Y-%m-%d %H:%M:%S")

    with conn:
        conn.execute(
            """
            INSERT INTO bookings (
                booking_id, customer_id, start_time, end_time, 
                party_size, status, source, special_requests
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (booking_id, customer_id, start_str, end_str, party_size, status, source, special_requests)
        )
        
        for tid in table_ids:
            conn.execute(
                """
                INSERT INTO booking_tables (booking_id, table_id)
                VALUES (?, ?);
                """,
                (booking_id, tid)
            )

    return booking_id


def get_available_tables(
    conn: sqlite3.Connection,
    start_time: datetime,
    end_time: datetime,
    area: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Finds active tables that are not occupied during the requested time window.
    """
    start_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
    end_str = end_time.strftime("%Y-%m-%d %H:%M:%S")

    query = """
        SELECT t.table_id, t.name, t.seats_min, t.seats_max, t.area
        FROM tables t
        WHERE t.active = 1
    """
    params: List[Any] = []

    if area:
        query += " AND t.area = ?"
        params.append(area)

    query += """
        AND t.table_id NOT IN (
            SELECT bt.table_id
            FROM booking_tables bt
            JOIN bookings b ON bt.booking_id = b.booking_id
            WHERE b.status NOT IN ('cancelled', 'no_show')
              AND b.start_time < ?
              AND b.end_time > ?
        )
        ORDER BY t.seats_max ASC, t.name ASC;
    """
    params.extend([end_str, start_str])

    cursor = conn.cursor()
    cursor.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]
