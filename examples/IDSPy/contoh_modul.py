"""Contoh IDSPy: Membuat modul IDScript dengan Maker API."""
from pathlib import Path
from IDScript.maker import IDSFunction, IDSModule


@IDSFunction(name="salam", declare="public", arguments={"nama": str}, annotation=str)
def _salam(nama: str) -> str:
    return f"Halo, {nama}!"


@IDSFunction(name="tambah", declare="public", arguments={"a": int, "b": int}, annotation=int)
def _tambah(a: int, b: int) -> int:
    return a + b


@IDSFunction(name="kali", declare="public", arguments={"a": int, "b": int}, annotation=int)
def _kali(a: int, b: int) -> int:
    return a * b


@IDSFunction(name="gabung", declare="public", arguments={"items": list}, annotation=str)
def _gabung(items: list) -> str:
    return ", ".join(str(i) for i in items)


@IDSModule(name="ContohIDSPy", path=Path(__file__).with_suffix(".idsm"))
def module(cls):
    cls.add(_salam, _tambah, _kali, _gabung)
    cls.declare("VERSI", str, "1.0.0", declare="public")
    if __name__ == "__main__":
        cls.write()
        print(f"Modul {cls.name} ditulis: {cls.path}")
