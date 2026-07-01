"""Readable stack-based VM for official IDScript bytecode."""

from __future__ import annotations

from dataclasses import dataclass, field
import importlib
from pathlib import Path
from typing import Any

from ..builtins import BUILTIN_FUNCTIONS, BUILTIN_TYPES, default_value
from ..bytecode import FunctionCode, ModuleCode
from ...diagnostics import (
    IDSAttributeError,
    IDSKeyError,
    IDSModuleError,
    IDSNameError,
    IDSRuntimeError,
    IDSTypeError,
    IDSValueError,
)
from IDScript.maker.pyvalue import IDSPyValue, unwrap_py_args, unwrap_py_value, wrap_py_value


OPCODE_ALIASES = {
    "CONST": "LOAD_CONST",
    "DEFAULT": "LOAD_DEFAULT",
    "LOAD": "LOAD_NAME",
    "STORE": "STORE_NAME",
    "STORE_LOCAL": "STORE_FAST",
    "POP": "POP_TOP",
    "BINARY": "BINARY_OP",
    "UNARY": "UNARY_OP",
    "COMPARE": "COMPARE_OP",
    "JUMP": "JUMP_ABSOLUTE",
    "JUMP_IF_FALSE": "POP_JUMP_IF_FALSE",
    "CALL": "CALL_FUNCTION",
    "RETURN": "RETURN_VALUE",
    "MAKE_LIST": "BUILD_LIST",
    "MAKE_MAP": "BUILD_MAP",
    "GET_INDEX": "BINARY_SUBSCR",
    "SET_INDEX": "STORE_SUBSCR",
    "FOR_NEXT": "FOR_ITER",
    "IMPORT": "IMPORT_NAME",
    "THROW": "RAISE_ERROR",
    "GET_ATTR": "LOAD_ATTR",
    "SET_ATTR": "STORE_ATTR",
    "MAKE_STRUCT": "BUILD_STRUCT_TYPE",
    "MAKE_STRUCT_INSTANCE": "BUILD_STRUCT_INSTANCE",
    "ADD_FIELD": "STORE_FIELD",
    "ADD_METHOD": "STORE_METHOD",
    "MATCH": "MATCH_VALUE",
    "MAKE_ENUM": "BUILD_ENUM_TYPE",
    "MAKE_TYPE_ALIAS": "BUILD_TYPE_ALIAS",
    "MAKE_INTERFACE": "BUILD_INTERFACE",
    "INFO": "LOAD_INFO",
}


class _VMReturn(BaseException):
    def __init__(self, value: Any) -> None:
        self.value = value


@dataclass(frozen=True)
class VMReference:
    scope: dict[str, Any]
    name: str

    def get(self) -> Any:
        return self.scope[self.name]

    def set(self, value: Any) -> None:
        self.scope[self.name] = value

    def copy(self) -> VMReference:
        return VMReference(self.scope, self.name)

    def __repr__(self) -> str:
        return f"<Referensial: {self.name}>"


@dataclass(frozen=True)
class VMFunction:
    module_key: str
    name: str
    code: FunctionCode


@dataclass(frozen=True)
class VMBoundMethod:
    instance: Any
    function: VMFunction


@dataclass(frozen=True)
class VMMethod:
    function: VMFunction
    is_public: bool = True
    is_static: bool = False


@dataclass
class VMStructType:
    name: str
    fields: dict[str, dict[str, Any]]
    methods: dict[str, VMMethod] = field(default_factory=dict)


@dataclass
class VMStructInstance:
    struct: VMStructType
    values: dict[str, Any]

    def __getattr__(self, name: str) -> Any:
        if name in self.values:
            return self.values[name]
        raise IDSAttributeError(f"Struktur {self.struct.name!r} tidak punya attribute {name!r}")

    def __setattr__(self, name: str, value: Any) -> None:
        if name in {"struct", "values"}:
            object.__setattr__(self, name, value)
            return
        values = self.__dict__.get("values")
        struct = self.__dict__.get("struct")
        if values is not None and struct is not None and name in struct.fields:
            values[name] = value
            return
        object.__setattr__(self, name, value)

    def __repr__(self) -> str:
        public = {
            name: value
            for name, value in self.values.items()
            if not self.struct.fields.get(name, {}).get("is_priv", False)
        }
        return f"{self.struct.name} {public}"


