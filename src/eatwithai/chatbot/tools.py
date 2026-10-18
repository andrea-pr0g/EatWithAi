"""
Chatbot Tools Module for Restaurant Reservations.

This module provides high-level, production-ready tools (functions) designed
to be called by conversational AI chatbots (e.g., OpenAI function calling,
LangChain, Anthropic tools, or custom LLM agents).

Available Tools:
- check_restaurant_status: Check if restaurant is open or closed (closures/shifts) at a given date/time.
- check_table_availability: Check if suitable table(s) are available for a given party size.
- find_available_slots: Find nearby open times on a date if a specific hour is booked.
- get_restaurant_schedule: Retrieve weekly opening hours or hours for a specific date.
- get_dining_duration_for_party: Look up how long a table reservation lasts by party size.
- create_booking_reservation: Full reservation tool that books table(s) and creates customer record.
- cancel_booking_reservation: Cancel an existing booking with customer verification.
- get_booking_info: Look up details of an existing reservation.
"""

from datetime import datetime, timedelta, date, time
from decimal import Decimal
from functools import wraps
from typing import Optional, List, Dict, Any
import uuid

from eatwithai.db import (
    get_connection,
    get_dining_duration,
    get_menu_categories,
    get_menu_items,
    get_menu_item_by_name,
    search_menu,
    update_tables_occupancy,
    get_tables_status,
)
from eatwithai.chatbot.schemas import CHATBOT_TOOL_DEFINITIONS



# ============================================================================
# Helper Functions & JSON Serialization Guardrail
# ============================================================================

