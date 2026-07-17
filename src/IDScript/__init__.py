"""IDScript package root."""

# Compiler utama — VM bytecode compiler + runtime (default)
from .compile import (
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

# Legacy interpreter (masih dipakai REPL, tidak disarankan untuk kode baru)
from .compile import LegacyCompile as Interpreter

# Utils
from .compile import Parse
from .compile import exceptions as Exceptions
from .compile.ids_ast import nodes as IDSNodes

from . import maker

Maker = maker

__version__ = "0.1.7"
__name__ = "IDScript"
__doc__ = "IDScript adalah bahasa pemrograman berbahasa Indonesia penerus Indonesian Script (IS), dengan interpreter dan compiler VM resmi."
