"""Builtin type names used by the official VM runtime."""

from __future__ import annotations

from typing import Any


BUILTIN_TYPES = {
    "Teks": str,
    "Angka": int,
    "Float": float,
    "Boolean": bool,
    "Kosong": type(None),
    "Apapun": Any,
    "OBJEK": object,
}


def default_value(type_name: str) -> object:
    if type_name == "Teks":
        return ""
    if type_name == "Angka":
        return 0
    if type_name == "Float":
        return 0.0
    if type_name == "Boolean":
        return False
    return None