def serialize_for_json(obj: Any) -> Any:
    """
    Recursively converts dates, datetimes, times, UUIDs, Decimals, and database records
    into clean JSON-serializable primitives (strings, ints, floats, lists, dicts).
    Prevents 'Object of type date is not JSON serializable' errors in LLM function callers.
    """
    if isinstance(obj, (date, datetime)):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        return obj.isoformat()
    if isinstance(obj, time):
        return obj.strftime("%H:%M")
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    if isinstance(obj, dict):
        return {str(k): serialize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [serialize_for_json(v) for v in obj]
    return obj


def json_safe_tool(func):
    """
    Decorator ensuring that any dictionary or data structure returned by a tool
    function is 100% JSON-serializable by Gemini and other LLM function callers.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        return serialize_for_json(res)
    return wrapper


def _parse_date_and_time(date_str: str, time_str: str) -> datetime:
    """Parses date string ('YYYY-MM-DD') and time string ('HH:MM' or 'HH:MM:SS')."""
    clean_date = date_str.strip().replace("/", "-")
    clean_time = time_str.strip()
    if len(clean_time) == 5:
        clean_time += ":00"
    return datetime.strptime(f"{clean_date} {clean_time}", "%Y-%m-%d %H:%M:%S")


def _format_time(t: Any) -> str:
    """Formats a datetime.time or string to 'HH:MM'."""
    if isinstance(t, time):
        return t.strftime("%H:%M")
    return str(t)[:5]


# ============================================================================
# Tool 1: Check Restaurant Status (Closures & Shifts)
# ============================================================================

@json_safe_tool
def check_restaurant_status(date_str: str, time_str: str) -> Dict[str, Any]:
    """
    Checks if the restaurant is open at a specific date and time.
    Evaluates:
      1. Full-day closures (holidays, renovations).
      2. Specific shift closures (private events).
      3. Regular opening shifts for the weekday.
      4. Shift cutoffs (last bookable time).

    Args:
        date_str: Target date in 'YYYY-MM-DD' format.
        time_str: Target time in 'HH:MM' format (24-hour clock).

    Returns:
        dict: {
            "is_open": bool,
            "date": str,
            "time": str,
            "reason": Optional[str],
            "shift": Optional[dict],
            "message": str
        }
    """
    try:
        dt = _parse_date_and_time(date_str, time_str)
    except ValueError as e:
        return {
            "is_open": False,
            "date": date_str,
            "time": time_str,
            "reason": f"Invalid date or time format: {e}",
            "message": "Please provide a valid date (YYYY-MM-DD) and time (HH:MM)."
        }

    target_date_str = dt.strftime("%Y-%m-%d")
    target_time_str = dt.strftime("%H:%M:%S")
    weekday_idx = dt.weekday()  # 0 = Monday, 6 = Sunday

    with get_connection() as conn:
        with conn.cursor() as cur:
            # 1. Check full-day closures
            cur.execute(
                """
                SELECT reason 
                FROM closures 
                WHERE date = %s AND shift_id IS NULL;
                """,
                (target_date_str,)
            )
            full_closure = cur.fetchone()
            if full_closure:
                return {
                    "is_open": False,
                    "date": target_date_str,
                    "time": time_str,
                    "reason": full_closure["reason"],
                    "shift": None,
                    "message": f"The restaurant is closed all day on {target_date_str} due to: {full_closure['reason']}."
                }

            # 2. Find matching shift for this weekday and time
            cur.execute(
                """
                SELECT shift_id, shift_name, weekday_name, start_time, end_time, last_bookable_time
                FROM opening_shifts
                WHERE weekday = %s
                  AND start_time <= %s
                  AND end_time >= %s;
                """,
                (weekday_idx, target_time_str, target_time_str)
            )
            shift = cur.fetchone()

            if not shift:
                # Query shifts for today to give a helpful message
                cur.execute(
                    """
                    SELECT shift_name, start_time, end_time, last_bookable_time
                    FROM opening_shifts
                    WHERE weekday = %s
                    ORDER BY start_time ASC;
                    """,
                    (weekday_idx,)
                )
                today_shifts = cur.fetchall()
                shift_descriptions = [
                    f"{s['shift_name']} ({_format_time(s['start_time'])}-{_format_time(s['end_time'])})"
                    for s in today_shifts
                ]
                hours_msg = ", ".join(shift_descriptions) if shift_descriptions else "Closed on this day"
                return {
                    "is_open": False,
                    "date": target_date_str,
                    "time": time_str,
                    "reason": "Outside operating hours",
                    "shift": None,
                    "message": f"The restaurant is not serving at {time_str} on {target_date_str}. Operating shifts for this day: {hours_msg}."
                }

            # 3. Check if this specific shift is closed (e.g. private event)
            cur.execute(
                """
                SELECT reason 
                FROM closures 
                WHERE date = %s AND shift_id = %s;
                """,
                (target_date_str, shift["shift_id"])
            )
            shift_closure = cur.fetchone()
            if shift_closure:
                return {
                    "is_open": False,
                    "date": target_date_str,
                    "time": time_str,
                    "reason": shift_closure["reason"],
                    "shift": dict(shift),
                    "message": f"The {shift['shift_name']} shift on {target_date_str} is closed due to: {shift_closure['reason']}."
                }

            # 4. Check last_bookable_time
            last_bookable_str = _format_time(shift["last_bookable_time"])
            if dt.time() > datetime.strptime(last_bookable_str, "%H:%M").time():
                return {
                    "is_open": False,
                    "date": target_date_str,
                    "time": time_str,
                    "reason": "Past last bookable time",
                    "shift": dict(shift),
                    "message": f"The requested time {time_str} is past the last bookable time ({last_bookable_str}) for the {shift['shift_name']} shift."
                }

            return {
                "is_open": True,
                "date": target_date_str,
                "time": time_str,
                "reason": None,
                "shift": {
                    "shift_id": shift["shift_id"],
                    "name": shift["shift_name"],
                    "weekday": shift["weekday_name"],
                    "start_time": _format_time(shift["start_time"]),
                    "end_time": _format_time(shift["end_time"]),
                    "last_bookable_time": last_bookable_str,
                },
                "message": f"The restaurant is open on {target_date_str} at {time_str} ({shift['shift_name']} shift)."
            }


# ============================================================================
# Tool 2: Dining Rules & Stay Duration
# ============================================================================

@json_safe_tool
def get_dining_duration_for_party(party_size: int) -> Dict[str, Any]:
    """
    Returns the allotted stay duration in minutes for a given party size.

    Args:
        party_size: Number of guests.

    Returns:
        dict: {
            "party_size": int,
            "duration_minutes": int,
            "description": str,
            "message": str
        }
    """
    if party_size <= 0:
        return {
            "party_size": party_size,
            "duration_minutes": 0,
            "description": "Invalid",
            "message": "Party size must be at least 1 person."
        }

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT duration_minutes, description 
                FROM dining_rules 
                WHERE %s BETWEEN party_size_from AND party_size_to
                ORDER BY duration_minutes ASC
                LIMIT 1;
                """,
                (party_size,)
            )
            rule = cur.fetchone()
            if not rule:
                cur.execute("SELECT duration_minutes, description FROM dining_rules ORDER BY party_size_to DESC LIMIT 1;")
                rule = cur.fetchone()

        duration = int(rule["duration_minutes"]) if rule else 120
        description = rule["description"] if rule else "Standard dining duration"

        return {
            "party_size": party_size,
            "duration_minutes": duration,
            "description": description,
            "message": f"For a party of {party_size}, the table is reserved for {duration} minutes ({description})."
        }


