from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal

from .errors import IDSMakerError, ensure_type, reject_positional, validate_declare, validate_options
from .function import _validate_declare
from .types import ids_type_name


Declare = Literal["private", "public"]


@dataclass
class IDSStructBinding:
    name: str
    cls: type
    declare: str = "private"
    properties: dict[str, tuple[str, Any] | Any] = field(default_factory=dict)
    extend: Any = None

    def __post_init__(self) -> None:
        _validate_declare(self.declare)
        self.ids_name = self.name

    @property
    def is_priv(self) -> bool:
        return self.declare == "private"

    def __repr__(self) -> str:
        return f"<IDSStruct {self.name!r}>"

    def fields(self) -> list[dict[str, Any]]:
        fields: dict[str, tuple[str, Any]] = {}
        if hasattr(self.extend, "fields"):
            for field in self.extend.fields():
                fields[field["name"]] = ("private" if field.get("is_priv") else "public", field["type"])
        fields.update(self.properties)
        return [
            {"name": name, "type": ids_type_name(type_), "is_priv": declare == "private"}
            for name, (declare, type_) in fields.items()
        ]


class IDSStruct:
    OPTIONS = {"name", "declare", "properties", "extend"}

    def __new__(
        cls,
        *args: Any,
        **options: Any,
    ) -> Callable[[type], IDSStructBinding]:
        reject_positional("IDSStruct", args)
        validate_options("IDSStruct", options, cls.OPTIONS)
        name = options.get("name")
        declare = options.get("declare", "private")
        properties = options.get("properties")
        extend = options.get("extend")
        if name is not None:
            ensure_type("IDSStruct", "name", name, str)
        if properties is not None:
            ensure_type("IDSStruct", "properties", properties, dict)
        _validate_declare(declare)

        def wrapper(value: type) -> IDSStructBinding:
            if not isinstance(value, type):
                raise IDSMakerError(f"IDSStruct can only decorate classes; got {type(value).__name__}.")
            struct_name = name or value.__name__
            annotations = _annotation_properties(getattr(value, "__annotations__", {}))
            if properties is not None:
                annotations.update(normalize_properties("IDSStruct", properties))
            if not annotations:
                raise IDSMakerError(
                    f"IDSStruct {struct_name!r} has no properties. "
                    "Define class annotations or pass the 'properties' option."
                )
            return IDSStructBinding(
                name=struct_name,
                cls=value,
                declare=declare,
                properties=annotations,
                extend=extend,
            )

        return wrapper


def _annotation_properties(annotations: dict[str, Any]) -> dict[str, tuple[str, Any]]:
    return {name: ("private", type_) for name, type_ in dict(annotations).items()}


def normalize_properties(wrapper: str, properties: dict[str, Any]) -> dict[str, tuple[str, Any]]:
    normalized: dict[str, tuple[str, Any]] = {}
    for name, value in properties.items():
        if not isinstance(name, str):
            raise IDSMakerError(f"{wrapper} property names must be str; got {type(name).__name__}.")
        if isinstance(value, tuple):
            if len(value) == 1:
                type_ = value[0]
                if _is_declare_text(type_):
                    raise IDSMakerError(
                        f"{wrapper} property {name!r} only declares visibility {type_!r}; "
                        "provide a type, for example ('private', str) or str."
                    )
                normalized[name] = ("private", type_)
                continue
            if len(value) != 2:
                raise IDSMakerError(
                    f"{wrapper} property {name!r} must be <type>, (<type>,), or (<declare>, <type>)."
                )
            declare, type_ = value
            validate_declare(declare)
            normalized[name] = (declare, type_)
            continue
        if _is_declare_text(value):
            raise IDSMakerError(
                f"{wrapper} property {name!r} only declares visibility {value!r}; "
                "provide a type, for example ('private', str) or str."
            )
        declare, type_ = "private", value
        validate_declare(declare)
        normalized[name] = (declare, type_)
    return normalized


def _is_declare_text(value: Any) -> bool:
    return isinstance(value, str) and value in {"private", "public"}
