from pathlib import Path
from typing import Any

from IDScript.maker import IDSFunction, IDSModule


@IDSFunction(name="ambil_atribut", declare="public", arguments={"obj": Any, "nama": str}, annotation=Any)
def _ambil_atribut(obj, nama: str) -> Any:
    return getattr(obj, nama)


@IDSFunction(name="atur_atribut", declare="public", arguments={"obj": Any, "nama": str, "nilai": Any}, annotation=None)
def _atur_atribut(obj, nama: str, nilai) -> None:
    setattr(obj, nama, nilai)


@IDSFunction(name="punya_atribut", declare="public", arguments={"obj": Any, "nama": str}, annotation=bool)
def _punya_atribut(obj, nama: str) -> bool:
    return hasattr(obj, nama)


@IDSFunction(name="punya_attr", declare="public", arguments={"obj": Any, "nama": str}, annotation=bool)
def _punya_attr(obj, nama: str) -> bool:
    return hasattr(obj, nama)


@IDSFunction(name="hapus_atribut", declare="public", arguments={"obj": Any, "nama": str}, annotation=None)
def _hapus_atribut(obj, nama: str) -> None:
    delattr(obj, nama)


@IDSFunction(name="daftar_atribut", declare="public", arguments={"obj": Any}, annotation=list)
def _daftar_atribut(obj) -> list:
    return dir(obj)


@IDSModule(name="_Atribut", path=Path(__file__).with_suffix(".idsm"))
def module(cls):
    cls.add(
        _ambil_atribut,
        _atur_atribut,
        _punya_atribut,
        _punya_attr,
        _hapus_atribut,
        _daftar_atribut,
    )
    if __name__ == "__main__":
        cls.write()