@dataclass(frozen=True)
class VMTypeAlias:
    name: str
    target: Any
    params: list[str] = field(default_factory=list)

    def __call__(self, *args: Any) -> Any:
        return self.target

    def __repr__(self) -> str:
        return f"<TypeAlias: {self.name}>"


@dataclass(frozen=True)
class VMInterface:
    name: str
    fields: dict[str, Any]

    def __repr__(self) -> str:
        return f"<Interface: {self.name}>"


@dataclass
class VMEnumType:
    name: str
    variants: dict[str, dict[str, Any]]
    is_module_file: bool = False
    methods: dict[str, VMMethod] = field(default_factory=dict)

    def __getattr__(self, name: str) -> Any:
        if name not in self.variants:
            if name in self.methods:
                return self.methods[name].function
            raise IDSAttributeError(f"Enum {self.name!r} tidak punya variant {name!r}")
        schema = self.variants[name]
        if schema.get("is_priv") and self.is_module_file:
            raise IDSAttributeError(f"Enum {self.name!r} tidak punya variant {name!r}")
        kind = schema["kind"]
        if kind in {"unit", "discriminant"}:
            return VMEnumValue(
                self,
                name,
                kind,
                value=schema.get("value"),
            )
        return VMEnumVariantConstructor(self, name, schema)

    def __repr__(self) -> str:
        return f"<Enum: {self.name}>"


@dataclass(frozen=True)
class VMEnumVariantConstructor:
    enum: VMEnumType
    name: str
    schema: dict[str, Any]

    def __call__(self, *args: Any) -> VMEnumValue:
        kind = self.schema["kind"]
        if kind == "tuple":
            expected = self.schema.get("args", [])
            if len(args) != len(expected):
                raise IDSTypeError(f"{self.enum.name}.{self.name} membutuhkan {len(expected)} argument")
            for value, type_desc in zip(args, expected):
                _check_descriptor(value, type_desc)
            return VMEnumValue(self.enum, self.name, "tuple", payload=tuple(args))
        if kind == "struct":
            if len(args) != 1 or not isinstance(args[0], dict):
                raise IDSTypeError(f"{self.enum.name}.{self.name} membutuhkan satu kamus payload")
            payload = dict(args[0])
            expected_fields = self.schema.get("fields", {})
            unknown = set(payload) - set(expected_fields)
            missing = set(expected_fields) - set(payload)
            if unknown:
                raise IDSAttributeError(f"Field enum tidak dikenal: {', '.join(sorted(unknown))}")
            if missing:
                raise IDSAttributeError(f"Field enum belum diisi: {', '.join(sorted(missing))}")
            for field, type_desc in expected_fields.items():
                _check_descriptor(payload[field], type_desc)
            return VMEnumValue(self.enum, self.name, "struct", fields=payload)
        raise IDSTypeError(f"{self.enum.name}.{self.name} bukan constructor")

    def __repr__(self) -> str:
        return f"{self.enum.name}.{self.name}"


@dataclass(frozen=True)
class VMEnumValue:
    enum: VMEnumType
    variant: str
    kind: str
    payload: tuple[Any, ...] = ()
    fields: dict[str, Any] = field(default_factory=dict)
    value: Any = None

    def __getattr__(self, name: str) -> Any:
        if name in self.fields:
            return self.fields[name]
        if name in self.enum.methods:
            method = self.enum.methods[name]
            return method.function if method.is_static else VMBoundMethod(self, method.function)
        raise IDSAttributeError(f"Enum value {self.enum.name}.{self.variant} tidak punya attribute {name!r}")

    def __getitem__(self, key: int | str) -> Any:
        if self.kind == "tuple":
            return self.payload[int(key)]
        if self.kind == "struct":
            return self.fields[str(key)]
        raise IDSTypeError(f"Enum value {self.enum.name}.{self.variant} tidak punya payload")

    def __repr__(self) -> str:
        base = f"{self.enum.name}.{self.variant}"
        if self.kind == "tuple":
            return f"{base}({', '.join(repr(item) for item in self.payload)})"
        if self.kind == "struct":
            body = ", ".join(f"{key}: {value!r}" for key, value in self.fields.items())
            return f"{base} {{ {body} }}"
        if self.kind == "discriminant":
            return f"{base} = {self.value!r}"
        return base


@dataclass
class ModuleState:
    code: ModuleCode
    globals: dict[str, Any]
    exports: dict[str, Any]
    initialized: bool = False


