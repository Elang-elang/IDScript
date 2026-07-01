from pathlib import Path
from typing import Any

from IDScript.maker import IDSFunction, IDSModule


class KamusObj:
    def __init__(self, nilai: Any):
        self.nilai = dict(nilai)

    def atur(self, kunci: Any, nilai: Any) -> None:
        self.nilai[kunci] = nilai

    def ambil(self, kunci: Any) -> Any:
        return self.nilai[kunci]

    def punya(self, kunci: Any) -> bool:
        return kunci in self.nilai

    def __dict__(self) -> dict:
        return dict(self.nilai)

    def __len__(self) -> int:
        return len(self.nilai)

    def __iter__(self):
        return iter(self.nilai)

    def __getitem__(self, kunci: Any) -> Any:
        return self.nilai[kunci]

    def __setitem__(self, kunci: Any, nilai: Any) -> None:
        self.nilai[kunci] = nilai

    def __repr__(self) -> str:
        return repr(self.nilai)


@IDSFunction(name="Kamus", declare="public", arguments={"nilai": Any}, annotation=Any)
def _kamus(nilai) -> KamusObj:
    return KamusObj(nilai)


@IDSFunction(name="adalah_kamus", declare="public", arguments={"nilai": Any}, annotation=bool)
def _adalah_kamus(nilai) -> bool:
    return isinstance(nilai, (dict, KamusObj))


@IDSModule(name="_Kamus", path=Path(__file__).with_suffix(".idsm"))
def module(cls):
    cls.add(_kamus, _adalah_kamus)
    if __name__ == "__main__":
        cls.write()
