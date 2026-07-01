"""IDScript package root."""

# Compiler untuk running code/file (runtime)
from .compile.compile import Compile as Interpreter
from .compile.Compiler.__main__ import _run_bytecode_file as Compiler

# Utils
from .compile import exceptions as Exceptions
from .compile.ids_ast import nodes as IDSNodes
from .compile.parser.transformer import Parse

from . import maker
Maker = maker

globals().pop('compile')

__version__ = "0.1.5b4"
__name__ = "IDScript"
__doc__ = "IDScript adalah bahasa pemrograman berbahasa Indonesia penerus Indonesian Script (IS), dengan interpreter dan compiler VM resmi."
