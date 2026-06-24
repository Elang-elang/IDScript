"""Public API for the official IDScript compiler pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .backend import BytecodeCompiler
from .bytecode import ModuleCode
from .runtime import VM


def compile_source(code: str, file: str | Path = "<memory.ids>") -> ModuleCode:
    return BytecodeCompiler().compile_source(code, file)


def compile_module_file(file: str | Path, output: str | Path | None = None) -> ModuleCode:
    source = Path(file)
    module = BytecodeCompiler().compile_file(source)
    if output is not None:
        Path(output).write_bytes(module.to_module_bytes())
    return module


def compile_bytecode_file(
    file: str | Path,
    output: str | Path | None = None,
    module_output: str | Path | None = None,
) -> ModuleCode:
    source = Path(file)
    module = compile_module_file(source, module_output or source.with_suffix(".idsm"))
    Path(output or source.with_suffix(".idsc")).write_bytes(module.to_compiled_bytes())
    return module


def compile_pipeline(file: str | Path, main: str = "utama", run: bool = True) -> Any:
    source = Path(file)
    compile_bytecode_file(source)
    if not run:
        return None
    return run_bytecode(source.with_suffix(".idsc"), main)


def run_source_direct(file: str | Path, main: str = "utama") -> Any:
    module = BytecodeCompiler().compile_file(file)
    return VM(module).run(main)


def run_bytecode(file: str | Path, main: str = "utama") -> Any:
    return VM(ModuleCode.from_bytes(Path(file).read_bytes())).run(main)