# ============================================================================
# Tool 3: Check Table Availability
# ============================================================================

@json_safe_tool
def check_table_availability(
    date_str: str,
    time_str: str,
    party_size: int,
    area: Optional[str] = None
) -> Dict[str, Any]:
    """
    Checks if there are available tables (single or joined combinable tables)
    for a given date, time, party size, and optional area.

    Args:
        date_str: Date in 'YYYY-MM-DD' format.
        time_str: Time in 'HH:MM' format.
        party_size: Number of guests.
        area: Optional seating preference ('indoor', 'terrace', 'bar', 'private_room').

    Returns:
        dict: Availability result, duration, and list of candidate tables.
    """
    # 1. First ensure restaurant is operating at this time
    status = check_restaurant_status(date_str, time_str)
    if not status["is_open"]:
        return {
            "is_available": False,
            "date": date_str,
            "time": time_str,
            "party_size": party_size,
            "area": area,
            "duration_minutes": 0,
            "single_tables": [],
            "combinable_options": [],
            "message": f"Cannot book: {status['message']}"
        }

    start_dt = _parse_date_and_time(date_str, time_str)
    with get_connection() as conn:
        duration_mins = get_dining_duration(conn, party_size)
        end_dt = start_dt + timedelta(minutes=duration_mins)

        with conn.cursor() as cur:
            # 2. Find active single tables capable of seating the party
            # where table is NOT currently booked in this time interval
            query_single = """
                SELECT t.table_id, t.name, t.seats_min, t.seats_max, t.area
                FROM tables t
                WHERE t.active = TRUE
                  AND t.seats_max >= %s
                  AND t.table_id NOT IN (
                      SELECT bt.table_id
                      FROM booking_tables bt
                      JOIN bookings b ON bt.booking_id = b.booking_id
                      WHERE b.status NOT IN ('cancelled', 'no_show')
                        AND b.start_time < %s
                        AND b.end_time > %s
                  )
            """
            params: List[Any] = [party_size, end_dt, start_dt]
            if area:
                query_single += " AND t.area = %s"
                params.append(area.lower())

            # Sort by best fit: minimum wasted capacity first
            query_single += " ORDER BY t.seats_max ASC, t.name ASC;"

            cur.execute(query_single, params)
            single_tables = [dict(row) for row in cur.fetchall()]

            # 3. If needed, check adjacent combinable table pairs
            # (e.g. for larger parties or when individual tables are booked)
            combinable_options: List[Dict[str, Any]] = []
            query_combos = """
                SELECT 
                    t1.table_id AS table1_id, t1.name AS table1_name, t1.seats_max AS table1_seats, t1.area AS area,
                    t2.table_id AS table2_id, t2.name AS table2_name, t2.seats_max AS table2_seats,
                    (t1.seats_max + t2.seats_max) AS combined_capacity
                FROM table_combinations tc
                JOIN tables t1 ON tc.table_id = t1.table_id
                JOIN tables t2 ON tc.combinable_with_table_id = t2.table_id
                WHERE t1.active = TRUE AND t2.active = TRUE
                  AND (t1.seats_max + t2.seats_max) >= %s
                  AND t1.table_id < t2.table_id -- avoid duplicate mirrored pairs
                  AND t1.table_id NOT IN (
                      SELECT bt.table_id FROM booking_tables bt
                      JOIN bookings b ON bt.booking_id = b.booking_id
                      WHERE b.status NOT IN ('cancelled', 'no_show')
                        AND b.start_time < %s AND b.end_time > %s
                  )
                  AND t2.table_id NOT IN (
                      SELECT bt.table_id FROM booking_tables bt
                      JOIN bookings b ON bt.booking_id = b.booking_id
                      WHERE b.status NOT IN ('cancelled', 'no_show')
                        AND b.start_time < %s AND b.end_time > %s
                  )
            """
            combo_params: List[Any] = [party_size, end_dt, start_dt, end_dt, start_dt]
            if area:
                query_combos += " AND t1.area = %s"
                combo_params.append(area.lower())

            query_combos += " ORDER BY combined_capacity ASC;"
            cur.execute(query_combos, combo_params)
            combinable_options = [dict(row) for row in cur.fetchall()]

    is_available = len(single_tables) > 0 or len(combinable_options) > 0

    if is_available:
        if single_tables:
            best_table = single_tables[0]
            msg = (
                f"Table available! {best_table['name']} ({best_table['area']}, "
                f"up to {best_table['seats_max']} seats) on {date_str} at {time_str} "
                f"for {duration_mins} minutes."
            )
        else:
            best_combo = combinable_options[0]
            msg = (
                f"Joined tables available! {best_combo['table1_name']} + {best_combo['table2_name']} "
                f"({best_combo['area']}, combined capacity: {best_combo['combined_capacity']} seats) "
                f"on {date_str} at {time_str} for {duration_mins} minutes."
            )
    else:
        msg = f"Sorry, no tables are available for a party of {party_size} on {date_str} at {time_str}."

    return {
        "is_available": is_available,
        "date": date_str,
        "time": time_str,
        "party_size": party_size,
        "area": area,
        "duration_minutes": duration_mins,
        "start_time": start_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": end_dt.strftime("%Y-%m-%d %H:%M:%S"),
        "single_tables": single_tables,
        "combinable_options": combinable_options,
        "message": msg
    }


