import sys
from pathlib import Path
from typing import Any

from IDScript.maker import IDSFunction, IDSModule
from IDScript.compile.exceptions import _paint

kind = _paint("kesalahan", "bold", "red")
error_text = f"error[{kind}]: "

@IDSFunction(name="format", arguments={"text": Any, "args": list}, annotation=str)
def _format(text, args: list) -> str:
    return str(text).format(*args)


@IDSFunction(name="print", arguments={"text": Any}, annotation=None)
def _print(text) -> None:
    print(text, flush=True, end='')


@IDSFunction(name="println", arguments={"text": Any}, annotation=None)
def _println(text) -> None:
    print(text, flush=True)


@IDSFunction(name="eprint", arguments={"text": Any}, annotation=None)
def _eprint(text) -> None:
    print(f'{error_text}{str(text)}', flush=True, end='')


@IDSFunction(name="eprintln", arguments={"text": Any}, annotation=None)
def _eprintln(text) -> None:
    print(f'{error_text}{str(text)}', flush=True)


@IDSFunction(name="input_teks", arguments={}, annotation=str)
def _input_teks() -> str:
    return sys.stdin.readline().strip()


@IDSModule(name="Konsol", path=Path(__file__).with_suffix(".idsm"))
def module(cls):
    cls.add(_format, _print, _println, _eprint, _eprintln, _input_teks)
    if __name__ == "__main__":
        cls.write()
