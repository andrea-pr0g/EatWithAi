#!/usr/bin/env python3
"""
Launcher script for EatWithAi FastAPI backend server.
Runs uvicorn with live reload on port 8000.
"""

import sys
from pathlib import Path

# Add src directory to sys.path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import uvicorn

if __name__ == "__main__":
    print("=" * 65)
    print(" STARTING EATWITHAI ORBITAL WEB SERVER (FastAPI + Uvicorn)")
    print(" Backend API  : http://localhost:8000")
    print(" API Docs     : http://localhost:8000/docs")
    print("=" * 65)
    uvicorn.run("eatwithai.server:app", host="0.0.0.0", port=8000, reload=True)