# ============================================================================
# Tool 4: Find Alternative Time Slots
# ============================================================================

@json_safe_tool
def find_available_slots(
    date_str: str,
    party_size: int,
    preferred_time: Optional[str] = None,
    area: Optional[str] = None,
    interval_minutes: int = 30
) -> Dict[str, Any]:
    """
    Finds available time slots on a given date for a party size.
    Ideal when a customer's preferred time is fully booked or when asking
    'What times are available for dinner on Friday?'.

    Args:
        date_str: Target date in 'YYYY-MM-DD' format.
        party_size: Number of guests.
        preferred_time: Optional preferred time (e.g. '20:00') to center suggestions around.
        area: Optional seating area preference.
        interval_minutes: Spacing between candidate slots (default 30 min).

    Returns:
        dict: List of available time strings and summary message.
    """
    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return {
            "date": date_str,
            "party_size": party_size,
            "available_slots": [],
            "message": "Invalid date format. Use YYYY-MM-DD."
        }

    weekday_idx = target_date.weekday()

    with get_connection() as conn:
        with conn.cursor() as cur:
            # Check full day closure
            cur.execute("SELECT reason FROM closures WHERE date = %s AND shift_id IS NULL;", (date_str,))
            closure = cur.fetchone()
            if closure:
                return {
                    "date": date_str,
                    "party_size": party_size,
                    "available_slots": [],
                    "message": f"Restaurant is closed all day on {date_str} ({closure['reason']})."
                }

            # Fetch active shifts for this day
            cur.execute(
                """
                SELECT shift_id, shift_name, start_time, end_time, last_bookable_time
                FROM opening_shifts
                WHERE weekday = %s
                ORDER BY start_time ASC;
                """,
                (weekday_idx,)
            )
            shifts = cur.fetchall()

    if not shifts:
        return {
            "date": date_str,
            "party_size": party_size,
            "available_slots": [],
            "message": f"No operating shifts scheduled for {date_str}."
        }

    candidate_slots: List[str] = []

    # Generate time slots across active shifts
    for s in shifts:
        shift_id = s["shift_id"]
        # Check if this shift is closed
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT reason FROM closures WHERE date = %s AND shift_id = %s;", (date_str, shift_id))
                if cur.fetchone():
                    continue

        start_t = _format_time(s["start_time"])
        last_t = _format_time(s["last_bookable_time"])

        curr_dt = datetime.strptime(f"{date_str} {start_t}", "%Y-%m-%d %H:%M")
        last_dt = datetime.strptime(f"{date_str} {last_t}", "%Y-%m-%d %H:%M")

        while curr_dt <= last_dt:
            t_str = curr_dt.strftime("%H:%M")
            check = check_table_availability(date_str, t_str, party_size, area=area)
            if check["is_available"]:
                candidate_slots.append(t_str)
            curr_dt += timedelta(minutes=interval_minutes)

    if preferred_time and candidate_slots:
        # Sort candidate slots by proximity to preferred time
        pref_dt = datetime.strptime(f"{date_str} {preferred_time[:5]}", "%Y-%m-%d %H:%M")
        candidate_slots.sort(
            key=lambda t: abs((datetime.strptime(f"{date_str} {t}", "%Y-%m-%d %H:%M") - pref_dt).total_seconds())
        )

    if candidate_slots:
        preview = ", ".join(candidate_slots[:6])
        msg = f"Available slots for a party of {party_size} on {date_str}: {preview}"
    else:
        msg = f"No open slots found for a party of {party_size} on {date_str}."

    return {
        "date": date_str,
        "party_size": party_size,
        "area": area,
        "available_slots": candidate_slots,
        "message": msg
    }


# ============================================================================
# Tool 5: Get Restaurant Schedule
# ============================================================================

