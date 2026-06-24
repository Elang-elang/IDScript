"""Builtin function implementations for the official VM runtime."""

from __future__ import annotations

import sys
from typing import Any, Callable


def _format(text: Any, *args: Any) -> str:
    return str(text).format(*args)


def _print(text: Any, *args: Any) -> None:
    sys.stdout.write(str(text).format(*args))
    return None


def _println(text: Any, *args: Any) -> None:
    sys.stdout.write((str(text) + "\n").format(*args))
    return None


def _eprint(text: Any, *args: Any) -> None:
    sys.stderr.write(str(text).format(*args))
    return None


def _eprintln(text: Any, *args: Any) -> None:
    sys.stderr.write((str(text) + "\n").format(*args))
    return None


def _input(expected_type: type = str) -> Any:
    return expected_type(sys.stdin.readline().strip())


def Global(
    global_scope: Any,
    name: str,
    value: Any,
    private: bool = True,
    /,
)-> None:
    global_scope.globals[name] = value
    if not private:
        global_scope.exports[name] = value

def Lokal(
    current_scope: dict[str, Any],
    name: str,
    value: Any,
    /,
)-> None:
    current_scope[name] = value

BUILTIN_FUNCTIONS: dict[str, Callable[..., Any]] = {
    "format": _format,
    "print": _print,
    "println": _println,
    "eprint": _eprint,
    "eprintln": _eprintln,
    "input": _input,
    "Global": Global,
    "Lokal": Lokal,
    "Galat": Exception,
}
