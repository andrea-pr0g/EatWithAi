"""
Database package for EatWithAi.
Provides connection utilities and data repository functions.
"""

from eatwithai.db.connection import check_psycopg2_installed, get_connection
from eatwithai.db.repository import (
    init_db,
    seed_db,
    get_dining_duration,
    create_customer,
    create_booking,
    get_available_tables,
    get_menu_categories,
    get_menu_items,
    get_menu_item_by_name,
    search_menu,
)

__all__ = [
    "check_psycopg2_installed",
    "get_connection",
    "init_db",
    "seed_db",
    "get_dining_duration",
    "create_customer",
    "create_booking",
    "get_available_tables",
    "get_menu_categories",
    "get_menu_items",
    "get_menu_item_by_name",
    "search_menu",
]