@json_safe_tool
def get_restaurant_schedule(date_str: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns operating shifts and scheduled closures.
    If date_str is provided, returns the specific schedule for that date.
    Otherwise, returns the regular weekly schedule and upcoming closures.

    Args:
        date_str: Optional 'YYYY-MM-DD' date string.

    Returns:
        dict: Opening hours and holiday closures.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            if date_str:
                dt = datetime.strptime(date_str, "%Y-%m-%d").date()
                weekday_idx = dt.weekday()

                # Closures for this date
                cur.execute(
                    """
                    SELECT closure_id, shift_id, reason 
                    FROM closures 
                    WHERE date = %s;
                    """,
                    (date_str,)
                )
                closures = [dict(r) for r in cur.fetchall()]

                # Shifts for this weekday
                cur.execute(
                    """
                    SELECT shift_id, shift_name, weekday_name, start_time, end_time, last_bookable_time
                    FROM opening_shifts
                    WHERE weekday = %s
                    ORDER BY start_time ASC;
                    """,
                    (weekday_idx,)
                )
                shifts = [
                    {
                        "shift_name": r["shift_name"],
                        "hours": f"{_format_time(r['start_time'])} - {_format_time(r['end_time'])}",
                        "last_bookable": _format_time(r["last_bookable_time"])
                    }
                    for r in cur.fetchall()
                ]

                is_full_day_closed = any(c["shift_id"] is None for c in closures)

                return {
                    "date": date_str,
                    "weekday": dt.strftime("%A"),
                    "is_closed_all_day": is_full_day_closed,
                    "shifts": [] if is_full_day_closed else shifts,
                    "closures": closures,
                    "message": f"Schedule for {dt.strftime('%A')}, {date_str} retrieved."
                }
            else:
                # Full weekly schedule
                cur.execute(
                    """
                    SELECT weekday_name, shift_name, start_time, end_time, last_bookable_time
                    FROM opening_shifts
                    ORDER BY weekday ASC, start_time ASC;
                    """
                )
                weekly_shifts = [
                    {
                        "day": r["weekday_name"],
                        "shift": r["shift_name"],
                        "hours": f"{_format_time(r['start_time'])} - {_format_time(r['end_time'])}",
                        "last_bookable": _format_time(r["last_bookable_time"])
                    }
                    for r in cur.fetchall()
                ]

                cur.execute("SELECT date, reason FROM closures ORDER BY date ASC;")
                all_closures = [dict(r) for r in cur.fetchall()]

                return {
                    "weekly_schedule": weekly_shifts,
                    "upcoming_closures": all_closures,
                    "message": "Weekly operating schedule and upcoming closures retrieved."
                }


# ============================================================================
# Tool 6: Get Restaurant Areas & Seating Zones
# ============================================================================

@json_safe_tool
def get_restaurant_areas_and_tables() -> Dict[str, Any]:
    """
    Retrieves the available dining zones/areas (indoor, terrace, bar, private room),
    their seat capacities, active table counts, and seating configurations.
    Use this when a customer asks about zones, areas, or seating arrangements.

    Returns:
        dict: List of zones, seat capacities, and summary message.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    area,
                    COUNT(*) AS total_tables,
                    MIN(seats_min) AS min_party,
                    MAX(seats_max) AS max_single_table_capacity,
                    SUM(seats_max) AS total_capacity,
                    STRING_AGG(name, ', ' ORDER BY name) AS table_names
                FROM tables
                WHERE active = TRUE
                GROUP BY area
                ORDER BY area;
                """
            )
            rows = [dict(r) for r in cur.fetchall()]

    descriptions = {
        "indoor": "Main cozy dining room with standard tables and combinable tables for larger groups.",
        "terrace": "Outdoor covered terrace dining with pleasant open-air ambiance.",
        "bar": "Bar seating area with high-top tables, ideal for drinks, appetizers, and solo diners.",
        "private_room": "Dedicated private dining room for events, private parties, and banquets (up to 16 guests)."
    }

    zones = []
    for r in rows:
        area_name = r["area"]
        zones.append({
            "zone": area_name,
            "description": descriptions.get(area_name, "Dining zone"),
            "tables_count": r["total_tables"],
            "capacity_per_table": f"{r['min_party']}-{r['max_single_table_capacity']} seats",
            "total_zone_capacity": r["total_capacity"],
            "tables": r["table_names"]
        })

    return {
        "available_zones": zones,
        "message": (
            "Our restaurant features 4 distinct dining zones: Indoor Dining Room, "
            "Outdoor Terrace, Bar High-Tops, and a Private Dining Room for events."
        )
    }


