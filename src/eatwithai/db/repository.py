"""
Database Repository Module.
Contains SQL query logic, entity persistence, table availability lookups,
and schema initialization/seeding helpers.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

from eatwithai.config import SCHEMA_PATH, SEED_PATH
from eatwithai.db.connection import get_connection, transaction


def init_db(schema_file: Optional[Path] = None, conn: Any = None) -> None:
    """
    Executes schema.sql DDL to create tables, indexes, views, and triggers
    along with initial table occupancy synchronization in a single atomic transaction.
    """
    target_path = schema_file or SCHEMA_PATH
    with open(target_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    if conn is not None:
        with transaction(conn, commit=True):
            with conn.cursor() as cur:
                cur.execute(schema_sql)
            update_tables_occupancy(conn, commit=False)
    else:
        with get_connection() as managed_conn:
            with managed_conn.cursor() as cur:
                cur.execute(schema_sql)
            update_tables_occupancy(managed_conn, commit=False)


def seed_db(seed_file: Optional[Path] = None, conn: Any = None) -> None:
    """
    Executes seed_data.sql to populate tables with sample dataset
    and updates table occupancy in a single atomic transaction.
    """
    target_path = seed_file or SEED_PATH
    with open(target_path, "r", encoding="utf-8") as f:
        seed_sql = f.read()

    if conn is not None:
        with transaction(conn, commit=True):
            with conn.cursor() as cur:
                cur.execute(seed_sql)
            update_tables_occupancy(conn, commit=False)
    else:
        with get_connection() as managed_conn:
            with managed_conn.cursor() as cur:
                cur.execute(seed_sql)
            update_tables_occupancy(managed_conn, commit=False)


def update_tables_occupancy(
    conn,
    at_time: Optional[datetime] = None,
    commit: bool = True,
) -> List[Dict[str, Any]]:
    """
    Updates the 'available' boolean column for all tables in the database based on occupancy.
    
    A table is marked available = FALSE if:
      - It is inactive (active = FALSE), OR
      - It has an active booking (status NOT IN ('cancelled', 'no_show')) 
        currently ongoing at the specified timestamp (start_time <= at_time AND end_time > at_time).
    Otherwise, available = TRUE.
    
    Args:
        conn: PostgreSQL database connection.
        at_time: Optional reference datetime. Defaults to CURRENT_TIMESTAMP if None.
        commit: Whether to commit if this is the outermost transaction on `conn`.
        
    Returns:
        List of dictionaries with updated table statuses, including occupancy and active booking info.
    """
    with transaction(conn, commit=commit):
        with conn.cursor() as cur:
            if at_time is None:
                cur.execute(
                    """
                    UPDATE tables t
                    SET available = (
                        t.active = TRUE
                        AND NOT EXISTS (
                            SELECT 1
                            FROM booking_tables bt
                            JOIN bookings b ON bt.booking_id = b.booking_id
                            WHERE bt.table_id = t.table_id
                              AND b.status NOT IN ('cancelled', 'no_show')
                              AND b.start_time <= CURRENT_TIMESTAMP
                              AND b.end_time > CURRENT_TIMESTAMP
                        )
                    );
                    """
                )
            else:
                cur.execute(
                    """
                    UPDATE tables t
                    SET available = (
                        t.active = TRUE
                        AND NOT EXISTS (
                            SELECT 1
                            FROM booking_tables bt
                            JOIN bookings b ON bt.booking_id = b.booking_id
                            WHERE bt.table_id = t.table_id
                              AND b.status NOT IN ('cancelled', 'no_show')
                              AND b.start_time <= %s
                              AND b.end_time > %s
                        )
                    );
                    """,
                    (at_time, at_time)
                )
        return get_tables_status(conn, at_time=at_time)


def get_tables_status(
    conn,
    at_time: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves all tables with their current occupancy and availability state,
    along with any active booking details for the occupied tables.
    """
    with conn.cursor() as cur:
        if at_time is None:
            cur.execute(
                """
                SELECT 
                    t.table_id,
                    t.name,
                    t.seats_min,
                    t.seats_max,
                    t.area,
                    t.active,
                    t.available,
                    b.booking_id,
                    b.party_size,
                    b.start_time,
                    b.end_time,
                    b.status AS booking_status,
                    b.source AS booking_source,
                    b.special_requests,
                    c.name || ' ' || c.surname AS customer_name,
                    c.phone AS customer_phone
                FROM tables t
                LEFT JOIN (
                    SELECT bt.table_id, b.booking_id, b.party_size, b.start_time, b.end_time,
                           b.status, b.source, b.special_requests, b.customer_id
                    FROM booking_tables bt
                    JOIN bookings b ON bt.booking_id = b.booking_id
                    WHERE b.status NOT IN ('cancelled', 'no_show')
                      AND b.start_time <= CURRENT_TIMESTAMP
                      AND b.end_time > CURRENT_TIMESTAMP
                ) b ON t.table_id = b.table_id
                LEFT JOIN customers c ON b.customer_id = c.customer_id
                ORDER BY t.table_id ASC;
                """
            )
        else:
            cur.execute(
                """
                SELECT 
                    t.table_id,
                    t.name,
                    t.seats_min,
                    t.seats_max,
                    t.area,
                    t.active,
                    t.available,
                    b.booking_id,
                    b.party_size,
                    b.start_time,
                    b.end_time,
                    b.status AS booking_status,
                    b.source AS booking_source,
                    b.special_requests,
                    c.name || ' ' || c.surname AS customer_name,
                    c.phone AS customer_phone
                FROM tables t
                LEFT JOIN (
                    SELECT bt.table_id, b.booking_id, b.party_size, b.start_time, b.end_time,
                           b.status, b.source, b.special_requests, b.customer_id
                    FROM booking_tables bt
                    JOIN bookings b ON bt.booking_id = b.booking_id
                    WHERE b.status NOT IN ('cancelled', 'no_show')
                      AND b.start_time <= %s
                      AND b.end_time > %s
                ) b ON t.table_id = b.table_id
                LEFT JOIN customers c ON b.customer_id = c.customer_id
                ORDER BY t.table_id ASC;
                """,
                (at_time, at_time)
            )
        return [dict(row) for row in cur.fetchall()]


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
    email: Optional[str] = None,
    commit: bool = True,
) -> str:
    """
    Inserts a new customer record into PostgreSQL and returns the generated UUID customer_id.
    """
    with transaction(conn, commit=commit):
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
        return customer_id


