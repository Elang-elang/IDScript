from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal

from .errors import IDSMakerError, ensure_type, reject_positional, validate_options
from .function import IDSMethodBinding, _validate_declare
from .generic import IDSGeneric, normalize_generic_params
from .implement import IDSImplementBinding
from .structure import IDSStructBinding, _annotation_properties, normalize_properties


Declare = Literal["private", "public"]


@dataclass
class IDSClassBinding:
    name: str
    cls: type
    struct: IDSStructBinding
    implement: IDSImplementBinding | None = None
    struct_params: list[IDSGeneric] = field(default_factory=list)
    impl_params: list[IDSGeneric] = field(default_factory=list)

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
    OPTIONS = {"name", "declare", "properties", "extend", "trait", "generic_params", "impl_params"}

    def __new__(
        cls,
        *args: Any,
        **options: Any,
    ) -> Callable[[type], IDSClassBinding]:
        reject_positional("IDSClass", args)
        validate_options("IDSClass", options, cls.OPTIONS)
        name = options.get("name")
        declare = options.get("declare", "public")
        properties = options.get("properties")
        extend = options.get("extend")
        trait = options.get("trait")
        raw_generic_params = options.get("generic_params")
        raw_impl_params = options.get("impl_params")
        struct_params = normalize_generic_params(raw_generic_params, label="IDSClass.generic_params")
        impl_params = normalize_generic_params(raw_impl_params, label="IDSClass.impl_params")
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
                params=struct_params,
            )
            methods = [
                item
                for item in value.__dict__.values()
                if isinstance(item, IDSMethodBinding)
            ]
            if methods:
                implement = IDSImplementBinding(
                    cls=struct, py_cls=value, trait=trait,
                    methods=methods, params=impl_params,
                )
            else:
                implement = None
            return IDSClassBinding(
                name=class_name, cls=value, struct=struct,
                implement=implement,
                struct_params=struct_params, impl_params=impl_params,
            )

        return wrapper
