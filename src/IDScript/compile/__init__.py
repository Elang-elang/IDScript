"""IDScript Compiler - package root.

Compiler utama adalah IDScript.compile.Compiler (VM bytecode compiler).
Compiler lama (AST interpreter) masih tersedia sebagai LegacyCompiler
untuk kompatibilitas REPL dan kode lama.
"""

from .Compiler import (
    BytecodeCompiler,
    FunctionCode,
    ModuleCode,
    VM,
    compile_bytecode_file,
    compile_module_file,
    compile_pipeline,
    compile_source,
    run_bytecode,
    run_source_direct,
)

from .entrypoint import Compile as LegacyCompile
from .parser import Parse

# Backward compatibility alias
Compile = LegacyCompile

__all__ = [
    "BytecodeCompiler",
    "FunctionCode",
    "ModuleCode",
    "VM",
    "compile_bytecode_file",
    "compile_module_file",
    "compile_pipeline",
    "compile_source",
    "run_bytecode",
    "run_source_direct",
    "LegacyCompile",
    "Parse",
]
