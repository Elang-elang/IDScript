from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .errors import IDSMakerError, reject_positional, validate_options
from .function import IDSMethodBinding
from .types import ids_type_name


@dataclass
class IDSImplementBinding:
    cls: Any
    py_cls: type
    trait: Any = None
    methods: list[IDSMethodBinding] = field(default_factory=list)

    @property
    def name(self) -> str:
        return ids_type_name(self.cls)

    @property
    def trait_name(self) -> str | None:
        return None if self.trait is None else ids_type_name(self.trait)

    def __repr__(self) -> str:
        return f"<IDSImplement {self.name!r}>"


class IDSImplement:
    OPTIONS = {"cls", "cls_", "trait"}

    def __new__(klass, *args: Any, **options: Any) -> Callable[[type], IDSImplementBinding]:
        reject_positional("IDSImplement", args)
        validate_options("IDSImplement", options, klass.OPTIONS)
        if "cls" in options and "cls_" in options:
            raise IDSMakerError("IDSImplement received both 'cls' and 'cls_'; use only 'cls'.")
        target = options.get("cls", options.get("cls_"))
        trait = options.get("trait")
        if target is None:
            raise IDSMakerError("IDSImplement requires option 'cls'.")

        def wrapper(value: type) -> IDSImplementBinding:
            if not isinstance(value, type):
                raise IDSMakerError(f"IDSImplement can only decorate classes; got {type(value).__name__}.")
            methods = [
                item
                for item in value.__dict__.values()
                if isinstance(item, IDSMethodBinding)
            ]
            return IDSImplementBinding(cls=target, py_cls=value, trait=trait, methods=methods)

        return wrapper
