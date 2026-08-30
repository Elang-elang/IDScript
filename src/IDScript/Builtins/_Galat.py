from pathlib import Path
from typing import Any

from IDScript.exceptions import (
    IDSError,
    IDSAttributeError,
    IDSIndexError,
    IDSKeyError,
    IDSLoopError,
    IDSMemoryError,
    IDSModuleError,
    IDSTypeError,
    IDSValueError,
)
from IDScript.maker import IDSFunction, IDSModule


@IDSFunction(name="Galat", declare="public", arguments={"message": Any}, annotation=Any)
def _galat(message) -> IDSError:
    return IDSError(message)


@IDSFunction(name="GalatTipe", declare="public", arguments={"message": Any}, annotation=Any)
def _galat_tipe(message) -> IDSTypeError:
    return IDSTypeError(message)


@IDSFunction(name="GalatNilai", declare="public", arguments={"message": Any}, annotation=Any)
def _galat_nilai(message) -> IDSValueError:
    return IDSValueError(message)


@IDSFunction(name="GalatAtribut", declare="public", arguments={"message": Any}, annotation=Any)
def _galat_atribut(message) -> IDSAttributeError:
    return IDSAttributeError(message)


@IDSFunction(name="GalatIndeks", declare="public", arguments={"message": Any}, annotation=Any)
def _galat_indeks(message) -> IDSIndexError:
    return IDSIndexError(message)


@IDSFunction(name="GalatKunci", declare="public", arguments={"message": Any}, annotation=Any)
def _galat_kunci(message) -> IDSKeyError:
    return IDSKeyError(message)


@IDSFunction(name="GalatModul", declare="public", arguments={"message": Any}, annotation=Any)
def _galat_modul(message) -> IDSModuleError:
    return IDSModuleError(message)


@IDSFunction(name="GalatLoop", declare="public", arguments={"message": Any}, annotation=Any)
def _galat_loop(message) -> IDSLoopError:
    return IDSLoopError(message)


@IDSFunction(name="GalatMemori", declare="public", arguments={"message": Any}, annotation=Any)
def _galat_memori(message) -> IDSMemoryError:
    return IDSMemoryError(message)


@IDSModule(name="_Galat", path=Path(__file__).with_suffix(".idsm"))
def module(cls):
    cls.add(
        _galat,
        _galat_tipe,
        _galat_nilai,
        _galat_atribut,
        _galat_indeks,
        _galat_kunci,
        _galat_modul,
        _galat_loop,
        _galat_memori,
    )
    if __name__ == "__main__":
        cls.write()