# ============================================================================
# Tool 7: Create Booking Reservation
# ============================================================================

@json_safe_tool
def create_booking_reservation(
    name: str,
    surname: str,
    phone: str,
    date_str: str,
    time_str: str,
    party_size: int,
    email: Optional[str] = None,
    area: Optional[str] = None,
    special_requests: Optional[str] = None
) -> Dict[str, Any]:
    """
    End-to-end booking tool for the chatbot:
      1. Verifies restaurant is open and table is available.
      2. Finds or creates the customer record.
      3. Allocates the best-fitting table (or joined tables).
      4. Saves the reservation to PostgreSQL.

    Args:
        name: Customer first name.
        surname: Customer last name.
        phone: Customer phone number.
        date_str: Date ('YYYY-MM-DD').
        time_str: Time ('HH:MM').
        party_size: Number of guests.
        email: Optional customer email.
        area: Optional preferred area ('indoor', 'terrace', 'bar', 'private_room').
        special_requests: Optional dietary requests or seating notes.

    Returns:
        dict: Booking confirmation with booking_id, table names, and timings.
    """
    # Check availability
    avail = check_table_availability(date_str, time_str, party_size, area=area)
    if not avail["is_available"]:
        return {
            "success": False,
            "booking_id": None,
            "message": f"Reservation failed: {avail['message']}"
        }

    # Select best table(s)
    table_ids: List[int] = []
    table_names: List[str] = []

    if avail["single_tables"]:
        chosen = avail["single_tables"][0]
        table_ids.append(chosen["table_id"])
        table_names.append(chosen["name"])
    elif avail["combinable_options"]:
        chosen = avail["combinable_options"][0]
        table_ids.extend([chosen["table1_id"], chosen["table2_id"]])
        table_names.extend([chosen["table1_name"], chosen["table2_name"]])
    else:
        return {
            "success": False,
            "booking_id": None,
            "message": "No suitable tables found."
        }

    start_dt = _parse_date_and_time(date_str, time_str)
    duration = avail["duration_minutes"]
    end_dt = start_dt + timedelta(minutes=duration)

    with get_connection() as conn:
        with conn.cursor() as cur:
            # Look up or create customer by phone or email
            cur.execute(
                """
                SELECT customer_id FROM customers 
                WHERE phone = %s OR (email IS NOT NULL AND email = %s)
                LIMIT 1;
                """,
                (phone.strip(), email.strip() if email else None)
            )
            cust = cur.fetchone()

            if cust:
                customer_id = str(cust["customer_id"])
            else:
                customer_id = str(uuid.uuid4())
                cur.execute(
                    """
                    INSERT INTO customers (customer_id, name, surname, phone, email)
                    VALUES (%s, %s, %s, %s, %s);
                    """,
                    (customer_id, name.strip(), surname.strip(), phone.strip(), email.strip() if email else None)
                )

            # Insert booking
            booking_id = str(uuid.uuid4())
            cur.execute(
                """
                INSERT INTO bookings (
                    booking_id, customer_id, start_time, end_time,
                    party_size, status, source, special_requests
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """,
                (
                    booking_id,
                    customer_id,
                    start_dt,
                    end_dt,
                    party_size,
                    "confirmed",
                    "chatbot",
                    special_requests
                )
            )

            # Map booking tables
            for tid in table_ids:
                cur.execute(
                    """
                    INSERT INTO booking_tables (booking_id, table_id)
                    VALUES (%s, %s);
                    """,
                    (booking_id, tid)
                )

        conn.commit()
        update_tables_occupancy(conn)

    tables_str = ", ".join(table_names)
    return {
        "success": True,
        "booking_id": booking_id,
        "customer_name": f"{name} {surname}",
        "party_size": party_size,
        "date": date_str,
        "start_time": time_str,
        "end_time": end_dt.strftime("%H:%M"),
        "duration_minutes": duration,
        "tables": table_names,
        "message": (
            f"Reservation confirmed! Booking reference: {booking_id[:8]}... "
            f"Table: {tables_str} on {date_str} at {time_str} for {party_size} guests "
            f"({duration} minutes stay)."
        )
    }


# ============================================================================
# Tool 8: Cancel Booking Reservation
# ============================================================================

