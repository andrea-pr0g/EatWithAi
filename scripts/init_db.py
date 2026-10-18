#!/usr/bin/env python3
"""
CLI script to initialize and seed the PostgreSQL Restaurant database.
Reads connection credentials from .env and applies sql/schema.sql and sql/seed_data.sql.
"""

import sys
from pathlib import Path

# Add src to sys.path so eatwithai is importable without requiring manual package installation
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from eatwithai.cli import init_db_main

if __name__ == "__main__":
    init_db_main()
