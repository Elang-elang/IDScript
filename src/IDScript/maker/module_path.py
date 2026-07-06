"""Resolve real module path for objects defined in __main__."""

from __future__ import annotations

import inspect
import os
import sys
from pathlib import Path
from typing import Any


def resolve_module(value: Any) -> str:
    """Return the importable module path for *value*, handling ``__main__``.

    When a Python file is run directly (``python path/to/mod.py``) every
    top-level object gets ``__module__ = "__main__"``.  This function
    recovers the real dot-separated module path from the file system.
    """

    module = getattr(value, "__module__", None)
    if module and module != "__main__":
        return module

    try:
        file = inspect.getfile(value)
    except (TypeError, OSError, AttributeError):
        return module or "__main__"

    file_path = Path(file).resolve(strict=False)

    # Strategy 1: walk up from the file's own directory,
    # collecting package dirs (with __init__.py) along the way.
    parts: list[str] = [file_path.parent.name]  # file's own dir is always included
    for parent in file_path.parent.parents:  # grandparent up
        if (parent / "__init__.py").exists():
            parts.append(parent.name)
        else:
            break
    parts.reverse()
    parts.append(file_path.stem)
    return ".".join(parts)

    # Strategy 2: find highest-matching sys.path entry
    for src in sys.path:
        if not src:
            src = os.getcwd()
        src_path = Path(src).resolve(strict=False)
        try:
            rel = file_path.relative_to(src_path)
        except ValueError:
            continue
        result = str(rel.with_suffix(""))
        for suffix in (".py", ".pyc", ".so", ".pyd"):
            if result.endswith(suffix):
                result = result[: -len(suffix)]
                break
        return result.replace("/", ".").replace("\\", ".")

    return file_path.stem
