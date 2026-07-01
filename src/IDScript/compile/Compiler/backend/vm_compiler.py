"""Compile shared IDScript AST nodes into official VM bytecode."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ...diagnostics import IDSLoopError, IDSValueError
from ...ids_ast import *
from ...runtime.types import EMPTY
from ..bytecode import FunctionCode, Instruction, ModuleCode
from ..frontend import parse_source


BUILTINS_DIR = Path(__file__).resolve().parents[3] / "builtins"


class BytecodeCompiler:
    """AST visitor that emits readable VM instructions.

    This class intentionally keeps each AST node handler small. If you want to
    add a language feature, add the AST handler here, add any needed opcode to
    TOKEN.json, then implement that opcode in runtime/vm.py.
    """

    def __init__(self):
        self._cache: dict[str, ModuleCode] = {}
        self._path_cache: dict[str, ModuleCode] = {}
        self._loop_stack: list[dict[str, Any]] = []
        self._temp_id = 0

    def compile_source(self, code: str, file: str | Path = "<memory.ids>") -> ModuleCode:
        module = self.compile_ast(parse_source(code, str(file)), Path(file).resolve())
        module.modules = {path: value for path, value in self._cache.items() if path != module.path}
        return module

    def compile_file(self, file: str | Path) -> ModuleCode:
        path = Path(file).resolve()
        module = self._compile_path(path)
        module.modules = {key: value for key, value in self._cache.items() if key != module.path}
        return module

    def compile_ast(self, node: Program, file: str | Path) -> ModuleCode:
        return self._compile_program(node, Path(file).resolve())

    def _compile_path(self, path: Path) -> ModuleCode:
        key = str(path)
        if key in self._path_cache:
            return self._path_cache[key]
        if path.suffix in {".idsm", ".idsc"}:
            return self._load_binary_module(path)
        return self._compile_program(parse_source(path.read_text(), str(path)), path)

    def _load_binary_module(self, path: Path) -> ModuleCode:
        module = ModuleCode.from_bytes(path.read_bytes())
        self._register_module(module)
        self._path_cache[str(path)] = module
        return module

    def _register_module(self, module: ModuleCode) -> None:
        self._cache[module.path] = module
        self._path_cache[module.path] = module
        for nested in module.modules.values():
            self._register_module(nested)

    def _compile_program(self, node: Program, file: Path) -> ModuleCode:
        key = str(file)
        if key in self._cache:
            return self._cache[key]
        module = ModuleCode(name=file.stem, path=key)
        self._cache[key] = module
        self._path_cache[key] = module
        code: list[Instruction] = []
        module.code = code
        for body in node.bodies or []:
            self._stmt(body, code, module, file)
        return module

    def _stmt(self, node: Any, code: list[Instruction], module: ModuleCode, file: Path) -> None:
        if isinstance(node, Top | Statement):
            if node.body is not None:
                self._stmt(node.body, code, module, file)
            return
        if isinstance(node, Block):
            for body in node.bodies or []:
                self._stmt(body, code, module, file)
            return
        if isinstance(node, FromImport):
            self._import_stmt(node, code, module, file)
            return
        if isinstance(node, Const):
            self._expr(node.expr, code)
            code.append(["STORE_NAME", node.name.id])
            if not node.is_priv:
                module.exports.append(node.name.id)
            return
        if isinstance(node, Variable):
            if node.expr is EMPTY:
                code.append(["LOAD_DEFAULT", self._type_name(node.type)])
            else:
                self._expr(node.expr, code)
            code.append(["STORE_FAST" if code is not module.code else "STORE_NAME", node.name.id])
            return
        if isinstance(node, Final):
            self._expr(node.expr, code)
            code.append(["STORE_FAST" if code is not module.code else "STORE_NAME", node.name.id])
            return
        if isinstance(node, Assignment):
            self._assignment(node, code)
            return
        if isinstance(node, Function):
            module.functions[node.name.id] = self._function(node.name.id, node.attrs, node.body, module, file)
            if not node.is_priv:
                module.exports.append(node.name.id)
            return
        if isinstance(node, TypeDef):
            code.append(["BUILD_TYPE_ALIAS", node.alias.id, self._type_descriptor(node.value), [arg.id for arg in node.args]])
            code.append(["STORE_NAME", node.alias.id])
            if not node.is_priv:
                module.exports.append(node.alias.id)
            return
        if isinstance(node, InterFace):
            code.append(["BUILD_INTERFACE", node.alias.id, self._interface_descriptor(node.args)])
            code.append(["STORE_NAME", node.alias.id])
            if not node.is_priv:
                module.exports.append(node.alias.id)
            return
        if isinstance(node, Enum):
            code.append(["BUILD_ENUM_TYPE", node.name.id, [self._enum_variant(field) for field in node.fields]])
            code.append(["STORE_NAME", node.name.id])
            if not node.is_priv:
                module.exports.append(node.name.id)
            return
        if isinstance(node, Structure):
            fields = [
                {"name": field.name.id, "type": self._type_name(field.type), "is_priv": field.is_priv}
                for field in node.body.bodies
            ]
            code.append(["BUILD_STRUCT_TYPE", node.name.id, fields])
            code.append(["STORE_NAME", node.name.id])
            if not node.is_priv:
                module.exports.append(node.name.id)
            return
        if isinstance(node, Implementation):
            self._implementation(node, code, module, file)
            return
        if isinstance(node, If):
            self._if(node, code, module, file)
            return
        if isinstance(node, While):
            self._while(node, code, module, file)
            return
        if isinstance(node, For):
            self._for(node, code, module, file)
            return
        if isinstance(node, Try):
            self._try(node, code, module, file)
            return
        if isinstance(node, Kembalikan):
            self._expr(node.value, code)
            code.append(["RETURN_VALUE"])
            return
        if isinstance(node, Kesalahan):
            self._expr(node.value, code)
            code.append(["RAISE_ERROR"])
            return
        if isinstance(node, Berhentikan):
            if not self._loop_stack:
                raise IDSLoopError("berhentikan hanya dapat digunakan di dalam loop")
            self._loop_stack[-1]["breaks"].append(len(code))
            code.append(["JUMP_ABSOLUTE", None])
            return
        if isinstance(node, Lanjutkan):
            if not self._loop_stack:
                raise IDSLoopError("lanjutkan hanya dapat digunakan di dalam loop")
            code.append(["JUMP_ABSOLUTE", self._loop_stack[-1]["continue"]])
            return
        if isinstance(node, Expression):
            self._expr(node, code)
            code.append(["POP_TOP"])
            return
        if isinstance(node, Switch):
            raise IDSValueError(f"{type(node).__name__} belum stabil di Compiler VM resmi")
        raise IDSValueError(f"Compiler VM belum mendukung statement {type(node).__name__}")

    def _expr(self, node: Any, code: list[Instruction]) -> None:
        if isinstance(node, Expression):
            self._expr(node.value, code)
        elif isinstance(node, Name):
            code.append(["LOAD_NAME", node.id])
        elif isinstance(node, Referensial):
            code.append(["LOAD_REFERENSIAL", node.name.id])
        elif isinstance(node, Deferensial):
            code.append(["LOAD_DEREFERENSIAL", node.name.id])
        elif isinstance(node, SalinReferensial):
            code.append(["COPY_REFERENSIAL", node.name.id])
        elif isinstance(node, Info):
            code.append(["LOAD_INFO", node.name.id])
        elif isinstance(node, Constant):
            code.append(["LOAD_CONST", node.value])
        elif isinstance(node, BinOp):
            self._expr(node.left, code)
            self._expr(node.right, code)
            code.append(["BINARY_OP", node.op])
        elif isinstance(node, UnaryOp):
            self._expr(node.operand, code)
            code.append(["UNARY_OP", node.op])
        elif isinstance(node, BoolOp):
            if len(node.values) != 2:
                raise IDSValueError("BoolOp multi nilai belum didukung di VM resmi")
            self._expr(node.values[0], code)
            self._expr(node.values[1], code)
            code.append(["BOOL_AND" if node.op == "and" else "BOOL_OR"])
        elif isinstance(node, Compare):
            self._expr(node.left, code)
            self._expr(node.comparators[0], code)
            code.append(["COMPARE_OP", node.ops[0]])
        elif isinstance(node, Call):
            self._expr(node.func, code)
            for g in node.generic or []:
                self._expr(g, code)
            for arg in node.args or []:
                self._expr(arg, code)
            argc = len(node.args or []) + len(node.generic or [])
            code.append(["CALL_FUNCTION", argc])
        elif isinstance(node, Attribute):
            self._expr(node.value, code)
            code.append(["LOAD_ATTR", node.attr])
        elif isinstance(node, Index):
            self._expr(node.value, code)
            self._expr(node.key, code)
            code.append(["BINARY_SUBSCR"])
        elif isinstance(node, StructFielded):
            self._expr(node.struct, code)
            for key, value in zip(node.kwargs.keys, node.kwargs.values):
                self._expr(key, code)
                self._expr(value, code)
            code.append(["BUILD_STRUCT_INSTANCE", len(node.kwargs.keys)])
        elif isinstance(node, Daftar):
            for item in node.elts:
                self._expr(item, code)
            code.append(["BUILD_LIST", len(node.elts)])
        elif isinstance(node, Kamus):
            for key, value in zip(node.keys, node.values):
                self._expr(key, code)
                self._expr(value, code)
            code.append(["BUILD_MAP", len(node.keys)])
        else:
            raise IDSValueError(f"Compiler VM belum mendukung expression {type(node).__name__}")

    def _assignment(self, node: Assignment, code: list[Instruction]) -> None:
        if isinstance(node.target, Deferensial):
            self._expr(node.expr, code)
            code.append(["STORE_DEREFERENSIAL", node.target.name.id])
            return
        if isinstance(node.target, Name):
            self._expr(node.expr, code)
            code.append(["STORE_NAME", node.target.id])
            return
        if isinstance(node.target, Index):
            self._expr(node.target.value, code)
            self._expr(node.target.key, code)
            self._expr(node.expr, code)
            code.append(["STORE_SUBSCR"])
            return
        if isinstance(node.target, Attribute):
            self._expr(node.target.value, code)
            self._expr(node.expr, code)
            code.append(["STORE_ATTR", node.target.attr])
            return
        raise IDSValueError("Target assignment belum didukung di VM resmi")

    def _function(self, name: str, attrs: AttrsFunc, block: Block, module: ModuleCode, file: Path) -> FunctionCode:
        ast_args = list(attrs.args.args or [])
        args = [arg.name.id for arg in ast_args]
        arg_is_def = [arg.is_def for arg in ast_args]
        generic = [g.id for g in attrs.generic] if attrs.generic else []
        body: list[Instruction] = []
        for stmt in block.bodies or []:
            self._stmt(stmt, body, module, file)
        if not body or body[-1][0] not in {"RETURN", "RETURN_VALUE"}:
            body.append(["LOAD_CONST", None])
            body.append(["RETURN_VALUE"])
        return FunctionCode(name=name, args=args, code=body, arg_is_def=arg_is_def, generic=generic)

    def _implementation(self, node: Implementation, code: list[Instruction], module: ModuleCode, file: Path) -> None:
        struct_name = node.name.id
        for method in node.body.bodies:
            method_name = f"{struct_name}.{method.name.id}"
            module.functions[method_name] = self._function(method_name, method.attrs, method.body, module, file)
            code.append(["LOAD_NAME", struct_name])
            code.append(["LOAD_NAME", method_name])
            code.append(["STORE_METHOD", method.name.id, not method.is_priv, method.static])

    def _if(self, node: If, code: list[Instruction], module: ModuleCode, file: Path) -> None:
        jump_when_true = self._condition(node.test, code)
        jump_false = len(code)
        code.append(["POP_JUMP_IF_TRUE" if jump_when_true else "POP_JUMP_IF_FALSE", None])
        self._stmt(node.body, code, module, file)
        jump_end = len(code)
        code.append(["JUMP_ABSOLUTE", None])
        code[jump_false][1] = len(code)
        if node.orelse is not None:
            self._stmt(node.orelse, code, module, file)
        code[jump_end][1] = len(code)

    def _while(self, node: While, code: list[Instruction], module: ModuleCode, file: Path) -> None:
        start = len(code)
        jump_when_true = self._condition(node.test, code)
        jump_false = len(code)
        code.append(["POP_JUMP_IF_TRUE" if jump_when_true else "POP_JUMP_IF_FALSE", None])
        breaks: list[int] = []
        self._loop_stack.append({"breaks": breaks, "continue": start})
        self._stmt(node.body, code, module, file)
        code.append(["JUMP_ABSOLUTE", start])
        end = len(code)
        code[jump_false][1] = end
        for pos in breaks:
            code[pos][1] = end
        self._loop_stack.pop()

    def _for(self, node: For, code: list[Instruction], module: ModuleCode, file: Path) -> None:
        iterator_name = self._temp("iter")
        self._expr(node.iter, code)
        code.append(["GET_ITER", iterator_name])
        start = len(code)
        targets = [target.name.id for target in node.target]
        for_next = len(code)
        code.append(["FOR_ITER", iterator_name, targets, None])
        breaks: list[int] = []
        self._loop_stack.append({"breaks": breaks, "continue": start})
        self._stmt(node.body, code, module, file)
        code.append(["JUMP_ABSOLUTE", start])
        end = len(code)
        code[for_next][3] = end
        for pos in breaks:
            code[pos][1] = end
        self._loop_stack.pop()

    def _try(self, node: Try, code: list[Instruction], module: ModuleCode, file: Path) -> None:
        body_code = self._block_code(node.body, module, file)
        handlers = [
            {
                "alias": handler.alias.id,
                "code": self._block_code(handler.body, module, file),
            }
            for handler in node.handler
        ]
        else_code = self._block_code(node.orelse, module, file) if node.orelse is not None else []
        finally_code = self._block_code(node.finalbody, module, file) if node.finalbody is not None else []
        code.append(["SETUP_TRY", body_code, handlers, else_code, finally_code])

    def _block_code(self, block: Block, module: ModuleCode, file: Path) -> list[Instruction]:
        block_code: list[Instruction] = []
        self._stmt(block, block_code, module, file)
        return block_code

    def _import_stmt(self, node: FromImport, code: list[Instruction], module: ModuleCode, file: Path) -> None:
        if node._from.startswith("."):
            module_path = (file.parent / Path(node._from)).resolve()
        else:
            module_path = (BUILTINS_DIR / Path(node._from)).resolve()
        imported = self._compile_path(module_path)
        specs = []
        for item in node._imports:
            source = item.name.id
            alias = item.alias.id if item.alias is not None else source
            specs.append([source, alias])
            if not item.is_priv:
                module.exports.append(alias)
        code.append(["IMPORT_NAME", imported.path, specs])

    def _condition(self, node: Any, code: list[Instruction]) -> bool:
        if isinstance(node, Expression):
            return self._condition(node.value, code)
        if isinstance(node, UnaryOp) and node.op == "not":
            self._expr(node.operand, code)
            code.append(["TO_BOOL"])
            return True
        self._expr(node, code)
        code.append(["TO_BOOL"])
        return False

    def _type_name(self, node: Type) -> str:
        if isinstance(node.type, Name):
            return node.type.id
        if isinstance(node.type, type):
            return node.type.__name__
        return type(node.type).__name__

    def _type_descriptor(self, node: Any) -> Any:
        if isinstance(node, Type):
            descriptor = self._type_descriptor(node.type)
            if node.option:
                return {"kind": "optional", "type": descriptor}
            return descriptor
        if isinstance(node, Name):
            return {"kind": "name", "name": node.id}
        if isinstance(node, type):
            return {"kind": "python", "name": node.__name__}
        if isinstance(node, DAFTAR):
            return {"kind": "list", "item": self._type_descriptor(node.body)}
        if isinstance(node, KAMUS):
            return {"kind": "dict", "key": self._type_descriptor(node.key), "value": self._type_descriptor(node.value)}
        if isinstance(node, SERIKAT):
            return {"kind": "union", "items": [self._type_descriptor(item) for item in node.bodies]}
        if isinstance(node, LITERAL):
            return {"kind": "literal", "items": [self._literal_value(item) for item in node.bodies]}
        if isinstance(node, Dynamic):
            return {"kind": "dynamic", "name": node.name.id, "args": [arg.id for arg in node.args]}
        return {"kind": "raw", "name": type(node).__name__}

    def _interface_descriptor(self, node: InterFaceBody | list[InterFaceBody]) -> dict[str, Any]:
        if isinstance(node, list):
            if not node:
                return {}
            node = node[0]
        return {
            str(self._const_key(key)): self._type_descriptor(value)
            for key, value in zip(node.keys, node.values)
        }

    def _enum_variant(self, node: Any) -> dict[str, Any]:
        if isinstance(node, TupleVariant):
            return {
                "name": node.name.id,
                "kind": "unit" if not node.args else "tuple",
                "args": [self._type_descriptor(arg) for arg in node.args],
                "is_priv": node.is_priv,
            }
        if isinstance(node, StructVariant):
            return {
                "name": node.name.id,
                "kind": "struct",
                "fields": {field.name.id: self._type_descriptor(field.type) for field in node.fields},
                "is_priv": node.is_priv,
            }
        if isinstance(node, Discriminant):
            return {
                "name": node.name.id,
                "kind": "discriminant",
                "value": self._literal_value(node.value),
                "is_priv": node.is_priv,
            }
        raise IDSValueError(f"Compiler VM belum mendukung enum variant {type(node).__name__}")

    def _literal_value(self, node: Any) -> Any:
        if isinstance(node, Expression):
            return self._literal_value(node.value)
        if isinstance(node, Constant):
            return node.value
        raise IDSValueError("Discriminant enum VM sementara hanya mendukung literal")

    def _const_key(self, node: Any) -> Any:
        if isinstance(node, Constant):
            return node.value
        if isinstance(node, Name):
            return node.id
        return type(node).__name__

    def _temp(self, prefix: str) -> str:
        self._temp_id += 1
        return f"__compiler_{prefix}_{self._temp_id}"
