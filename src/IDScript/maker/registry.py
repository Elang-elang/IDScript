from __future__ import annotations

import threading
from types import ModuleType
from typing import Any

from .errors import IDSMakerError
from .module_path import resolve_module


NATIVE_REGISTRY: dict[str, Any] = {}
_registry_lock = threading.Lock()


def native_key(value: Any) -> str:
    if isinstance(value, ModuleType):
        return f"{value.__name__}:<module>"
    module = resolve_module(value)
    qualname = getattr(value, "__qualname__", None)
    if not qualname:
        raise IDSMakerError(
            f"Object {value!r} cannot be registered as a native binding. "
            "Expected a Python module, function, class, or importable object with __qualname__."
        )
    return f"{module}:{qualname}"


def register_native(value: Any) -> str:
    key = native_key(value)
    with _registry_lock:
        NATIVE_REGISTRY[key] = value
    return key


def resolve_native(key: str) -> Any:
    with _registry_lock:
        if key not in NATIVE_REGISTRY:
            raise IDSMakerError(f"Native binding {key!r} is not registered.")
        return NATIVE_REGISTRY[key]


def unregister_native(key: str) -> None:
    """Remove a single entry from NATIVE_REGISTRY to avoid stale references."""
    with _registry_lock:
        NATIVE_REGISTRY.pop(key, None)


def clear_registry() -> None:
    """Remove all native bindings. Useful during testing or module reload."""
    with _registry_lock:
        NATIVE_REGISTRY.clear()
