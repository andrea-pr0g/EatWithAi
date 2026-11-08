"""
Database package for EatWithAi.
Provides connection utilities and data repository functions.
"""

from eatwithai.db.connection import (
    ManagedConnection,
    check_psycopg2_installed,
    get_connection,
    transaction,
)
from eatwithai.db.repository import (
    init_db,
    seed_db,
    update_tables_occupancy,
    get_tables_status,
    get_dining_duration,
    create_customer,
    create_booking,
    create_customer_and_booking,
    get_available_tables,
    get_menu_categories,
    get_menu_items,
    get_menu_item_by_name,
    search_menu,
)

__all__ = [
    "ManagedConnection",
    "check_psycopg2_installed",
    "get_connection",
    "transaction",
    "init_db",
    "seed_db",
    "update_tables_occupancy",
    "get_tables_status",
    "get_dining_duration",
    "create_customer",
    "create_booking",
    "create_customer_and_booking",
    "get_available_tables",
    "get_menu_categories",
    "get_menu_items",
    "get_menu_item_by_name",
    "search_menu",
]

