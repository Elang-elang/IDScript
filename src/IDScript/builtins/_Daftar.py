from pathlib import Path
from typing import Any

from IDScript.maker import IDSFunction, IDSModule


class DaftarObj:
    def __init__(self, nilai: Any):
        self.nilai = list(nilai)

    def masukan(self, nilai: Any) -> None:
        self.nilai.append(nilai)

    def ambil(self, indeks: int) -> Any:
        return self.nilai[indeks]

    def panjang(self) -> int:
        return len(self.nilai)

    def to_list(self) -> list:
        return list(self.nilai)

    def __len__(self) -> int:
        return len(self.nilai)

    def __iter__(self):
        return iter(self.nilai)

    def __getitem__(self, indeks: int) -> Any:
        return self.nilai[indeks]

    def __repr__(self) -> str:
        return repr(self.nilai)


@IDSFunction(name="Daftar", declare="public", arguments={"nilai": Any}, annotation=Any)
def _daftar(nilai) -> DaftarObj:
    return DaftarObj(nilai)


@IDSFunction(name="adalah_daftar", declare="public", arguments={"nilai": Any}, annotation=bool)
def _adalah_daftar(nilai) -> bool:
    return isinstance(nilai, (list, DaftarObj))


@IDSModule(name="_Daftar", path=Path(__file__).with_suffix(".idsm"))
def module(cls):
    cls.add(_daftar, _adalah_daftar)
    if __name__ == "__main__":
        cls.write()
