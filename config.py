"""
Configuration module for loading PostgreSQL credentials from .env or environment variables.
Provides a zero-dependency fallback parser if python-dotenv is not installed yet.
"""

import os
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).parent
ENV_PATH = BASE_DIR / ".env"


def load_env_file(env_file: Path = ENV_PATH) -> None:
    """
    Loads key=value pairs from .env into os.environ.
    Uses python-dotenv if installed, otherwise uses a native fallback parser.
    """
    if not env_file.exists():
        return

    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
    except ImportError:
        # Built-in lightweight fallback parser
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip("'\"")
                if key not in os.environ:
                    os.environ[key] = val


# Load credentials upon import
load_env_file()


def get_db_config() -> Dict[str, Any]:
    """
    Returns connection parameters dictionary for psycopg2.connect(**config).
    """
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "dbname": os.getenv("DB_NAME", "restaurant_db"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
        "sslmode": os.getenv("DB_SSLMODE", "prefer"),
    }


def get_connection_uri() -> str:
    """
    Returns a PostgreSQL connection URI string (e.g. postgresql://user:pass@host:port/dbname).
    """
    cfg = get_db_config()
    password_part = f":{cfg['password']}" if cfg["password"] else ""
    return f"postgresql://{cfg['user']}{password_part}@{cfg['host']}:{cfg['port']}/{cfg['dbname']}?sslmode={cfg['sslmode']}"


def get_gemini_config() -> Dict[str, str]:
    """
    Returns Gemini AI configuration (API key and target model name).
    """
    return {
        "api_key": os.getenv("GEMINI_API_KEY", "").strip(),
        "model": os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip(),
    }

