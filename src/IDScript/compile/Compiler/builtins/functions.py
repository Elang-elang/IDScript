"""Internal builtin functions for the official VM runtime.

Standard functions/classes live in external builtins under ``IDScript/builtins``
and must be imported explicitly by IDScript code.
"""

from __future__ import annotations

from typing import Any, Callable


BUILTIN_FUNCTIONS: dict[str, Callable[..., Any]] = {}
