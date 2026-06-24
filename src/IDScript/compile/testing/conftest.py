"""Test path setup - adds the IDScript package root to sys.path."""

from pathlib import Path
import sys


PACKAGE_DIR = Path(__file__).resolve().parent.parent.parent  # IDScript/src/IDScript/
COMPILE_DIR = Path(__file__).resolve().parent.parent  # compile/

if str(PACKAGE_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_DIR))
