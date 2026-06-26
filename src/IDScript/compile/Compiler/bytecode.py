"""Official IDScript module and bytecode data structures."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from typing import Any

from .TOKEN import TOKEN


Instruction = list[Any]


@dataclass
class FunctionCode:
    """Bytecode body for one IDScript function."""

    name: str
    args: list[str]
    code: list[Instruction]
    arg_is_def: list[bool] = field(default_factory=list)

    def to_module_dict(self) -> dict[str, Any]:
        data = {"name": self.name, "args": self.args, "code": self.code}
        if any(self.arg_is_def):
            data["arg_is_def"] = self.arg_is_def
        return data

    def to_compiled_dict(self) -> dict[str, Any]:
        data = {
            "name": self.name,
            "args": self.args,
            "code": [TOKEN.encode_instruction(inst) for inst in self.code],
        }
        if any(self.arg_is_def):
            data["arg_is_def"] = self.arg_is_def
        return data

    @classmethod
    def from_module_dict(cls, data: dict[str, Any]) -> FunctionCode:
        args = list(data["args"])
        return cls(
            name=data["name"],
            args=args,
            code=list(data["code"]),
            arg_is_def=list(data.get("arg_is_def", [False] * len(args))),
        )

    @classmethod
    def from_compiled_dict(cls, data: dict[str, Any]) -> FunctionCode:
        args = list(data["args"])
        return cls(
            name=data["name"],
            args=args,
            code=[TOKEN.decode_instruction(inst) for inst in data["code"]],
            arg_is_def=list(data.get("arg_is_def", [False] * len(args))),
        )


@dataclass
class ModuleCode:
    """Compiled representation for one IDScript module and its dependencies."""

    name: str
    path: str
    code: list[Instruction] = field(default_factory=list)
    functions: dict[str, FunctionCode] = field(default_factory=dict)
    exports: list[str] = field(default_factory=list)
    modules: dict[str, ModuleCode] = field(default_factory=dict)

    def to_module_dict(self) -> dict[str, Any]:
        return {
            "format": "idsm",
            "version": 1,
            "encoding": "utf-8",
            "name": self.name,
            "path": self.path,
            "code": self.code,
            "functions": {name: fn.to_module_dict() for name, fn in self.functions.items()},
            "exports": self.exports,
            "modules": {path: module.to_module_dict() for path, module in self.modules.items()},
        }

    def to_compiled_dict(self) -> dict[str, Any]:
        return {
            "format": "idsc",
            "version": 1,
            "encoding": "utf-8",
            "name": self.name,
            "path": self.path,
            "code": [TOKEN.encode_instruction(inst) for inst in self.code],
            "functions": {name: fn.to_compiled_dict() for name, fn in self.functions.items()},
            "exports": self.exports,
            "modules": {path: module.to_compiled_dict() for path, module in self.modules.items()},
        }

    def to_module_bytes(self) -> bytes:
        payload = json.dumps(self.to_module_dict(), separators=(",", ":")).encode("utf-8")
        return TOKEN.magic("module") + payload

    def to_compiled_bytes(self) -> bytes:
        payload = json.dumps(self.to_compiled_dict(), separators=(",", ":")).encode("utf-8")
        return TOKEN.magic("compiled") + payload

    @classmethod
    def from_bytes(cls, data: bytes) -> ModuleCode:
        if data.startswith(TOKEN.magic("module")):
            payload = json.loads(data[len(TOKEN.magic("module")):].decode("utf-8"))
            return cls.from_module_dict(payload)
        if data.startswith(TOKEN.magic("compiled")):
            payload = json.loads(data[len(TOKEN.magic("compiled")):].decode("utf-8"))
            return cls.from_compiled_dict(payload)
        if data.startswith(TOKEN.magic("legacy")):
            payload = json.loads(data[len(TOKEN.magic("legacy")):].decode("utf-8"))
            return cls.from_legacy_dict(payload)
        raise ValueError("Header bytecode IDScript tidak valid")

    @classmethod
    def from_module_dict(cls, data: dict[str, Any]) -> ModuleCode:
        return cls(
            name=data["name"],
            path=data["path"],
            code=list(data["code"]),
            functions={name: FunctionCode.from_module_dict(fn) for name, fn in data["functions"].items()},
            exports=list(data["exports"]),
            modules={path: ModuleCode.from_module_dict(module) for path, module in data["modules"].items()},
        )

    @classmethod
    def from_compiled_dict(cls, data: dict[str, Any]) -> ModuleCode:
        return cls(
            name=data["name"],
            path=data["path"],
            code=[TOKEN.decode_instruction(inst) for inst in data["code"]],
            functions={name: FunctionCode.from_compiled_dict(fn) for name, fn in data["functions"].items()},
            exports=list(data["exports"]),
            modules={path: ModuleCode.from_compiled_dict(module) for path, module in data["modules"].items()},
        )

    @classmethod
    def from_legacy_dict(cls, data: dict[str, Any]) -> ModuleCode:
        return cls(
            name=data["name"],
            path=data["path"],
            code=list(data["code"]),
            functions={name: FunctionCode.from_module_dict(fn) for name, fn in data["functions"].items()},
            exports=list(data["exports"]),
            modules={path: ModuleCode.from_legacy_dict(module) for path, module in data["modules"].items()},
        )
