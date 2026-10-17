"""
Database management module for PostgreSQL using psycopg2.
Credentials are read from .env via config.py.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any

from config import get_db_config, get_connection_uri

# Attempt psycopg2 import with helpful error if missing
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    psycopg2 = None
    RealDictCursor = None
    PSYCOPG2_AVAILABLE = False

BASE_DIR = Path(__file__).parent
SCHEMA_PATH = BASE_DIR / "schema.sql"
SEED_PATH = BASE_DIR / "seed_data.sql"


def check_psycopg2_installed() -> None:
    """Raises an informative ImportError if psycopg2 is not installed."""
    if not PSYCOPG2_AVAILABLE:
        raise ImportError(
            "\n" + "=" * 60 + "\n"
            "psycopg2 is not installed.\n"
            "Please install dependencies with:\n"
            "    pip install -r requirements.txt\n"
            "or:\n"
            "    pip install psycopg2-binary python-dotenv\n"
            + "=" * 60
        )


def get_connection():
    """
    Returns a psycopg2 connection using credentials loaded from .env.
    Uses RealDictCursor by default so column values can be accessed by name.
    """
    check_psycopg2_installed()
    config = get_db_config()
    try:
        conn = psycopg2.connect(**config, cursor_factory=RealDictCursor)
        conn.autocommit = False
        return conn
    except psycopg2.OperationalError as exc:
        raise ConnectionError(
            f"\n" + "=" * 60 + "\n"
            f"Failed to connect to PostgreSQL server at {config['host']}:{config['port']}/{config['dbname']}.\n"
            f"Please check your credentials in: .env\n"
            f"Error details: {exc}\n"
            + "=" * 60
        ) from exc


def init_db(schema_file: Path = SCHEMA_PATH) -> None:
    """
    Executes schema.sql DDL to create tables, indexes, views, and triggers.
    """
    with open(schema_file, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
        conn.commit()


def seed_db(seed_file: Path = SEED_PATH) -> None:
    """
    Executes seed_data.sql to populate tables with sample dataset.
    """
    with open(seed_file, "r", encoding="utf-8") as f:
        seed_sql = f.read()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(seed_sql)
        conn.commit()


def get_dining_duration(conn, party_size: int) -> int:
    """
    Determines allocated dining duration in minutes based on dining_rules.
    Falls back to 120 minutes if no specific rule matches.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT duration_minutes 
            FROM dining_rules 
            WHERE %s BETWEEN party_size_from AND party_size_to
            ORDER BY duration_minutes ASC
            LIMIT 1;
            """,
            (party_size,)
        )
        row = cur.fetchone()
        if row:
            return int(row["duration_minutes"])

        # Fallback to max duration rule if party_size exceeds highest range
        cur.execute("SELECT duration_minutes FROM dining_rules ORDER BY party_size_to DESC LIMIT 1;")
        max_row = cur.fetchone()
        return int(max_row["duration_minutes"]) if max_row else 120


def create_customer(
    conn,
    name: str,
    surname: str,
    phone: str,
    email: Optional[str] = None
) -> str:
    """
    Inserts a new customer record into PostgreSQL and returns the generated UUID customer_id.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO customers (name, surname, phone, email)
            VALUES (%s, %s, %s, %s)
            RETURNING customer_id;
            """,
            (name, surname, phone, email)
        )
        customer_id = str(cur.fetchone()["customer_id"])
    conn.commit()
    return customer_id


def create_booking(
    conn,
    customer_id: str,
    start_time: datetime,
    party_size: int,
    table_ids: List[int],
    source: str = "chatbot",
    status: str = "confirmed",
    special_requests: Optional[str] = None
) -> str:
    """
    Creates a booking in PostgreSQL:
    - Calculates end_time from dining_rules
    - Inserts booking and returns generated UUID
    - Associates tables in booking_tables
    """
    duration = get_dining_duration(conn, party_size)
    end_time = start_time + timedelta(minutes=duration)

    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO bookings (
                customer_id, start_time, end_time, 
                party_size, status, source, special_requests
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING booking_id;
            """,
            (customer_id, start_time, end_time, party_size, status, source, special_requests)
        )
        booking_id = str(cur.fetchone()["booking_id"])

        for tid in table_ids:
            cur.execute(
                """
                INSERT INTO booking_tables (booking_id, table_id)
                VALUES (%s, %s);
                """,
                (booking_id, tid)
            )
    conn.commit()
    return booking_id


def get_available_tables(
    conn,
    start_time: datetime,
    end_time: datetime,
    area: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Finds active tables that are not occupied during the requested time window.
    """
    query = """
        SELECT t.table_id, t.name, t.seats_min, t.seats_max, t.area
        FROM tables t
        WHERE t.active = TRUE
    """
    params: List[Any] = []

    if area:
        query += " AND t.area = %s"
        params.append(area)

    query += """
        AND t.table_id NOT IN (
            SELECT bt.table_id
            FROM booking_tables bt
            JOIN bookings b ON bt.booking_id = b.booking_id
            WHERE b.status NOT IN ('cancelled', 'no_show')
              AND b.start_time < %s
              AND b.end_time > %s
        )
        ORDER BY t.seats_max ASC, t.name ASC;
    """
    params.extend([end_time, start_time])

    with conn.cursor() as cur:
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]
