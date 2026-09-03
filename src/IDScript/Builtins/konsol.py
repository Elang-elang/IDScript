from IDScript.WrapperIDS.Python import *
from typing import Any
from builtins import print as _p


@Structure
class Konsol:
    pass

public_method = Konsol.Method(public=True, static=True)

@public_method
def print(sub: Any) -> None:
    _p(sub, end="", flush=True)

@public_method
def println(sub: Any) -> None:
    _p(sub, flush=True)

@public_method
def eprint(sub: Any) -> None:
    _p(f'\033[31m\033[1m[Galat]: \033[0m',      sub, end="", flush=True)

@public_method
def eprintln(sub: Any) -> None:
    _p(f'\033[31m\033[1m[Galat]: \033[0m',      sub, flush=True)

@public_method
def wprint(sub: Any) -> None:
    _p(f'\033[33m\033[1m[Peringatan]: \033[0m', sub, end="", flush=True)

@public_method
def wprintln(sub: Any) -> None:
    _p(f'\033[33m\033[1m[Peringatan]: \033[0m', sub, flush=True)

@public_method
def sprint(sub: Any) -> None:
    _p(f'\033[32m\033[1m[Sukses]: \033[0m',     sub, end="", flush=True)

@public_method
def sprintln(sub: Any) -> None:
    _p(f'\033[32m\033[1m[Sukses]: \033[0m',     sub, flush=True)

@Module
def utama(cls):
    cls.add_struct(Konsol)