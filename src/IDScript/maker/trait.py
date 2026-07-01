from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal

from .errors import IDSMakerError, ensure_type, reject_positional, validate_options
from .function import IDSMethodBinding, _validate_declare


Declare = Literal["private", "public"]


@dataclass
class IDSTraitBinding:
    name: str
    cls: type
    declare: str = "private"
    methods: list[IDSMethodBinding] = field(default_factory=list)

    def __post_init__(self) -> None:
        _validate_declare(self.declare)
        self.ids_name = self.name

    @property
    def is_priv(self) -> bool:
        return self.declare == "private"

    def descriptor(self) -> dict[str, object]:
        return {
            "kind": "trait",
            "name": self.name,
            "methods": [method.abstract_descriptor() for method in self.methods],
        }

    def __repr__(self) -> str:
        return f"<IDSTrait {self.name!r}>"


class IDSTrait:
    OPTIONS = {"name", "declare"}

    def __new__(
        cls,
        *args: Any,
        **options: Any,
    ) -> Callable[[type], IDSTraitBinding]:
        reject_positional("IDSTrait", args)
        validate_options("IDSTrait", options, cls.OPTIONS)
        name = options.get("name")
        declare = options.get("declare", "private")
        if name is not None:
            ensure_type("IDSTrait", "name", name, str)
        _validate_declare(declare)

        def wrapper(value: type) -> IDSTraitBinding:
            if not isinstance(value, type):
                raise IDSMakerError(f"IDSTrait can only decorate classes; got {type(value).__name__}.")
            methods = [
                item
                for item in value.__dict__.values()
                if isinstance(item, IDSMethodBinding)
            ]
            return IDSTraitBinding(name=name or value.__name__, cls=value, declare=declare, methods=methods)

        return wrapper
