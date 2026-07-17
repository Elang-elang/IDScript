from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

from ..compile.ids_ast import GenericParam as _GenericParam
from ..compile.Compiler.bytecode import ModuleCode
from .errors import IDSError, IDSMakerError, ensure_type, validate_options
from .function import IDSFunctionBinding, IDSMethodBinding
from .generic import IDSGeneric, normalize_generic_params
from .implement import IDSImplementBinding
from .klass import IDSClassBinding
from .module_path import resolve_module
from .registry import register_native
from .structure import IDSStructBinding
from .trait import IDSTraitBinding
from .types import type_descriptor


@dataclass
class IDSDeclaration:
    name: str
    type: Any
    value: Any = None


@dataclass
class IDSTypedef:
    name: str
    value: Any
    params: list[_GenericParam] | None = None


@dataclass(init=False)
class IDSModule:
    OPTIONS = {"name", "path"}

    name: str
    path: str | Path | None = None
    items: list[Any] = field(default_factory=list)
    declarations: list[IDSDeclaration] = field(default_factory=list)
    typedefs: list[IDSTypedef] = field(default_factory=list)

    def __init__(self, *args: Any, **options: Any) -> None:
        if len(args) > 2:
            raise IDSMakerError(
                "IDSModule accepts at most two positional arguments: name and path. "
                f"Received {len(args)} positional argument(s)."
            )
        validate_options("IDSModule", options, self.OPTIONS)
        name = args[0] if args else None
        path = args[1] if len(args) == 2 else None
        if "name" in options:
            if name is not None:
                raise IDSMakerError("IDSModule received 'name' twice; pass it either positionally or as a keyword.")
            name = options["name"]
        if "path" in options:
            if path is not None:
                raise IDSMakerError("IDSModule received 'path' twice; pass it either positionally or as a keyword.")
            path = options["path"]
        if name is None:
            raise IDSMakerError("IDSModule requires option 'name'.")
        ensure_type("IDSModule", "name", name, str)
        if path is not None:
            ensure_type("IDSModule", "path", path, (str, Path))
        self.name = name
        self.path = path
        self.items = []
        self.declarations = []
        self.typedefs = []

    def __call__(self, func: Callable[[IDSModule], Any]) -> IDSModule:
        if not callable(func):
            raise IDSMakerError(f"IDSModule can only decorate callables; got {type(func).__name__}.")
        func(self)
        return self

    def add(self, *items: Any) -> IDSModule:
        self.items.extend(items)
        return self

    def declare(self, name: str, type: Any, value: Any = None) -> IDSModule:
        ensure_type("IDSModule.declare", "name", name, str)
        self.declarations.append(IDSDeclaration(name=name, type=type, value=value))
        return self

    def typedef(
        self,
        name: str,
        value: Any,
        params: str | list[str | tuple | IDSGeneric] | None = None,
    ) -> IDSModule:
        ensure_type("IDSModule.typedef", "name", name, str)
        normalized = normalize_generic_params(params, label="IDSModule.typedef")
        ast_params = [g.to_ast_param() for g in normalized]
        self.typedefs.append(IDSTypedef(name=name, value=value, params=ast_params))
        return self

    def build(self) -> ModuleCode:
        path = Path(self.path or f"{self.name}.idsm").resolve()
        module = ModuleCode(name=self.name, path=str(path))
        for item in self.items:
            self._add_item(module, item)
        for declaration in self.declarations:
            if self._is_json_value(declaration.value):
                module.code.append(["LOAD_CONST", declaration.value])
            else:
                native_name = f"__py_native__.{declaration.name}"
                module.native_symbols[native_name] = self._native_symbol(declaration.value)
                module.code.append(["LOAD_NAME", native_name])
            module.code.append(["STORE_NAME", declaration.name])
            self._export(module, declaration.name)
        for typedef in self.typedefs:
            params = [p.name.id if hasattr(p, 'name') else str(p) for p in (typedef.params or [])]
            module.code.append(["BUILD_TYPE_ALIAS", typedef.name, type_descriptor(typedef.value), params])
            module.code.append(["STORE_NAME", typedef.name])
            self._export(module, typedef.name)
        return module

    def write(self, path: str | Path | None = None, *, compiled: bool = False, both: bool = False) -> Path | tuple[Path, Path] | None:
        target = Path(path or self.path or f"{self.name}.idsm").resolve()
        try:
            return self._write(target, compiled=compiled, both=both)
        except IDSError as error:
            raise error
        except Exception as error:
            raise IDSMakerError(str(error)) from error

    def _write(self, path: str | Path | None = None, *, compiled: bool = False, both: bool = False) -> Path | tuple[Path, Path]:
        target = Path(path or self.path or f"{self.name}.idsm").resolve()
        module = self.build()
        module.path = str(target)
        if both:
            module_path = target.with_suffix(".idsm")
            compiled_path = target.with_suffix(".idsc")
            module.path = str(module_path)
            module_path.write_bytes(module.to_module_bytes())
            module.path = str(compiled_path)
            compiled_path.write_bytes(module.to_compiled_bytes())
            return module_path, compiled_path
        if compiled:
            target = target.with_suffix(".idsc")
            module.path = str(target)
            target.write_bytes(module.to_compiled_bytes())
            return target
        target = target.with_suffix(".idsm")
        module.path = str(target)
        target.write_bytes(module.to_module_bytes())
        return target

    def _add_item(self, module: ModuleCode, item: Any) -> None:
        if isinstance(item, IDSClassBinding):
            self._add_struct(module, item.struct)
            if item.implement is not None:
                self._add_implement(module, item.implement)
            return
        if isinstance(item, IDSStructBinding):
            self._add_struct(module, item)
            return
        if isinstance(item, IDSImplementBinding):
            self._add_implement(module, item)
            return
        if isinstance(item, IDSTraitBinding):
            self._add_trait(module, item)
            return
        if isinstance(item, IDSMethodBinding):
            raise IDSMakerError(
                "IDSMethod cannot be added as a top-level module function. "
                "Use IDSFunction for functions, or place IDSMethod inside IDSClass, IDSImplement, or IDSTrait."
            )
        if isinstance(item, IDSFunctionBinding):
            self._add_function(module, item)
            return
        raise IDSMakerError(
            f"IDSModule.add received unsupported item {item!r}. "
            "Expected IDSFunction, IDSStruct, IDSImplement, IDSClass, or IDSTrait binding."
        )

    def _add_function(self, module: ModuleCode, item: IDSFunctionBinding) -> None:
        native_name = f"__py_native__.{item.name}"
        ns = dict(item.native_symbol)
        if ns.get("module") == "__main__" and self.path:
            ns["module"] = resolve_module(item.func)
        module.native_symbols[native_name] = ns
        module.functions[item.name] = item.to_function_code(native_name=native_name)
        if not item.is_priv:
            self._export(module, item.name)

    def _add_struct(self, module: ModuleCode, item: IDSStructBinding) -> None:
        module.code.append(["BUILD_STRUCT_TYPE", item.name, item.fields()])
        module.code.append(["STORE_NAME", item.name])
        if not item.is_priv:
            self._export(module, item.name)

    def _add_implement(self, module: ModuleCode, item: IDSImplementBinding) -> None:
        if item.params:
            raise IDSMakerError(
                f"IDSImplement {item.name!r}: impl-level generics ({[p.name for p in item.params]}) "
                "not yet supported by the VM runtime. Use concrete type_args instead."
            )
        if item.type_args:
            raise IDSMakerError(
                f"IDSImplement {item.name!r}: monomorphization with type_args={item.type_args} "
                "not yet supported by the VM runtime."
            )
        for method in item.methods:
            function_name = f"{item.name}.{method.name}"
            native_name = f"__py_native__.{function_name}"
            module.native_symbols[native_name] = method.native_symbol
            module.functions[function_name] = method.to_function_code(name=function_name, native_name=native_name)
            module.code.append(["LOAD_NAME", item.name])
            module.code.append(["LOAD_NAME", function_name])
            module.code.append(["STORE_METHOD", method.name, not method.is_priv, method.static])

    def _add_trait(self, module: ModuleCode, item: IDSTraitBinding) -> None:
        if item.params:
            raise IDSMakerError(
                f"IDSTrait {item.name!r}: generic traits "
                "not yet supported by the VM runtime."
            )
        module.code.append(["LOAD_CONST", item.descriptor()])
        module.code.append(["STORE_NAME", item.name])
        if not item.is_priv:
            self._export(module, item.name)

    def _export(self, module: ModuleCode, name: str) -> None:
        if name not in module.exports:
            module.exports.append(name)

    def _is_json_value(self, value: Any) -> bool:
        try:
            json.dumps(value)
            return True
        except TypeError:
            return False

    def _native_symbol(self, value: Any) -> dict[str, Any]:
        key = register_native(value)
        if isinstance(value, ModuleType):
            return {
                "kind": "module",
                "module": value.__name__,
                "registry_key": key,
            }
        qualname = getattr(value, "__qualname__", None)
        if not qualname:
            raise IDSMakerError(
                f"Declaration value {value!r} cannot be serialized or registered as a native binding. "
                "Use a JSON-compatible value, Python module, function, class, or importable object."
            )
        return {
            "kind": "object",
            "module": resolve_module(value),
            "qualname": qualname,
            "registry_key": key,
        }