class VM:
    """Execute IDScript ModuleCode.

    The VM uses a stack. Compiler instructions push values to the stack, pop
    values from it, and store values into local or module scopes.
    """

    def __init__(self, module: ModuleCode):
        self.root = module
        self.modules: dict[str, ModuleCode] = {}
        self._register_module(module)
        self.states: dict[str, ModuleState] = {}

    def _register_module(self, module: ModuleCode) -> None:
        self.modules[module.path] = module
        for nested in module.modules.values():
            self._register_module(nested)

    def run(self, name: str = "utama") -> Any:
        try:
            state = self._load_module(self.root.path)
            func = self._resolve_name(state, name, {})
            return self._call(func, [], state, {})
        except AttributeError:
            raise
        except IDSRuntimeError:
            raise
        except Exception as e:
            raise IDSRuntimeError.from_exception(e, file=self.root.path) from e

    def exports(self, module_key: str | None = None) -> dict[str, Any]:
        key = module_key or self.root.path
        try:
            state = self._load_module(key)
            return dict(state.exports)
        except IDSRuntimeError:
            raise
        except Exception as error:
            raise IDSRuntimeError.from_exception(error, file=key) from error

    def _load_module(self, module_key: str) -> ModuleState:
        if module_key not in self.modules:
            path = Path(module_key)
            if path.suffix in {".idsm", ".idsc"} and path.exists():
                loaded = ModuleCode.from_bytes(path.read_bytes())
                self._register_module(loaded)
                self.modules[module_key] = loaded
        if module_key in self.states:
            state = self.states[module_key]
            if state.initialized:
                return state
        else:
            state = ModuleState(code=self.modules[module_key], globals={}, exports={})
            self.states[module_key] = state

        for name, symbol in state.code.native_symbols.items():
            state.globals[name] = self._resolve_native_symbol(name, symbol)
        for name, function in state.code.functions.items():
            state.globals[name] = VMFunction(module_key, name, function)
        self._execute(state.code.code, state, {})
        state.exports.update({name: state.globals[name] for name in state.code.exports if name in state.globals})
        state.initialized = True
        return state

    def _execute(self, code: list[list[Any]], state: ModuleState, locals_: dict[str, Any]) -> Any:
        stack: list[Any] = []
        ip = 0
        while ip < len(code):
            inst = code[ip]
            op = OPCODE_ALIASES.get(inst[0], inst[0])

            if op == "LOAD_CONST":
                stack.append(inst[1])
            elif op == "LOAD_DEFAULT":
                stack.append(default_value(inst[1]))
            elif op == "LOAD_NAME":
                stack.append(self._resolve_name(state, inst[1], locals_))
            elif op == "LOAD_REFERENSIAL":
                stack.append(self._resolve_reference(state, inst[1], locals_))
            elif op == "LOAD_DEREFERENSIAL":
                stack.append(self._dereference(self._resolve_name(state, inst[1], locals_)))
            elif op == "COPY_REFERENSIAL":
                stack.append(self._copy_reference(self._resolve_name(state, inst[1], locals_)))
            elif op == "LOAD_INFO":
                stack.append(self._info_name(self._resolve_name(state, inst[1], locals_)))
            elif op == "STORE_NAME":
                self._store_name(state, locals_, inst[1], stack.pop())
            elif op == "STORE_DEREFERENSIAL":
                self._store_dereference(self._resolve_name(state, inst[1], locals_), stack.pop())
            elif op == "STORE_FAST":
                locals_[inst[1]] = stack.pop()
            elif op == "POP_TOP":
                if stack:
                    stack.pop()
            elif op == "BINARY_OP":
                right = stack.pop()
                left = stack.pop()
                stack.append(self._binary(inst[1], left, right, state, locals_))
            elif op == "UNARY_OP":
                stack.append(not self._truthy(stack.pop()))
            elif op == "TO_BOOL":
                stack.append(self._truthy(stack.pop()))
            elif op == "BOOL_AND":
                right = stack.pop()
                left = stack.pop()
                stack.append(right if self._truthy(left) else left)
            elif op == "BOOL_OR":
                right = stack.pop()
                left = stack.pop()
                stack.append(left if self._truthy(left) else right)
            elif op == "COMPARE_OP":
                right = stack.pop()
                left = stack.pop()
                stack.append(self._compare(inst[1], left, right, state, locals_))
            elif op == "JUMP_ABSOLUTE":
                ip = inst[1]
                continue
            elif op == "POP_JUMP_IF_FALSE":
                if not self._truthy(stack.pop()):
                    ip = inst[1]
                    continue
            elif op == "POP_JUMP_IF_TRUE":
                if self._truthy(stack.pop()):
                    ip = inst[1]
                    continue
            elif op == "CALL_FUNCTION":
                argc = inst[1]
                args = stack[-argc:] if argc else []
                if argc:
                    del stack[-argc:]
                stack.append(self._call(stack.pop(), args, state, locals_))
            elif op == "RETURN_VALUE":
                raise _VMReturn(stack.pop() if stack else None)
            elif op == "BUILD_LIST":
                count = inst[1]
                values = stack[-count:] if count else []
                if count:
                    del stack[-count:]
                stack.append(list(values))
            elif op == "BUILD_MAP":
                count = inst[1]
                result = {}
                for _ in range(count):
                    value = stack.pop()
                    key = stack.pop()
                    result[key] = value
                stack.append(result)
            elif op == "BINARY_SUBSCR":
                key = stack.pop()
                value = stack.pop()
                stack.append(self._get_index(value, key, state, locals_))
            elif op == "STORE_SUBSCR":
                value = stack.pop()
                key = stack.pop()
                target = stack.pop()
                self._set_index(target, key, value, state, locals_)
            elif op == "LOAD_ATTR":
                stack.append(self._get_attr(stack.pop(), inst[1]))
            elif op == "STORE_ATTR":
                value = stack.pop()
                target = stack.pop()
                self._set_attr(target, inst[1], value)
            elif op == "BUILD_STRUCT_TYPE":
                stack.append(VMStructType(inst[1], {field["name"]: field for field in inst[2]}))
            elif op == "BUILD_TYPE_ALIAS":
                stack.append(VMTypeAlias(inst[1], self._resolve_type_descriptor(inst[2], state, locals_), list(inst[3])))
            elif op == "BUILD_INTERFACE":
                stack.append(VMInterface(inst[1], dict(inst[2])))
            elif op == "BUILD_ENUM_TYPE":
                stack.append(
                    VMEnumType(
                        inst[1],
                        {variant["name"]: variant for variant in inst[2]},
                        state.code.path != self.root.path,
                    )
                )
            elif op == "BUILD_STRUCT_INSTANCE":
                count = inst[1]
                struct_values: dict[str, Any] = {}
                for _ in range(count):
                    value = stack.pop()
                    key = stack.pop()
                    struct_values[key] = value
                struct = stack.pop()
                if not isinstance(struct, VMStructType):
                    raise IDSTypeError("Constructor struktur membutuhkan VMStructType")
                stack.append(VMStructInstance(struct, struct_values))
            elif op == "STORE_METHOD":
                method = stack.pop()
                target = stack.pop()
                if not isinstance(method, VMFunction):
                    raise IDSTypeError("STORE_METHOD membutuhkan fungsi VM")
                if isinstance(target, VMStructType | VMEnumType):
                    target.methods[inst[1]] = VMMethod(
                        function=method,
                        is_public=bool(inst[2]) if len(inst) > 2 else True,
                        is_static=bool(inst[3]) if len(inst) > 3 else False,
                    )
                else:
                    raise IDSTypeError("STORE_METHOD membutuhkan struktur atau enum")
            elif op == "SETUP_TRY":
                self._execute_try(inst[1], inst[2], inst[3], inst[4], state, locals_)
            elif op == "GET_ITER":
                locals_[inst[1]] = iter(stack.pop())
            elif op == "FOR_ITER":
                try:
                    value = next(locals_[inst[1]])
                except StopIteration:
                    ip = inst[3]
                    continue
                targets = inst[2]
                if len(targets) == 1:
                    locals_[targets[0]] = value
                else:
                    for index, target in enumerate(targets):
                        locals_[target] = value[index]
            elif op == "IMPORT_NAME":
                imported = self._load_module(inst[1])
                for source, alias in inst[2]:
                    if source == "*":
                        state.globals.update(imported.exports)
                    elif source in imported.exports:
                        state.globals[alias or source] = imported.exports[source]
                    else:
                        raise IDSModuleError(f"Nama {source!r} tidak diekspor oleh {inst[1]!r}")
            elif op == "RAISE_ERROR":
                raise IDSRuntimeError(stack.pop() if stack else "Terjadi kesalahan pada VM IDScript")
            else:
                raise IDSValueError(f"Opcode VM {op!r} belum diimplementasikan")
            ip += 1
        return None

    def _store_name(self, state: ModuleState, locals_: dict[str, Any], name: str, value: Any) -> None:
        if name in locals_:
            locals_[name] = value
        else:
            state.globals[name] = value

    def _call(self, func: Any, args: list[Any], state: ModuleState, locals_: dict[str, Any]) -> Any:
        if isinstance(func, VMBoundMethod):
            generic_count = len(func.function.code.generic)
            args = list(args[:generic_count]) + [func.instance] + list(args[generic_count:])
            return self._call(func.function, args, state, locals_)
        if isinstance(func, VMFunction):
            state = self._load_module(func.module_key)
            locals_ = {}
            generic_count = len(func.code.generic)
            for i, name in enumerate(func.code.generic):
                locals_[name] = args[i]
            regular_args = args[generic_count:]
            arg_is_def = func.code.arg_is_def or [False] * len(func.code.args)
            for name, value, is_def in zip(func.code.args, regular_args, arg_is_def):
                if is_def and not isinstance(value, VMReference):
                    raise IDSTypeError(f"Argumen deferensial {name!r} membutuhkan referensial")
                locals_[name] = value
            try:
                return self._execute(func.code.code, state, locals_)
            except _VMReturn as ret:
                return ret.value
            except IDSRuntimeError:
                raise
            except Exception as error:
                raise IDSRuntimeError.from_exception(error, file=func.module_key) from error
        if callable(func):
            try:
                return self._wrap_py_value(func(*unwrap_py_args(args)))
            except IDSRuntimeError:
                raise
            except Exception as error:
                raise IDSRuntimeError.from_exception(error, file=state.code.path) from error
        raise IDSTypeError(f"Objek {func!r} tidak dapat dipanggil")

    def _wrap_py_value(self, value: Any) -> Any:
        return wrap_py_value(
            value,
            (
                VMReference,
                VMFunction,
                VMBoundMethod,
                VMMethod,
                VMStructType,
                VMStructInstance,
                VMTypeAlias,
                VMInterface,
                VMEnumType,
                VMEnumValue,
                VMEnumVariantConstructor,
            ),
        )

    def _resolve_native_symbol(self, name: str, symbol: dict[str, Any]) -> Any:
        module_name = symbol.get("module")
        qualname = symbol.get("qualname")
        if not module_name:
            raise IDSModuleError(f"Binding native {name!r} tidak lengkap")
        try:
            module = importlib.import_module(module_name)
            if symbol.get("kind") == "module":
                return module
            registry_key = symbol.get("registry_key")
            if registry_key:
                from IDScript.maker.registry import resolve_native

                return resolve_native(registry_key)
            if not qualname:
                raise IDSModuleError(f"Binding native {name!r} tidak punya qualname")
            value: Any = module
            for part in qualname.split("."):
                if part == "<locals>":
                    raise IDSModuleError("Binding lokal tidak dapat diimpor ulang")
                value = getattr(value, part)
            return value
        except IDSRuntimeError:
            raise
        except Exception as error:
            raise IDSRuntimeError.from_exception(error, file=symbol.get("file")) from error

    def _execute_try(
        self,
        body_code: list[list[Any]],
        handlers: list[dict[str, Any]],
        else_code: list[list[Any]],
        finally_code: list[list[Any]],
        state: ModuleState,
        locals_: dict[str, Any],
    ) -> None:
        try:
            self._execute(body_code, state, locals_)
        except Exception as err:
            if not handlers:
                raise
            if not isinstance(err, IDSRuntimeError):
                err = IDSRuntimeError.from_exception(err, file=state.code.path)
            self._execute_handler(handlers[0], err, state, locals_)
        else:
            if else_code:
                self._execute(else_code, state, locals_)
        finally:
            if finally_code:
                self._execute(finally_code, state, locals_)

    def _execute_handler(
        self,
        handler: dict[str, Any],
        error: Exception,
        state: ModuleState,
        locals_: dict[str, Any],
    ) -> None:
        alias = handler["alias"]
        missing = object()
        previous = locals_.get(alias, missing)
        locals_[alias] = error
        try:
            self._execute(handler["code"], state, locals_)
        finally:
            if previous is missing:
                locals_.pop(alias, None)
            else:
                locals_[alias] = previous

    def _resolve_name(self, state: ModuleState, name: str, locals_: dict[str, Any]) -> Any:
        if name in locals_:
            return locals_[name]
        if name in state.globals:
            return state.globals[name]
        if name in BUILTIN_FUNCTIONS:
            return BUILTIN_FUNCTIONS[name]
        if name in BUILTIN_TYPES:
            return BUILTIN_TYPES[name]
        if name == "benar":
            return True
        if name == "salah":
            return False
        if name == "kosong":
            return None
        raise IDSNameError(f"{name!r} tidak terdefinisi")

    def _resolve_reference(self, state: ModuleState, name: str, locals_: dict[str, Any]) -> VMReference:
        if name in locals_:
            return VMReference(locals_, name)
        if name in state.globals:
            return VMReference(state.globals, name)
        raise IDSNameError(f"{name!r} tidak terdefinisi")

    def _dereference(self, value: Any) -> Any:
        if not isinstance(value, VMReference):
            raise IDSTypeError(f"{value!r} bukan referensial")
        return value.get()

    def _store_dereference(self, value: Any, new_value: Any) -> None:
        if not isinstance(value, VMReference):
            raise IDSTypeError(f"{value!r} bukan referensial")
        value.set(new_value)

    def _copy_reference(self, value: Any) -> VMReference:
        if not isinstance(value, VMReference):
            raise IDSTypeError(f"{value!r} bukan referensial")
        return value.copy()

    def _get_attr(self, value: Any, name: str) -> Any:
        if isinstance(value, VMEnumType):
            return getattr(value, name)
        if isinstance(value, VMEnumValue):
            return getattr(value, name)
        if isinstance(value, VMStructType):
            if name in value.methods:
                return value.methods[name].function
            raise IDSAttributeError(f"Struktur {value.name!r} tidak punya attribute {name!r}")
        if isinstance(value, VMStructInstance):
            if name in value.values:
                return value.values[name]
            if name in value.struct.methods:
                method = value.struct.methods[name]
                return method.function if method.is_static else VMBoundMethod(value, method.function)
        if isinstance(value, dict):
            return value[name]
        if isinstance(value, IDSPyValue) and name == "isiAsli":
            return value.isiAsli
        return self._wrap_py_value(getattr(value, name))

    def _set_attr(self, value: Any, name: str, new_value: Any) -> None:
        if isinstance(value, VMStructInstance):
            if name not in value.struct.fields:
                raise IDSAttributeError(f"Struktur {value.struct.name!r} tidak punya field {name!r}")
            value.values[name] = new_value
            return
        setattr(value, name, unwrap_py_value(new_value))

    def _has_method(self, value: Any, name: str) -> bool:
        return isinstance(value, VMStructInstance) and name in value.struct.methods

    def _call_method(
        self,
        value: VMStructInstance,
        name: str,
        args: list[Any],
        state: ModuleState,
        locals_: dict[str, Any],
    ) -> Any:
        method = value.struct.methods[name]
        if method.is_static:
            return self._call(method.function, args, state, locals_)
        return self._call(VMBoundMethod(value, method.function), args, state, locals_)

    def _get_index(self, value: Any, key: Any, state: ModuleState, locals_: dict[str, Any]) -> Any:
        if self._has_method(value, "__getitem__"):
            return self._call_method(value, "__getitem__", [key], state, locals_)
        return self._wrap_py_value(value[unwrap_py_value(key)])

    def _set_index(self, target: Any, key: Any, value: Any, state: ModuleState, locals_: dict[str, Any]) -> None:
        if self._has_method(target, "__setitem__"):
            self._call_method(target, "__setitem__", [key, value], state, locals_)
            return
        target[unwrap_py_value(key)] = unwrap_py_value(value)

    def _truthy(self, value: Any) -> bool:
        return bool(value)

    def _info_name(self, value: Any) -> str:
        if value is None:
            return "Kosong"
        if isinstance(value, bool):
            return "Boolean"
        if isinstance(value, int):
            return "Angka"
        if isinstance(value, float):
            return "Float"
        if isinstance(value, str):
            return "Teks"
        if isinstance(value, list):
            return "Daftar"
        if isinstance(value, dict):
            return "Kamus"
        if isinstance(value, VMEnumType):
            return "Enum"
        if isinstance(value, (VMEnumValue, VMEnumVariantConstructor)):
            return "VarianEnum"
        if isinstance(value, (VMStructType, VMStructInstance)):
            return "Struktur"
        if isinstance(value, VMInterface):
            return "Antarmuka"
        if isinstance(value, VMTypeAlias) or isinstance(value, type):
            return "Tipe"
        if isinstance(value, (VMFunction, VMBoundMethod)) or callable(value):
            return "Fungsi"
        if isinstance(value, VMReference):
            return "Referensial"
        return "Objek"

    def _binary(self, op: str, left: Any, right: Any, state: ModuleState, locals_: dict[str, Any]) -> Any:
        methods = {
            "+": "__add__",
            "*": "__mul__",
        }
        reverse_methods = {
            "*": "__rmul__",
        }
        method = methods.get(op)
        if method and self._has_method(left, method):
            return self._call_method(left, method, [right], state, locals_)
        reverse_method = reverse_methods.get(op)
        if reverse_method and self._has_method(right, reverse_method):
            return self._call_method(right, reverse_method, [left], state, locals_)
        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op == "/":
            return left / right
        if op == "**":
            return left ** right
        raise IDSValueError(f"Operator binary {op!r} belum didukung")

    def _compare(self, op: str, left: Any, right: Any, state: ModuleState, locals_: dict[str, Any]) -> bool:
        methods = {
            "==": "__eq__",
            "!=": "__ne__",
            ">": "__gt__",
            ">=": "__ge__",
            "<": "__lt__",
            "<=": "__le__",
        }
        method = methods.get(op)
        if method and self._has_method(left, method):
            return bool(self._call_method(left, method, [right], state, locals_))
        if op == "==":
            return left == right
        if op == "!=":
            return left != right
        if op == ">":
            return left > right
        if op == ">=":
            return left >= right
        if op == "<":
            return left < right
        if op == "<=":
            return left <= right
        if op == "in":
            if self._has_method(right, "__contains__"):
                return bool(self._call_method(right, "__contains__", [left], state, locals_))
            return left in right
        if op == "not in":
            if self._has_method(right, "__contains__"):
                return not bool(self._call_method(right, "__contains__", [left], state, locals_))
            return left not in right
        if op == "is":
            return left is right
        if op == "is not":
            return left is not right
        raise IDSValueError(f"Operator compare {op!r} belum didukung")

    def _resolve_type_descriptor(self, descriptor: Any, state: ModuleState, locals_: dict[str, Any]) -> Any:
        if not isinstance(descriptor, dict):
            return Any
        kind = descriptor.get("kind")
        if kind == "name":
            name = descriptor["name"]
            if name in BUILTIN_TYPES:
                return BUILTIN_TYPES[name]
            resolved = self._resolve_name(state, name, locals_)
            if isinstance(resolved, VMTypeAlias):
                return resolved.target
            return resolved
        if kind == "python":
            return {
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "NoneType": type(None),
                "Any": Any,
            }.get(descriptor["name"], Any)
        if kind == "list":
            return list
        if kind == "dict":
            return dict
        if kind == "optional":
            return (self._resolve_type_descriptor(descriptor["type"], state, locals_), type(None))
        if kind == "union":
            return tuple(self._resolve_type_descriptor(item, state, locals_) for item in descriptor["items"])
        return Any


def _check_descriptor(value: Any, descriptor: Any) -> None:
    if not isinstance(descriptor, dict):
        return
    kind = descriptor.get("kind")
    if kind == "name":
        expected = BUILTIN_TYPES.get(descriptor["name"])
        if expected is not None and expected is not Any and not isinstance(value, expected):
            raise IDSTypeError(f"Nilai {value!r} bukan tipe {descriptor['name']}")
    elif kind == "python":
        expected = {"str": str, "int": int, "float": float, "bool": bool, "NoneType": type(None)}.get(descriptor["name"])
        if expected is not None and not isinstance(value, expected):
            raise IDSTypeError(f"Nilai {value!r} bukan tipe {descriptor['name']}")
    elif kind == "list" and not isinstance(value, list):
        raise IDSTypeError(f"Nilai {value!r} bukan daftar")
    elif kind == "dict" and not isinstance(value, dict):
        raise IDSTypeError(f"Nilai {value!r} bukan kamus")