@json_safe_tool
def cancel_booking_reservation(booking_id: str, phone_or_email: str) -> Dict[str, Any]:
    """
    Cancels an existing booking after verifying the customer's phone or email.

    Args:
        booking_id: UUID string of the booking.
        phone_or_email: Customer's phone number or email address for verification.

    Returns:
        dict: Cancellation confirmation status.
    """
    contact = phone_or_email.strip().lower()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT b.booking_id, b.status, c.phone, c.email, b.start_time
                FROM bookings b
                JOIN customers c ON b.customer_id = c.customer_id
                WHERE b.booking_id = %s;
                """,
                (booking_id.strip(),)
            )
            row = cur.fetchone()

            if not row:
                return {
                    "success": False,
                    "message": f"No booking found with reference ID '{booking_id}'."
                }

            if row["status"] == "cancelled":
                return {
                    "success": True,
                    "message": "This booking has already been cancelled."
                }

            # Verification check
            cust_phone = (row["phone"] or "").lower()
            cust_email = (row["email"] or "").lower()
            if contact not in cust_phone and contact != cust_email:
                return {
                    "success": False,
                    "message": "Verification failed: Provided phone or email does not match the reservation records."
                }

            cur.execute(
                """
                UPDATE bookings 
                SET status = 'cancelled' 
                WHERE booking_id = %s;
                """,
                (booking_id.strip(),)
            )
        conn.commit()
        update_tables_occupancy(conn)

    return {
        "success": True,
        "booking_id": booking_id,
        "message": f"Reservation {booking_id[:8]}... for {row['start_time']} has been successfully cancelled."
    }


# ============================================================================
# Tool 9: Get Booking Information
# ============================================================================

@json_safe_tool
def get_booking_info(booking_id: str) -> Dict[str, Any]:
    """
    Looks up details of a booking by ID.

    Args:
        booking_id: UUID string of the reservation.

    Returns:
        dict: Booking details including customer name, status, time, and tables.
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT * FROM v_booking_details
                WHERE booking_id = %s;
                """,
                (booking_id.strip(),)
            )
            row = cur.fetchone()

    if not row:
        return {
            "found": False,
            "message": f"No reservation found with ID '{booking_id}'."
        }

    return {
        "found": True,
        "booking": dict(row),
        "message": f"Reservation details found for {row['customer_name']} on {row['start_time']}."
    }


# ============================================================================
# Tool 10: Get Restaurant Menu
# ============================================================================

@json_safe_tool
def get_restaurant_menu(
    category: Optional[str] = None,
    dietary_preference: Optional[str] = None,
    max_price: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Retrieves the restaurant's authentic American food menu.
    Allows filtering by menu category (e.g. 'Appetizers & Starters', 'Handcrafted Burgers',
    'Sandwiches & Subs', 'Texas & Southern BBQ', 'Steaks & Prime Cuts', 'Classic Sides',
    'Handcrafted Desserts', 'Beverages & Hand-Spun Shakes'), dietary preference
    ('vegetarian', 'vegan', 'gluten-free'), or maximum price.

    Args:
        category: Optional category name or keyword (e.g. 'Burgers', 'Steaks', 'Desserts').
        dietary_preference: Optional dietary filter ('vegetarian', 'vegan', 'gluten-free').
        max_price: Optional maximum price in dollars.

    Returns:
        dict: Available categories, matching items, count, and status message.
    """
    is_veg = True if dietary_preference and "veg" in dietary_preference.lower() and "vegan" not in dietary_preference.lower() else None
    is_vegan = True if dietary_preference and "vegan" in dietary_preference.lower() else None
    is_gf = True if dietary_preference and ("gluten" in dietary_preference.lower() or "gf" in dietary_preference.lower()) else None

    with get_connection() as conn:
        categories = get_menu_categories(conn)
        items = get_menu_items(
            conn,
            category=category,
            is_vegetarian=is_veg,
            is_vegan=is_vegan,
            is_gluten_free=is_gf,
            max_price=max_price,
            only_available=True,
        )

    return {
        "status": "success",
        "category_filter": category or "All Categories",
        "dietary_filter": dietary_preference or "None",
        "total_items_found": len(items),
        "available_categories": [c["name"] for c in categories],
        "items": items,
        "message": f"Retrieved {len(items)} American food menu item(s)."
    }


# ============================================================================
# Tool 11: Search Menu Items
# ============================================================================

@json_safe_tool
def search_menu_items(search_query: str) -> Dict[str, Any]:
    """
    Searches the American food menu by keyword (e.g., 'burger', 'brisket', 'wings',
    'steak', 'shake', 'cheesecake', 'truffle', 'ribs', 'bacon', 'mac & cheese').

    Args:
        search_query: Dish name, ingredient, or keyword to search for.

    Returns:
        dict: Matching dishes with descriptions, prices, dietary information, and allergens.
    """
    if not search_query or not search_query.strip():
        return {
            "status": "error",
            "message": "Please provide a search keyword or dish name.",
            "items": []
        }

    with get_connection() as conn:
        results = search_menu(conn, search_query.strip())

    return {
        "status": "success",
        "search_query": search_query.strip(),
        "total_matches": len(results),
        "items": results,
        "message": f"Found {len(results)} item(s) matching '{search_query.strip()}'."
    }