def create_booking(
    conn,
    customer_id: str,
    start_time: datetime,
    party_size: int,
    table_ids: List[int],
    source: str = "chatbot",
    status: str = "confirmed",
    special_requests: Optional[str] = None,
    commit: bool = True,
) -> str:
    """
    Creates a booking in PostgreSQL atomically:
    - Acquires row-level FOR UPDATE locks on requested tables in deterministic order
    - Validates that tables exist, are active, and have no overlapping active bookings
    - Calculates end_time from dining_rules
    - Inserts booking, associates tables in booking_tables, and updates occupancy in a single transaction
    """
    if not table_ids:
        raise ValueError("At least one table_id must be provided to create a booking.")

    with transaction(conn, commit=commit):
        duration = get_dining_duration(conn, party_size)
        end_time = start_time + timedelta(minutes=duration)
        sorted_table_ids = sorted(set(table_ids))

        with conn.cursor() as cur:
            # Lock target table rows in ascending table_id order to prevent race conditions and deadlocks
            cur.execute(
                """
                SELECT table_id, name, active
                FROM tables
                WHERE table_id = ANY(%s)
                ORDER BY table_id ASC
                FOR UPDATE;
                """,
                (sorted_table_ids,)
            )
            locked_tables = cur.fetchall()
            if len(locked_tables) != len(sorted_table_ids):
                raise ValueError("One or more specified tables do not exist.")

            inactive = [t["name"] for t in locked_tables if not t["active"]]
            if inactive:
                raise ValueError(f"Cannot book inactive table(s): {', '.join(inactive)}")

            if status not in ("cancelled", "no_show"):
                cur.execute(
                    """
                    SELECT bt.table_id, t.name, b.booking_id
                    FROM booking_tables bt
                    JOIN bookings b ON bt.booking_id = b.booking_id
                    JOIN tables t ON bt.table_id = t.table_id
                    WHERE bt.table_id = ANY(%s)
                      AND b.status NOT IN ('cancelled', 'no_show')
                      AND b.start_time < %s
                      AND b.end_time > %s
                    LIMIT 1;
                    """,
                    (sorted_table_ids, end_time, start_time)
                )
                conflict = cur.fetchone()
                if conflict:
                    raise ValueError(
                        f"Table {conflict['name']} (ID {conflict['table_id']}) is already booked "
                        f"for the requested time window."
                    )

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

            for tid in sorted_table_ids:
                cur.execute(
                    """
                    INSERT INTO booking_tables (booking_id, table_id)
                    VALUES (%s, %s);
                    """,
                    (booking_id, tid)
                )

        update_tables_occupancy(conn, commit=False)
        return booking_id


