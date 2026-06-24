"""Official readable compiler pipeline for IDScript."""

import sys
import types

from ..runtime import Compiler as _LegacyRuntimeCompiler

__all__ = [
    "BytecodeCompiler",
    "FunctionCode",
    "ModuleCode",
    "TOKEN",
    "TokenRegistry",
    "VM",
    "compile_bytecode_file",
    "compile_module_file",
    "compile_pipeline",
    "compile_source",
    "load_tokens",
    "run_bytecode",
    "run_source_direct",
]


def __getattr__(name):
    if name in {"TOKEN", "TokenRegistry", "load_tokens"}:
        from .TOKEN import TOKEN, TokenRegistry, load_tokens
        return {"TOKEN": TOKEN, "TokenRegistry": TokenRegistry, "load_tokens": load_tokens}[name]
    if name == "BytecodeCompiler":
        from .backend import BytecodeCompiler
        return BytecodeCompiler
    if name in {"FunctionCode", "ModuleCode"}:
        from .bytecode import FunctionCode, ModuleCode
        return {"FunctionCode": FunctionCode, "ModuleCode": ModuleCode}[name]
    if name == "VM":
        from .runtime import VM
        return VM
    if name in {
        "compile_bytecode_file",
        "compile_module_file",
        "compile_pipeline",
        "compile_source",
        "run_bytecode",
        "run_source_direct",
    }:
        from .api import compile_bytecode_file, compile_module_file, compile_pipeline, compile_source, run_bytecode, run_source_direct
        return {
            "compile_bytecode_file": compile_bytecode_file,
            "compile_module_file": compile_module_file,
            "compile_pipeline": compile_pipeline,
            "compile_source": compile_source,
            "run_bytecode": run_bytecode,
            "run_source_direct": run_source_direct,
        }[name]
    raise AttributeError(name)


class _CompilerPackage(types.ModuleType):
    def __getattribute__(self, name):
        if name in {"TOKEN", "TokenRegistry", "load_tokens"}:
            from .TOKEN import TOKEN, TokenRegistry, load_tokens
            return {"TOKEN": TOKEN, "TokenRegistry": TokenRegistry, "load_tokens": load_tokens}[name]
        return super().__getattribute__(name)

_parent_package = sys.modules.get(__package__.split(".")[0])
if _parent_package is not None:
    # Keep the historical API stable: `from compile import Compiler` must still
    # return the interpreter class, not this `compile.Compiler` subpackage.
    setattr(_parent_package, "Compiler", _LegacyRuntimeCompiler)

sys.modules[__name__].__class__ = _CompilerPackage
