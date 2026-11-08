"""
PostgreSQL Connection Management Module.
Handles driver imports, connection creation with RealDictCursor,
atomic transaction context management, automatic connection closure,
and friendly error reporting for connection issues.
"""

from contextlib import contextmanager
from typing import Any, Generator
import uuid
from eatwithai.config import get_db_config, get_connection_uri

# Attempt psycopg2 import with helpful error if missing
try:
    import psycopg2
    from psycopg2.extensions import connection as _Psycopg2Connection
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    psycopg2 = None
    _Psycopg2Connection = object  # type: ignore[assignment,misc]
    RealDictCursor = None
    PSYCOPG2_AVAILABLE = False


class ManagedConnection(_Psycopg2Connection):
    """
    PostgreSQL connection subclass that guarantees:
    1. Atomic transaction boundaries (COMMIT on clean exit, ROLLBACK on exception)
       when used in a `with conn:` block.
    2. Automatic connection closure when exiting the outermost `with conn:` block,
       preventing leaked TCP connections.
    3. Nested transaction tracking (`_tx_depth`) so repository functions invoked
       inside a `with conn:` or `with transaction(conn):` block participate in
       the enclosing atomic transaction rather than committing prematurely.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._context_depth: int = 0
        self._tx_depth: int = 0

    def __enter__(self) -> "ManagedConnection":
        self._context_depth += 1
        self._tx_depth += 1
        super().__enter__()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        self._context_depth = max(0, self._context_depth - 1)
        self._tx_depth = max(0, self._tx_depth - 1)
        if self._context_depth == 0:
            try:
                if not self.closed:
                    return bool(super().__exit__(exc_type, exc_val, exc_tb))
                return False
            finally:
                if not self.closed:
                    self.close()
        return False


@contextmanager
def transaction(conn: Any, commit: bool = True) -> Generator[Any, None, None]:
    """
    Context manager for atomic SQL execution on an existing connection without closing it.

    - If this is the outermost transaction scope on `conn` (`_tx_depth == 0`) and `commit=True`:
      commits on clean exit and rolls back the connection on exception.
    - If nested inside an active `with conn:` or `with transaction(conn):` scope (or when
      `commit=False`), uses a PostgreSQL SAVEPOINT so partial failures roll back cleanly to
      the savepoint while deferring the final COMMIT to the outermost transaction owner.
    """
    tx_depth = getattr(conn, "_tx_depth", 0)
    is_outermost = (tx_depth == 0) and commit

    if hasattr(conn, "_tx_depth"):
        conn._tx_depth = tx_depth + 1

    if is_outermost:
        try:
            yield conn
        except Exception:
            if not getattr(conn, "closed", False):
                conn.rollback()
            raise
        else:
            if not getattr(conn, "closed", False):
                conn.commit()
        finally:
            if hasattr(conn, "_tx_depth"):
                conn._tx_depth = max(0, conn._tx_depth - 1)
    else:
        savepoint_name = f"sp_{uuid.uuid4().hex[:12]}"
        with conn.cursor() as cur:
            cur.execute(f"SAVEPOINT {savepoint_name};")
        try:
            yield conn
        except Exception:
            if not getattr(conn, "closed", False):
                with conn.cursor() as cur:
                    cur.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name};")
                    cur.execute(f"RELEASE SAVEPOINT {savepoint_name};")
            raise
        else:
            if not getattr(conn, "closed", False):
                with conn.cursor() as cur:
                    cur.execute(f"RELEASE SAVEPOINT {savepoint_name};")
        finally:
            if hasattr(conn, "_tx_depth"):
                conn._tx_depth = max(0, conn._tx_depth - 1)


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


def get_connection() -> ManagedConnection:
    """
    Returns a ManagedConnection (psycopg2 connection subclass) using credentials loaded from config.
    Uses RealDictCursor by default so column values can be accessed by name, and ensures
    atomic commit/rollback plus automatic connection closure when used as a context manager.
    """
    check_psycopg2_installed()
    config = get_db_config()
    try:
        conn = psycopg2.connect(
            **config,
            connection_factory=ManagedConnection,
            cursor_factory=RealDictCursor,
        )
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