def create_customer_and_booking(
    conn,
    name: str,
    surname: str,
    phone: str,
    start_time: datetime,
    party_size: int,
    table_ids: List[int],
    email: Optional[str] = None,
    source: str = "chatbot",
    status: str = "confirmed",
    special_requests: Optional[str] = None,
    commit: bool = True,
) -> Tuple[str, str]:
    """
    Atomically creates (or reuses by matching phone/email) a customer record and creates
    a booking within a single transaction. If booking fails, customer creation is rolled back.
    Returns (customer_id, booking_id).
    """
    with transaction(conn, commit=commit):
        clean_phone = phone.strip()
        clean_email = email.strip() if email else None
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT customer_id FROM customers
                WHERE phone = %s OR (email IS NOT NULL AND email = %s)
                LIMIT 1;
                """,
                (clean_phone, clean_email)
            )
            existing = cur.fetchone()

        if existing:
            customer_id = str(existing["customer_id"])
        else:
            customer_id = create_customer(
                conn,
                name=name.strip(),
                surname=surname.strip(),
                phone=clean_phone,
                email=clean_email,
                commit=False,
            )

        booking_id = create_booking(
            conn,
            customer_id=customer_id,
            start_time=start_time,
            party_size=party_size,
            table_ids=table_ids,
            source=source,
            status=status,
            special_requests=special_requests,
            commit=False,
        )
        return customer_id, booking_id


def get_available_tables(
    conn,
    start_time: datetime,
    end_time: datetime,
    area: Optional[str] = None,
    for_update: bool = False,
) -> List[Dict[str, Any]]:
    """
    Finds active tables that are not occupied during the requested time window.
    When `for_update=True`, acquires row-level FOR UPDATE locks on the candidate tables.
    """
    query = """
        SELECT t.table_id, t.name, t.seats_min, t.seats_max, t.area, t.available
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
        ORDER BY t.seats_max ASC, t.name ASC
    """
    if for_update:
        query += " FOR UPDATE"
    query += ";"
    params.extend([end_time, start_time])

    with conn.cursor() as cur:
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]


def get_menu_categories(conn) -> List[Dict[str, Any]]:
    """
    Retrieves all menu categories ordered by display_order.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT category_id, name, description, display_order, created_at
            FROM menu_categories
            ORDER BY display_order ASC;
            """
        )
        return [dict(row) for row in cur.fetchall()]


def get_menu_items(
    conn,
    category: Optional[str] = None,
    is_vegetarian: Optional[bool] = None,
    is_vegan: Optional[bool] = None,
    is_gluten_free: Optional[bool] = None,
    max_price: Optional[float] = None,
    only_available: bool = True,
) -> List[Dict[str, Any]]:
    """
    Queries menu items with optional category, dietary, and budget filtering.
    """
    query = """
        SELECT 
            item_id, name, category_name, category_id, description,
            price, calories, spicy_level, is_vegetarian, is_vegan,
            is_gluten_free, allergens, is_available, category_order
        FROM v_menu_details
        WHERE 1=1
    """
    params: List[Any] = []

    if only_available:
        query += " AND is_available = TRUE"

    if category:
        query += " AND (LOWER(category_name) LIKE LOWER(%s) OR category_id::TEXT = %s)"
        params.extend([f"%{category}%", category])

    if is_vegetarian is not None:
        query += " AND is_vegetarian = %s"
        params.append(is_vegetarian)

    if is_vegan is not None:
        query += " AND is_vegan = %s"
        params.append(is_vegan)

    if is_gluten_free is not None:
        query += " AND is_gluten_free = %s"
        params.append(is_gluten_free)

    if max_price is not None:
        query += " AND price <= %s"
        params.append(max_price)

    query += " ORDER BY category_order ASC, price ASC;"

    with conn.cursor() as cur:
        cur.execute(query, params)
        return [dict(row) for row in cur.fetchall()]


def get_menu_item_by_name(conn, name: str) -> Optional[Dict[str, Any]]:
    """
    Looks up a single menu item by case-insensitive name match.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT 
                item_id, name, category_name, category_id, description,
                price, calories, spicy_level, is_vegetarian, is_vegan,
                is_gluten_free, allergens, is_available, category_order
            FROM v_menu_details
            WHERE LOWER(name) = LOWER(%s)
            LIMIT 1;
            """,
            (name.strip(),)
        )
        row = cur.fetchone()
        return dict(row) if row else None


def search_menu(conn, search_term: str) -> List[Dict[str, Any]]:
    """
    Full-text / pattern search across menu item names, descriptions, and category names.
    """
    term = f"%{search_term.strip()}%"
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT 
                item_id, name, category_name, category_id, description,
                price, calories, spicy_level, is_vegetarian, is_vegan,
                is_gluten_free, allergens, is_available, category_order
            FROM v_menu_details
            WHERE is_available = TRUE
              AND (
                  name ILIKE %s
                  OR description ILIKE %s
                  OR category_name ILIKE %s
                  OR allergens ILIKE %s
              )
            ORDER BY category_order ASC, price ASC;
            """,
            (term, term, term, term)
        )
        return [dict(row) for row in cur.fetchall()]

