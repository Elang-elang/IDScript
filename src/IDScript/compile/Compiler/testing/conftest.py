"""Test path setup for the official Compiler tests."""

from pathlib import Path
import sys


PACKAGE_DIR = Path(__file__).resolve().parents[3]

if str(PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR))
