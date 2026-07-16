import sys
from pathlib import Path
from typing import Any

from IDScript.maker import IDSFunction, IDSModule


@IDSFunction(name="format", arguments={"text": Any, "args": list}, annotation=str)
def _format(text, args: list) -> str:
    return str(text).format(*args)


@IDSFunction(name="print", arguments={"text": Any}, annotation=None)
def _print(text) -> None:
    sys.stdout.write(str(text))


@IDSFunction(name="println", arguments={"text": Any}, annotation=None)
def _println(text) -> None:
    sys.stdout.write(f"{text}\n")


@IDSFunction(name="eprint", arguments={"text": Any}, annotation=None)
def _eprint(text) -> None:
    sys.stderr.write(str(text))


@IDSFunction(name="eprintln", arguments={"text": Any}, annotation=None)
def _eprintln(text) -> None:
    sys.stderr.write(f"{text}\n")


@IDSFunction(name="input_teks", arguments={}, annotation=str)
def _input_teks() -> str:
    return sys.stdin.readline().strip()


@IDSModule(name="Konsol", path=Path(__file__).with_suffix(".idsm"))
def module(cls):
    cls.add(_format, _print, _println, _eprint, _eprintln, _input_teks)
    if __name__ == "__main__":
        cls.write()
