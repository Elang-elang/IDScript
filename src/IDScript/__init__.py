<<<<<<< HEAD
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

__version__ = "0.1.7"
__name__ = "IDScript"
__doc__ = "IDScript adalah bahasa pemrograman berbahasa Indonesia penerus Indonesian Script (IS), dengan interpreter dan compiler VM resmi."
=======
from .interpreter        import Compile
#from .type_checker import TypeChecker
from .properties._Reprer import Reprer
from .                   import TOKEN as IDVMToken

@Reprer(writer='Grammar<IDScript>')
class Grammar:
    def __new__(cls) -> str:
        from pathlib import Path
        resolve_path = Path(__file__).parent / 'gramm.lark'
        return resolve_path.read_text()

del Reprer
>>>>>>> 3bedd79 (Update from Alternative and the new update)
