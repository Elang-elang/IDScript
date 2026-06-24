"""Builtin functions and builtin type names available to IDScript programs."""

import typing as T
from .runtime.types import check_types
import builtins
import sys
from typing import Any


"> Bases builtin "

class Builtin:
    def __init__(self): pass
    def __repr__(self): return f"<Builtin <{type(self).__name__}>>"

class Format(Builtin):
    @staticmethod
    def __call__(text: Any, *args):
        return str(text).format(*args)

class Print(Builtin):
    @staticmethod
    def __call__(text: str, *args) -> None:
        sys.stdout.write(str(text).format(*args))
        return None

class Println(Builtin):
    @staticmethod
    def __call__(text: str, *args) -> None:
        sys.stdout.write((str(text) + "\n").format(*args))
        return None

class EPrint(Builtin):
    @staticmethod
    def __call__(text: str, *args) -> None:
        sys.stderr.write(str(text).format(*args))
        return None

class EPrintln(Builtin):
    @staticmethod
    def __call__(text: str, *args) -> None:
        sys.stderr.write((str(text) + "\n").format(*args))
        return None

class Input(Builtin):
    @staticmethod
    def __call__(expected_type: T.Type) -> T.Any:
        text = input().strip()
        res = expected_type(text)
    
        check_types(res, expected_type)
        return res

ALL = [
    # Functions
    ("format",   T.Callable[..., str],    Format()),
    ("print",    T.Callable[..., None],    Print()),
    ("println",  T.Callable[..., None],  Println()),
    ("eprint",   T.Callable[..., None],   EPrint()),
    ("eprintln", T.Callable[..., None], EPrintln()),
    ("input",    T.Callable[..., T.Any],   Input()),
    ("Galat",    T.Type,                 Exception),
    
    # Types
    ("Teks",      T.Type,        str),
    ("Angka",     T.Type,        int),
    ("Float",     T.Type,      float),
    ("Boolean",   T.Type,       bool),
    ("Kosong",    T.Type, type(None)),
    ("Apapun",    T.Type,      T.Any),
    ("OBJEK",     T.Type,     object),
    
    # Keyword boolean
    ("benar",   bool,       True),
    ("salah",   bool,      False),
    ("kosong",  type(None), None),
]


def GLOBAL(
    global_scope: Any,
    name: str,
    value: Any,
    private: bool = True,
    /,
)-> None:
    global_scope.declare(
        name,
        Any,
        value,
        True,
        private
    )
    
def LOCAL(
    current_scope: Any,
    name: str,
    value: Any,
    /,
)-> None:
    current_scope.declare(
        name,
        Any,
        value,
        False,
    )
