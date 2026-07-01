from __future__ import annotations

from typing import Any


IDS_PRIMITIVE_TYPES = (str, int, float, bool, type(None), list, dict)


class IDSPyValue:
    """Wrapper for Python values that are not native IDScript values."""

    def __init__(self, value: Any) -> None:
        object.__setattr__(self, "_ids_py_value", value)

    @property
    def isiAsli(self) -> Any:
        return object.__getattribute__(self, "_ids_py_value")

    def __repr__(self) -> str:
        return f"<IDSPyValue<{repr(self.isiAsli)}>>"

    __str__ = __repr__

    def __getattr__(self, name: str) -> Any:
        return wrap_py_value(getattr(self.isiAsli, name))

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(self.isiAsli, name, unwrap_py_value(value))

    def __delattr__(self, name: str) -> None:
        delattr(self.isiAsli, name)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        result = self.isiAsli(*unwrap_py_args(args), **unwrap_py_kwargs(kwargs))
        return wrap_py_value(result)

    def __getitem__(self, key: Any) -> Any:
        return wrap_py_value(self.isiAsli[unwrap_py_value(key)])

    def __setitem__(self, key: Any, value: Any) -> None:
        self.isiAsli[unwrap_py_value(key)] = unwrap_py_value(value)

    def __delitem__(self, key: Any) -> None:
        del self.isiAsli[unwrap_py_value(key)]

    def __iter__(self):
        return iter(self.isiAsli)

    def __len__(self) -> int:
        return len(self.isiAsli)

    def __contains__(self, item: Any) -> bool:
        return unwrap_py_value(item) in self.isiAsli

    def __bool__(self) -> bool:
        return bool(self.isiAsli)

    def __eq__(self, other: Any) -> bool:
        return self.isiAsli == unwrap_py_value(other)

    def __ne__(self, other: Any) -> bool:
        return self.isiAsli != unwrap_py_value(other)

    def __lt__(self, other: Any) -> bool:
        return self.isiAsli < unwrap_py_value(other)

    def __le__(self, other: Any) -> bool:
        return self.isiAsli <= unwrap_py_value(other)

    def __gt__(self, other: Any) -> bool:
        return self.isiAsli > unwrap_py_value(other)

    def __ge__(self, other: Any) -> bool:
        return self.isiAsli >= unwrap_py_value(other)

    def __add__(self, other: Any) -> Any:
        return wrap_py_value(self.isiAsli + unwrap_py_value(other))

    def __radd__(self, other: Any) -> Any:
        return wrap_py_value(unwrap_py_value(other) + self.isiAsli)

    def __sub__(self, other: Any) -> Any:
        return wrap_py_value(self.isiAsli - unwrap_py_value(other))

    def __rsub__(self, other: Any) -> Any:
        return wrap_py_value(unwrap_py_value(other) - self.isiAsli)

    def __mul__(self, other: Any) -> Any:
        return wrap_py_value(self.isiAsli * unwrap_py_value(other))

    def __rmul__(self, other: Any) -> Any:
        return wrap_py_value(unwrap_py_value(other) * self.isiAsli)

    def __truediv__(self, other: Any) -> Any:
        return wrap_py_value(self.isiAsli / unwrap_py_value(other))

    def __rtruediv__(self, other: Any) -> Any:
        return wrap_py_value(unwrap_py_value(other) / self.isiAsli)


def wrap_py_value(value: Any, ids_types: tuple[type, ...] = ()) -> Any:
    if isinstance(value, IDSPyValue):
        return value
    if ids_types and isinstance(value, ids_types):
        return value
    if isinstance(value, IDS_PRIMITIVE_TYPES):
        return value
    return IDSPyValue(value)


def unwrap_py_value(value: Any) -> Any:
    if isinstance(value, IDSPyValue):
        return value.isiAsli
    return value


def unwrap_py_args(args: tuple[Any, ...] | list[Any]) -> list[Any]:
    return [unwrap_py_value(arg) for arg in args]


def unwrap_py_kwargs(kwargs: dict[str, Any]) -> dict[str, Any]:
    return {key: unwrap_py_value(value) for key, value in kwargs.items()}
