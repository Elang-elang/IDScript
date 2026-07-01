from __future__ import annotations

from dataclasses import dataclass, field
import inspect
from typing import Any, Callable, Literal

from ..compile.Compiler.bytecode import FunctionCode
from .errors import IDSMakerError, ensure_type, reject_positional, validate_declare, validate_options
from .pyvalue import wrap_py_value
from .registry import register_native
from .types import ids_type_name


Declare = Literal["private", "public"]


def _validate_declare(value: str) -> None:
    validate_declare(value)


@dataclass
class IDSFunctionBinding:
    name: str
    func: Callable[..., Any]
    declare: str = "private"
    arguments: dict[str, Any] = field(default_factory=dict)
    annotation: Any = Any
    is_method: bool = False
    native_name: str = ""
    native_symbol: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_declare(self.declare)
        self.ids_name = self.name
        self.native_name = self.native_name or f"__py_native__.{self.name}"
        key = register_native(self.func)
        self.native_symbol = {
            "kind": "function",
            "module": self.func.__module__,
            "qualname": self.func.__qualname__,
            "registry_key": key,
        }

    @property
    def is_priv(self) -> bool:
        return self.declare == "private"

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return wrap_py_value(self.func(*args, **kwargs))

    def __repr__(self) -> str:
        return f"<IDSFunction {self.name!r}>"

    def to_function_code(self, name: str | None = None, native_name: str | None = None) -> FunctionCode:
        call_name = native_name or self.native_name
        args = list(self.arguments)
        code = [["LOAD_NAME", call_name]]
        code.extend(["LOAD_NAME", arg] for arg in args)
        code.append(["CALL_FUNCTION", len(args)])
        code.append(["RETURN_VALUE"])
        return FunctionCode(name=name or self.name, args=args, code=code)

    def abstract_descriptor(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "arguments": {name: ids_type_name(type_) for name, type_ in self.arguments.items()},
            "annotation": ids_type_name(self.annotation),
            "is_priv": self.is_priv,
        }


class IDSFunction:
    OPTIONS = {"name", "declare", "arguments", "annotation"}

    def __new__(
        cls,
        *args: Any,
        **options: Any,
    ) -> Callable[[Callable[..., Any]], IDSFunctionBinding]:
        reject_positional("IDSFunction", args)
        validate_options("IDSFunction", options, cls.OPTIONS)
        name = options.get("name")
        declare = options.get("declare", "private")
        arguments = options.get("arguments")
        annotation = options.get("annotation", Any)
        if name is not None:
            ensure_type("IDSFunction", "name", name, str)
        if arguments is not None:
            ensure_type("IDSFunction", "arguments", arguments, dict)
        _validate_declare(declare)

        def wrapper(func: Callable[..., Any]) -> IDSFunctionBinding:
            if not callable(func):
                raise IDSMakerError(f"IDSFunction can only decorate callables; got {type(func).__name__}.")
            func_name = name or func.__name__
            normalized_args, normalized_annotation = _normalize_signature("IDSFunction", func, arguments, annotation)
            return IDSFunctionBinding(
                name=func_name,
                func=func,
                declare=declare,
                arguments=normalized_args,
                annotation=normalized_annotation,
            )

        return wrapper


@dataclass
class IDSMethodBinding(IDSFunctionBinding):
    static: bool = False

    def __post_init__(self) -> None:
        super().__post_init__()
        self.is_method = True

    def __repr__(self) -> str:
        return f"<IDSMethod {self.name!r}>"

    def abstract_descriptor(self) -> dict[str, Any]:
        descriptor = super().abstract_descriptor()
        descriptor["static"] = self.static
        return descriptor


class IDSMethod:
    OPTIONS = IDSFunction.OPTIONS | {"static"}

    def __new__(
        cls,
        *args: Any,
        **options: Any,
    ) -> Callable[[Callable[..., Any]], IDSMethodBinding]:
        reject_positional("IDSMethod", args)
        validate_options("IDSMethod", options, cls.OPTIONS)
        name = options.get("name")
        declare = options.get("declare", "private")
        arguments = options.get("arguments")
        annotation = options.get("annotation", Any)
        static = options.get("static", False)
        if name is not None:
            ensure_type("IDSMethod", "name", name, str)
        if arguments is not None:
            ensure_type("IDSMethod", "arguments", arguments, dict)
        ensure_type("IDSMethod", "static", static, bool)
        _validate_declare(declare)

        def wrapper(func: Callable[..., Any]) -> IDSMethodBinding:
            if not callable(func):
                raise IDSMakerError(f"IDSMethod can only decorate callables; got {type(func).__name__}.")
            func_name = name or func.__name__
            normalized_args, normalized_annotation = _normalize_signature("IDSMethod", func, arguments, annotation)
            return IDSMethodBinding(
                name=func_name,
                func=func,
                declare=declare,
                arguments=normalized_args,
                annotation=normalized_annotation,
                static=static,
            )

        return wrapper


def _normalize_signature(
    wrapper: str,
    func: Callable[..., Any],
    arguments: dict[str, Any] | None,
    annotation: Any,
) -> tuple[dict[str, Any], Any]:
    signature = inspect.signature(func)
    supported = {
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
    }
    params = list(signature.parameters.values())
    for param in params:
        if param.kind not in supported:
            raise IDSMakerError(
                f"{wrapper} parameter {param.name!r} is not supported. "
                "Only positional parameters can be exposed to IDScript."
            )

    if arguments is None:
        normalized = {
            param.name: Any if param.annotation is inspect._empty else param.annotation
            for param in params
        }
    else:
        unknown = set(arguments) - {param.name for param in params}
        missing = {param.name for param in params} - set(arguments)
        if unknown:
            raise IDSMakerError(
                f"{wrapper} argument option(s) {', '.join(repr(name) for name in sorted(unknown))} "
                "do not exist in the Python function signature."
            )
        if missing:
            raise IDSMakerError(
                f"{wrapper} argument option(s) {', '.join(repr(name) for name in sorted(missing))} "
                "are missing from the decorator arguments mapping."
            )
        normalized = dict(arguments)
        for param in params:
            if param.annotation is not inspect._empty and ids_type_name(param.annotation) != ids_type_name(normalized[param.name]):
                raise IDSMakerError(
                    f"{wrapper} argument {param.name!r} type mismatch: "
                    f"Python annotation is {ids_type_name(param.annotation)!r}, "
                    f"decorator value is {ids_type_name(normalized[param.name])!r}."
                )

    normalized_annotation = annotation
    if annotation is Any and signature.return_annotation is not inspect._empty:
        normalized_annotation = signature.return_annotation
    elif signature.return_annotation is not inspect._empty and ids_type_name(signature.return_annotation) != ids_type_name(annotation):
        raise IDSMakerError(
            f"{wrapper} return type mismatch: "
            f"Python annotation is {ids_type_name(signature.return_annotation)!r}, "
            f"decorator value is {ids_type_name(annotation)!r}."
        )

    return normalized, normalized_annotation
