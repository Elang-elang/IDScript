from pathlib import Path
from typing import Any

from IDScript.maker import IDSFunction, IDSModule


@IDSFunction(name="panjang", declare="public", arguments={"nilai": Any}, annotation=int)
def _panjang(nilai) -> int:
    return len(nilai)


@IDSFunction(name="jangkauan", declare="public", arguments={"args": list}, annotation=list)
def _jangkauan(args: list) -> list:
    if len(args) == 1:
        return list(range(args[0] + 1))
    return list(range(*args))


@IDSModule(name="_Iterasi", path=Path(__file__).with_suffix(".idsm"))
def module(cls):
    cls.add(_panjang, _jangkauan)
    if __name__ == "__main__":
        cls.write()
