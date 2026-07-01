"""Official IDScript module and bytecode data structures."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import struct
from typing import Any

from ..diagnostics import IDSValueError
from .TOKEN import TOKEN


Instruction = list[Any]


@dataclass
class FunctionCode:
    """Bytecode body for one IDScript function."""

    name: str
    args: list[str]
    code: list[Instruction]
    arg_is_def: list[bool] = field(default_factory=list)
    generic: list[str] = field(default_factory=list)

    def to_module_dict(self) -> dict[str, Any]:
        data = {"name": self.name, "args": self.args, "code": self.code}
        if any(self.arg_is_def):
            data["arg_is_def"] = self.arg_is_def
        if self.generic:
            data["generic"] = self.generic
        return data

    def to_compiled_dict(self) -> dict[str, Any]:
        data = {
            "name": self.name,
            "args": self.args,
            "code": [TOKEN.encode_instruction(inst) for inst in self.code],
        }
        if any(self.arg_is_def):
            data["arg_is_def"] = self.arg_is_def
        if self.generic:
            data["generic"] = self.generic
        return data

    @classmethod
    def from_module_dict(cls, data: dict[str, Any]) -> FunctionCode:
        args = list(data["args"])
        return cls(
            name=data["name"],
            args=args,
            code=list(data["code"]),
            arg_is_def=list(data.get("arg_is_def", [False] * len(args))),
            generic=list(data.get("generic", [])),
        )

    @classmethod
    def from_compiled_dict(cls, data: dict[str, Any]) -> FunctionCode:
        args = list(data["args"])
        return cls(
            name=data["name"],
            args=args,
            code=[TOKEN.decode_instruction(inst) for inst in data["code"]],
            arg_is_def=list(data.get("arg_is_def", [False] * len(args))),
            generic=list(data.get("generic", [])),
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
    native_symbols: dict[str, dict[str, Any]] = field(default_factory=dict)

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
            "native_symbols": self.native_symbols,
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
            "native_symbols": self.native_symbols,
        }

    def to_module_bytes(self) -> bytes:
        payload = json.dumps(self.to_module_dict(), indent=4, ensure_ascii=False).encode("utf-8")
        return TOKEN.magic("module") + payload

    def to_compiled_bytes(self) -> bytes:
        payload = _BinaryCodec.encode(self.to_compiled_dict())
        return TOKEN.magic("compiled") + payload

    @classmethod
    def from_bytes(cls, data: bytes) -> ModuleCode:
        if data.startswith(TOKEN.magic("module")):
            payload = json.loads(data[len(TOKEN.magic("module")):].decode("utf-8"))
            return cls.from_module_dict(payload)
        if data.startswith(TOKEN.magic("compiled")):
            payload = _BinaryCodec.decode(data[len(TOKEN.magic("compiled")):])
            return cls.from_compiled_dict(payload)
        raise IDSValueError("Header bytecode IDScript tidak valid")

    @classmethod
    def from_module_dict(cls, data: dict[str, Any]) -> ModuleCode:
        return cls(
            name=data["name"],
            path=data["path"],
            code=list(data["code"]),
            functions={name: FunctionCode.from_module_dict(fn) for name, fn in data["functions"].items()},
            exports=list(data["exports"]),
            modules={path: ModuleCode.from_module_dict(module) for path, module in data["modules"].items()},
            native_symbols=dict(data.get("native_symbols", {})),
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
            native_symbols=dict(data.get("native_symbols", {})),
        )



class _BinaryCodec:
    NONE = b"N"
    FALSE = b"F"
    TRUE = b"T"
    INT = b"I"
    FLOAT = b"R"
    STR = b"S"
    LIST = b"L"
    DICT = b"D"

    @classmethod
    def encode(cls, value: Any) -> bytes:
        output = bytearray()
        cls._write_value(output, value)
        return bytes(output)

    @classmethod
    def decode(cls, data: bytes) -> Any:
        value, offset = cls._read_value(data, 0)
        if offset != len(data):
            raise IDSValueError("Payload compiled IDScript memiliki byte sisa")
        return value

    @classmethod
    def _write_value(cls, output: bytearray, value: Any) -> None:
        if value is None:
            output.extend(cls.NONE)
            return
        if value is False:
            output.extend(cls.FALSE)
            return
        if value is True:
            output.extend(cls.TRUE)
            return
        if isinstance(value, int):
            data = cls._int_bytes(value)
            output.extend(cls.INT)
            cls._write_u32(output, len(data))
            output.extend(data)
            return
        if isinstance(value, float):
            output.extend(cls.FLOAT)
            output.extend(struct.pack(">d", value))
            return
        if isinstance(value, str):
            data = value.encode("utf-8")
            output.extend(cls.STR)
            cls._write_u32(output, len(data))
            output.extend(data)
            return
        if isinstance(value, list):
            output.extend(cls.LIST)
            cls._write_u32(output, len(value))
            for item in value:
                cls._write_value(output, item)
            return
        if isinstance(value, dict):
            output.extend(cls.DICT)
            cls._write_u32(output, len(value))
            for key, item in value.items():
                cls._write_value(output, key)
                cls._write_value(output, item)
            return
        raise IDSValueError(f"Nilai {value!r} tidak dapat dikompilasi ke binary IDScript")

    @classmethod
    def _read_value(cls, data: bytes, offset: int) -> tuple[Any, int]:
        if offset >= len(data):
            raise IDSValueError("Payload compiled IDScript terpotong")
        tag = data[offset : offset + 1]
        offset += 1
        if tag == cls.NONE:
            return None, offset
        if tag == cls.FALSE:
            return False, offset
        if tag == cls.TRUE:
            return True, offset
        if tag == cls.INT:
            length, offset = cls._read_u32(data, offset)
            raw, offset = cls._read_bytes(data, offset, length)
            return int.from_bytes(raw, "big", signed=True), offset
        if tag == cls.FLOAT:
            raw, offset = cls._read_bytes(data, offset, 8)
            return struct.unpack(">d", raw)[0], offset
        if tag == cls.STR:
            length, offset = cls._read_u32(data, offset)
            raw, offset = cls._read_bytes(data, offset, length)
            return raw.decode("utf-8"), offset
        if tag == cls.LIST:
            length, offset = cls._read_u32(data, offset)
            result = []
            for _ in range(length):
                item, offset = cls._read_value(data, offset)
                result.append(item)
            return result, offset
        if tag == cls.DICT:
            length, offset = cls._read_u32(data, offset)
            result = {}
            for _ in range(length):
                key, offset = cls._read_value(data, offset)
                item, offset = cls._read_value(data, offset)
                result[key] = item
            return result, offset
        raise IDSValueError(f"Tag binary IDScript {tag!r} tidak dikenal")

    @staticmethod
    def _int_bytes(value: int) -> bytes:
        length = max(1, (value.bit_length() + 8) // 8)
        while True:
            try:
                return value.to_bytes(length, "big", signed=True)
            except OverflowError:
                length += 1

    @staticmethod
    def _write_u32(output: bytearray, value: int) -> None:
        output.extend(struct.pack(">I", value))

    @staticmethod
    def _read_u32(data: bytes, offset: int) -> tuple[int, int]:
        raw, offset = _BinaryCodec._read_bytes(data, offset, 4)
        return struct.unpack(">I", raw)[0], offset

    @staticmethod
    def _read_bytes(data: bytes, offset: int, length: int) -> tuple[bytes, int]:
        end = offset + length
        if end > len(data):
            raise IDSValueError("Payload compiled IDScript terpotong")
        return data[offset:end], end
