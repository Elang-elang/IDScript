from __future__ import annotations

from types import ModuleType
from typing import Any

from .errors import IDSMakerError


NATIVE_REGISTRY: dict[str, Any] = {}


def native_key(value: Any) -> str:
    if isinstance(value, ModuleType):
        return f"{value.__name__}:<module>"
    module = getattr(value, "__module__", None)
    qualname = getattr(value, "__qualname__", None)
    if not module or not qualname:
        raise IDSMakerError(
            f"Object {value!r} cannot be registered as a native binding. "
            "Expected a Python module, function, class, or importable object with __module__ and __qualname__."
        )
    return f"{module}:{qualname}"


def register_native(value: Any) -> str:
    key = native_key(value)
    NATIVE_REGISTRY[key] = value
    return key


def resolve_native(key: str) -> Any:
    if key not in NATIVE_REGISTRY:
        raise IDSMakerError(f"Native binding {key!r} is not registered.")
    return NATIVE_REGISTRY[key]
