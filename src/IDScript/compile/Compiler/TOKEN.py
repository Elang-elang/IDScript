"""Token and opcode registry for the official IDScript compiler backend."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


TOKEN_FILE = Path(__file__).with_name("TOKEN.json")


@dataclass(frozen=True)
class TokenRegistry:
    """Read-only helper around TOKEN.json.

    The registry keeps opcode numbers, file magic headers, builtin names, and
    language keywords in one place so the compiler and VM do not duplicate
    token constants.
    """

    data: dict[str, Any]

    @classmethod
    def load(cls, path: str | Path = TOKEN_FILE) -> TokenRegistry:
        return cls(json.loads(Path(path).read_text(encoding="utf-8")))

    @property
    def opcodes(self) -> dict[str, int]:
        return {name: int(code) for name, code in self.data["opcodes"].items()}

    @property
    def opcode_names(self) -> dict[int, str]:
        return {code: name for name, code in self.opcodes.items()}

    @property
    def opcode_aliases(self) -> dict[str, str]:
        return {str(alias): str(name) for alias, name in self.data.get("opcode_aliases", {}).items()}

    def canonical_opcode(self, name: str) -> str:
        return self.opcode_aliases.get(name, name)

    def opcode_code(self, name: str) -> int:
        name = self.canonical_opcode(name)
        try:
            return self.opcodes[name]
        except KeyError as exc:
            raise ValueError(f"Opcode {name!r} tidak terdaftar di TOKEN.json") from exc

    def opcode_name(self, code: int) -> str:
        try:
            return self.opcode_names[code]
        except KeyError as exc:
            raise ValueError(f"Kode opcode {code!r} tidak terdaftar di TOKEN.json") from exc

    def magic(self, format_name: str) -> bytes:
        try:
            return str(self.data["file_formats"][format_name]["magic"]).encode("utf-8")
        except KeyError as exc:
            raise ValueError(f"Format file {format_name!r} tidak terdaftar") from exc

    def encode_instruction(self, instruction: list[Any]) -> list[Any]:
        if not instruction:
            raise ValueError("Instruksi kosong tidak valid")
        return [self.opcode_code(str(instruction[0])), *(self._encode_value(item) for item in instruction[1:])]

    def decode_instruction(self, instruction: list[Any]) -> list[Any]:
        if not instruction:
            raise ValueError("Instruksi kosong tidak valid")
        return [self.opcode_name(int(instruction[0])), *(self._decode_value(item) for item in instruction[1:])]

    def _encode_value(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {key: self._encode_value(item) for key, item in value.items()}
        if isinstance(value, list):
            if value and isinstance(value[0], str) and self.canonical_opcode(value[0]) in self.opcodes:
                return self.encode_instruction(value)
            return [self._encode_value(item) for item in value]
        return value

    def _decode_value(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {key: self._decode_value(item) for key, item in value.items()}
        if isinstance(value, list):
            if value and isinstance(value[0], int) and value[0] in self.opcode_names:
                return self.decode_instruction(value)
            return [self._decode_value(item) for item in value]
        return value


TOKEN = TokenRegistry.load()


def load_tokens(path: str | Path = TOKEN_FILE) -> TokenRegistry:
    return TokenRegistry.load(path)
