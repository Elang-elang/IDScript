from pathlib import Path
import re
from typing import Any

from IDScript.maker import IDSFunction, IDSModule


@IDSFunction(name="cocok", declare="public", arguments={"pattern": str, "text": str}, annotation=bool)
def _cocok(pattern: str, text: str) -> bool:
    return re.match(pattern, text) is not None


@IDSFunction(name="cari", declare="public", arguments={"pattern": str, "text": str}, annotation=Any)
def _cari(pattern: str, text: str) -> Any:
    return re.search(pattern, text)


@IDSFunction(name="teks_cari", declare="public", arguments={"pattern": str, "text": str}, annotation=Any)
def _teks_cari(pattern: str, text: str) -> Any:
    match = re.search(pattern, text)
    return None if match is None else match.group(0)


@IDSFunction(name="semua", declare="public", arguments={"pattern": str, "text": str}, annotation=list)
def _semua(pattern: str, text: str) -> list:
    return re.findall(pattern, text)


@IDSFunction(name="ganti", declare="public", arguments={"pattern": str, "repl": str, "text": str}, annotation=str)
def _ganti(pattern: str, repl: str, text: str) -> str:
    return re.sub(pattern, repl, text)


@IDSFunction(name="pisah", declare="public", arguments={"pattern": str, "text": str}, annotation=list)
def _pisah(pattern: str, text: str) -> list:
    return re.split(pattern, text)


@IDSFunction(name="kompilasi", declare="public", arguments={"pattern": str}, annotation=Any)
def _kompilasi(pattern: str) -> Any:
    return re.compile(pattern)


@IDSFunction(name="escape", declare="public", arguments={"text": str}, annotation=str)
def _escape(text: str) -> str:
    return re.escape(text)


@IDSFunction(name="grup", declare="public", arguments={"match": Any, "index": Any}, annotation=Any)
def _grup(match: Any, index: Any) -> Any:
    if match is None:
        return None
    return match.group(index)


@IDSFunction(name="grup_dict", declare="public", arguments={"match": Any}, annotation=dict)
def _grup_dict(match: Any) -> dict:
    if match is None:
        return {}
    return match.groupdict()


@IDSModule(name="_Regex", path=Path(__file__).with_suffix(".idsm"))
def module(cls):
    cls.add(_cocok, _cari, _teks_cari, _semua, _ganti, _pisah, _kompilasi, _escape, _grup, _grup_dict)
    if __name__ == "__main__":
        cls.write()
