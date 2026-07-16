from pathlib import Path
from typing import Any

from IDScript.maker import IDSFunction, IDSModule


@IDSFunction(name="panjang", arguments={"nilai": Any}, annotation=int)
def _panjang(nilai) -> int:
    return len(nilai)


@IDSFunction(name="jangkauan", arguments={"args": list}, annotation=list)
def _jangkauan(args: list) -> list:
    if len(args) == 1:
        return list(range(args[0] + 1))
    return list(range(*args))

@IDSFunction(name="bungkus_argumen", arguments={"func": Any}, annotation=Any)
def _bungkus_argumen(func: Any) -> Any:
    def pembungkusan_argumen(*args):
        return func(*args)
    return pembungkusan_argumen


@IDSModule(name="Iterasi", path=Path(__file__).with_suffix(".idsm"))
def module(cls):
    cls.add(_panjang, _jangkauan, _bungkus_argumen)
    if __name__ == "__main__":
        cls.write()
