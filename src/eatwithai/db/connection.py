"""
PostgreSQL Connection Management Module.
Handles driver imports, connection creation with RealDictCursor,
and friendly error reporting for connection issues.
"""

from typing import Any
from eatwithai.config import get_db_config, get_connection_uri

# Attempt psycopg2 import with helpful error if missing
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    psycopg2 = None
    RealDictCursor = None
    PSYCOPG2_AVAILABLE = False


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
    Returns a psycopg2 connection using credentials loaded from config.
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
