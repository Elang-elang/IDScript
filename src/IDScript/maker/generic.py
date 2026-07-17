from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Any

from ..compile.ids_ast import GenericParam as _GenericParam
from ..compile.ids_ast.nodes import Name, Type


@dataclass
class IDSGeneric:
    """Deklarasi parameter generik untuk IDSStruct, IDSFunction, IDSMethod,
    IDSImplement, IDSTrait, IDSClass, maupun IDSModule.typedef.

    Contoh::

        IDSGeneric("T")                  # name="T"
        IDSGeneric("T", bound=int)               # name="T", bound=Angka
        IDSGeneric("T", default=str)             # name="T", default=Teks
        IDSGeneric("T", bound=int, default=str)  # keduanya
    """
    name: str
    bound: Any = None
    default: Any = None

    def to_ast_param(self) -> _GenericParam:
        name_node = Name(id=self.name)
        bound_node = self._to_ast_type(self.bound) if self.bound is not None else None
        default_node = self._to_ast_type(self.default) if self.default is not None else None
        return _GenericParam(name=name_node, bound=bound_node, default=default_node)

    @staticmethod
    def _to_ast_type(tp: Any) -> Type:
        from .types import ids_type_name
        if isinstance(tp, tuple):
            type_names = " | ".join(ids_type_name(t) for t in tp)
            raise TypeError(
                f"Multiple bounds ({type_names}) not yet supported by GenericParam AST. "
                "Use a single bound type for now."
            )
        return Type(Name(ids_type_name(tp)))


def normalize_generic_params(
    raw: Any,
    *,
    label: str = "generic_params",
) -> list[IDSGeneric]:
    if raw is None:
        return []
    if isinstance(raw, str):
        warnings.warn(
            f"Use IDSGeneric({raw!r}) instead of plain string for {label}",
            UserWarning, stacklevel=2,
        )
        return [IDSGeneric(raw)]
    if isinstance(raw, list):
        return _normalize_list(raw, label)
    raise TypeError(
        f"{label} must be a str, list of IDSGeneric, or None; "
        f"got {type(raw).__name__}"
    )


def _normalize_list(items: list[Any], label: str) -> list[IDSGeneric]:
    result: list[IDSGeneric] = []
    for item in items:
        if isinstance(item, IDSGeneric):
            result.append(item)
        elif isinstance(item, str):
            warnings.warn(
                f"Use IDSGeneric({item!r}) instead of plain string for {label}",
                UserWarning, stacklevel=3,
            )
            result.append(IDSGeneric(item))
        elif isinstance(item, tuple):
            _warn_tuple(item, label)
            result.append(_tuple_to_generic(item))
        else:
            raise TypeError(
                f"Each entry in {label} must be IDSGeneric, str, or tuple; "
                f"got {type(item).__name__}"
            )
    return result


def _warn_tuple(item: tuple[Any, ...], label: str) -> None:
    name = item[0]
    warnings.warn(
        f"Use IDSGeneric({name!r}, ...) instead of tuple {item!r} for {label}",
        UserWarning, stacklevel=3,
    )


def _tuple_to_generic(item: tuple[Any, ...]) -> IDSGeneric:
    name = item[0]
    if not isinstance(name, str):
        raise TypeError(f"First element of generic tuple must be a str, got {type(name).__name__}")
    rest = item[1:]
    if len(rest) == 0:
        return IDSGeneric(name)
    if len(rest) == 1:
        return IDSGeneric(name, bound=rest[0])
    if len(rest) == 2:
        return IDSGeneric(name, bound=rest[0], default=rest[1])
    raise TypeError(
        f"Generic tuple must have 1-3 elements (name, bound?, default?), "
        f"got {len(item)}: {item!r}"
    )
