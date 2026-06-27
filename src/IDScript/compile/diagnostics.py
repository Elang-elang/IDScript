"""Compatibility re-export for IDScript diagnostics and exceptions."""

try:
    from IDScript.exceptions import *
except ImportError:
    import sys
    from pathlib import Path

    src_dir = Path(__file__).resolve().parents[2]
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    from IDScript.exceptions import *
