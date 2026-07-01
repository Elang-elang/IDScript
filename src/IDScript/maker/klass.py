from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Literal

from .errors import IDSMakerError, ensure_type, reject_positional, validate_options
from .function import IDSMethodBinding, _validate_declare
from .implement import IDSImplementBinding
from .structure import IDSStructBinding, _annotation_properties, normalize_properties


Declare = Literal["private", "public"]


@dataclass
class IDSClassBinding:
    name: str
    cls: type
    struct: IDSStructBinding
    implement: IDSImplementBinding | None = None

    def __post_init__(self) -> None:
        self.ids_name = self.name

    @property
    def declare(self) -> str:
        return self.struct.declare

    @property
    def is_priv(self) -> bool:
        return self.struct.is_priv

    @property
    def methods(self) -> list[IDSMethodBinding]:
        if self.implement is None:
            return []
        return self.implement.methods

    def fields(self) -> list[dict[str, Any]]:
        return self.struct.fields()

    def __repr__(self) -> str:
        return f"<IDSClass {self.name!r}>"


class IDSClass:
    OPTIONS = {"name", "declare", "properties", "extend", "trait"}

    def __new__(
        cls,
        *args: Any,
        **options: Any,
    ) -> Callable[[type], IDSClassBinding]:
        reject_positional("IDSClass", args)
        validate_options("IDSClass", options, cls.OPTIONS)
        name = options.get("name")
        declare = options.get("declare", "private")
        properties = options.get("properties")
        extend = options.get("extend")
        trait = options.get("trait")
        if name is not None:
            ensure_type("IDSClass", "name", name, str)
        if properties is not None:
            ensure_type("IDSClass", "properties", properties, dict)
        _validate_declare(declare)

        def wrapper(value: type) -> IDSClassBinding:
            if not isinstance(value, type):
                raise IDSMakerError(f"IDSClass can only decorate classes; got {type(value).__name__}.")
            class_name = name or value.__name__
            annotations = _annotation_properties(getattr(value, "__annotations__", {}))
            if properties is not None:
                annotations.update(normalize_properties("IDSClass", properties))
            struct = IDSStructBinding(
                name=class_name,
                cls=value,
                declare=declare,
                properties=annotations,
                extend=extend,
            )
            methods = [
                item
                for item in value.__dict__.values()
                if isinstance(item, IDSMethodBinding)
            ]
            implement = IDSImplementBinding(cls=struct, py_cls=value, trait=trait, methods=methods) if methods else None
            return IDSClassBinding(name=class_name, cls=value, struct=struct, implement=implement)

        return wrapper