# ============================================================================
# OpenAI / LLM Function Calling Schema Definitions
# ============================================================================


CHATBOT_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "check_restaurant_status",
            "description": "Checks if the restaurant is open on a specific date and time, evaluating weekly shifts, holiday closures, and shift cutoff times.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_str": {"type": "string", "description": "Date in YYYY-MM-DD format (e.g. '2026-10-20')"},
                    "time_str": {"type": "string", "description": "Time in HH:MM format (24-hour clock, e.g. '19:30')"}
                },
                "required": ["date_str", "time_str"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_table_availability",
            "description": "Checks whether table(s) are available for a given party size on a specific date, time, and optional seating area.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_str": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                    "time_str": {"type": "string", "description": "Time in HH:MM format (24-hour clock)"},
                    "party_size": {"type": "integer", "description": "Number of guests (e.g. 2, 4, 8)"},
                    "area": {
                        "type": "string",
                        "enum": ["indoor", "terrace", "bar", "private_room"],
                        "description": "Optional seating area preference"
                    }
                },
                "required": ["date_str", "time_str", "party_size"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_available_slots",
            "description": "Finds open time slots for a party on a given date if their preferred hour is unavailable or when asked for options.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_str": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                    "party_size": {"type": "integer", "description": "Number of guests"},
                    "preferred_time": {"type": "string", "description": "Optional preferred time (e.g. '20:00')"},
                    "area": {"type": "string", "description": "Optional seating area"}
                },
                "required": ["date_str", "party_size"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_restaurant_schedule",
            "description": "Retrieves the weekly opening hours, shifts, and holiday closures, or the hours for a specific date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date_str": {"type": "string", "description": "Optional specific date in YYYY-MM-DD format"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_booking_reservation",
            "description": "Confirms and books a table reservation for a customer with contact details, party size, and optional requests.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Customer's first name"},
                    "surname": {"type": "string", "description": "Customer's last name"},
                    "phone": {"type": "string", "description": "Customer's contact phone number"},
                    "email": {"type": "string", "description": "Optional customer email address"},
                    "date_str": {"type": "string", "description": "Reservation date in YYYY-MM-DD format"},
                    "time_str": {"type": "string", "description": "Reservation time in HH:MM format (24-hour clock)"},
                    "party_size": {"type": "integer", "description": "Number of guests"},
                    "area": {"type": "string", "enum": ["indoor", "terrace", "bar", "private_room"]},
                    "special_requests": {"type": "string", "description": "Dietary requirements or special notes"}
                },
                "required": ["name", "surname", "phone", "date_str", "time_str", "party_size"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_booking_reservation",
            "description": "Cancels an existing reservation after verifying the customer's phone or email address.",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_id": {"type": "string", "description": "UUID reference ID of the reservation"},
                    "phone_or_email": {"type": "string", "description": "Customer's phone or email for identity verification"}
                },
                "required": ["booking_id", "phone_or_email"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_restaurant_areas_and_tables",
            "description": "Retrieves the available dining zones/areas (indoor, terrace, bar, private room), their seat capacities, active table counts, and seating configurations.",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_booking_info",
            "description": "Retrieves the details and status of an existing reservation by its reference ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_id": {"type": "string", "description": "UUID reference ID of the reservation"}
                },
                "required": ["booking_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_restaurant_menu",
            "description": "Retrieves the restaurant's authentic American food menu, including categories, dish descriptions, prices, spicy levels, and dietary information (vegetarian, vegan, gluten-free).",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Optional category filter (e.g. 'Burgers', 'BBQ', 'Steaks', 'Starters', 'Sides', 'Desserts', 'Beverages')"
                    },
                    "dietary_preference": {
                        "type": "string",
                        "enum": ["vegetarian", "vegan", "gluten-free"],
                        "description": "Optional dietary filter"
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Optional maximum price filter"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_menu_items",
            "description": "Searches American menu items by keyword, dish name, ingredient, or allergen (e.g. 'ribeye', 'wings', 'cheeseburger', 'brisket', 'shake', 'fries').",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_query": {
                        "type": "string",
                        "description": "Dish name, ingredient, or food term to search for"
                    }
                },
                "required": ["search_query"]
            }
        }
    }
]


