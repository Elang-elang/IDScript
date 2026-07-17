from __future__ import annotations

import warnings
from types import NoneType
from typing import Any, get_args, get_origin

from ..compile.ids_ast.nodes import Name, Type


PYTHON_TO_IDS: dict[Any, str] = {
    str: "Teks",
    int: "Angka",
    float: "Float",
    bool: "Boolean",
    None: "Kosong",
    NoneType: "Kosong",
    Any: "Apapun",
    object: "Apapun",
}


class IDSTyped:
    """Penanda bahwa suatu properti/parameter mengacu ke generic param name.

    Contoh:  value: IDSTyped("T")   artinya field ``value`` bertipe ``T``
    (parameter generik yang dideklarasikan lewat `generic_params`/`IDSGeneric`).
    """
    __slots__ = ('_name',)

    def __init__(self, name: str) -> None:
        if not isinstance(name, str):
            raise TypeError(f"IDSTyped name must be a str, got {type(name).__name__}")
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f"IDSTyped({self._name!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, IDSTyped):
            return self._name == other._name
        return NotImplemented

    def __hash__(self) -> int:
        return hash(("IDSTyped", self._name))


def ids_type_name(value: Any) -> str:
    if isinstance(value, IDSTyped):
        return value.name
    if isinstance(value, str):
        warnings.warn(
            f"Use IDSTyped({value!r}) instead of plain string for generic type annotation",
            UserWarning, stacklevel=2,
        )
        return value
    if hasattr(value, "ids_name"):
        return str(value.ids_name)
    if hasattr(value, "name") and not isinstance(value, type):
        return str(value.name)
    if value in PYTHON_TO_IDS:
        return PYTHON_TO_IDS[value]
    if isinstance(value, type):
        return value.__name__
    return str(value)


def ids_type(value: Any) -> Type:
    return Type(Name(ids_type_name(value)))


def type_descriptor(value: Any) -> Any:
    origin = get_origin(value)
    args = get_args(value)
    if origin is list and args:
        return {"kind": "list", "item": type_descriptor(args[0])}
    if origin is dict and len(args) == 2:
        return {"kind": "dict", "key": type_descriptor(args[0]), "value": type_descriptor(args[1])}
    return {"kind": "name", "name": ids_type_name(value)}
