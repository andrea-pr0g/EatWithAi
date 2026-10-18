#!/usr/bin/env python3
"""
CLI script to launch the interactive Gemini Restaurant Chatbot.
Reads connection credentials and GEMINI_API_KEY from .env.
"""

import sys
from pathlib import Path

# Add src to sys.path so eatwithai is importable without requiring manual package installation
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from eatwithai.chatbot.agent import run_cli

if __name__ == "__main__":
    run_cli()
