"""IDScript package root."""

# Compiler untuk running code/file (runtime)
from .compile.compile import Compile as InterpRun
from .compile.Compiler.__main__ import _run_bytecode_file as CompRun

# Utils
from .exceptions import __exceptions__ as Exceptions
from .compile.ids_ast import nodes as ids_ast
from .compile.parser.transformer import Parse

Interpreter = InterpreterRun = InterpRun
Compiler = CompilerRun = CompRun


__version__ = "0.1.3"
__name__ = "IDScript"
__description__ = "IDScript adalah bahasa pemrograman berbahasa Indonesia penerus Indonesian Script (IS), dengan interpreter dan compiler VM resmi."


def __getattr__(name):
    if name in ('compile', 'builtins', 'exceptions'):
        raise TypeError(f'Cannot get a private field {name!r}')
    return globals()[name]

def __setattr__(name, value):
    raise TypeError(f'Cannot set a field {name!r}')

def __delattr__(name):
    raise TypeError(f'Cannot delete a field {name!r}')

def __getitem__(key):
    return globals()['__getattr__'](key)

def __setitem__(key, value):
    return globals()['__setattr__'](key, value)

def __delitem__(key):
    return globals()['__delattr__'](key)

def __getattribute__(name):
    return globals()['__getattr__'](key)