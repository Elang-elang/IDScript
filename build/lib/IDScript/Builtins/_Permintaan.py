from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    import pip
    pip.main(["install", "requests"])

from IDScript.maker import IDSFunction, IDSModule, unwrap_py_value


def _options(opsi: Any) -> dict[str, Any]:
    if opsi is None:
        return {}
    opsi = unwrap_py_value(opsi)
    if not isinstance(opsi, dict):
        raise TypeError("opsi permintaan harus berupa kamus")
    return dict(opsi)


@IDSFunction(name="minta", declare="public", arguments={"method": str, "url": str, "opsi": dict}, annotation=Any)
def _minta(method: str, url: str, opsi: dict) -> Any:
    return requests.request(method, url, **_options(opsi))


@IDSFunction(name="ambil", declare="public", arguments={"url": str, "opsi": dict}, annotation=Any)
def _ambil(url: str, opsi: dict) -> Any:
    return requests.get(url, **_options(opsi))


@IDSFunction(name="kirim", declare="public", arguments={"url": str, "opsi": dict}, annotation=Any)
def _kirim(url: str, opsi: dict) -> Any:
    return requests.post(url, **_options(opsi))


@IDSFunction(name="taruh", declare="public", arguments={"url": str, "opsi": dict}, annotation=Any)
def _taruh(url: str, opsi: dict) -> Any:
    return requests.put(url, **_options(opsi))


@IDSFunction(name="tambal", declare="public", arguments={"url": str, "opsi": dict}, annotation=Any)
def _tambal(url: str, opsi: dict) -> Any:
    return requests.patch(url, **_options(opsi))


@IDSFunction(name="hapus", declare="public", arguments={"url": str, "opsi": dict}, annotation=Any)
def _hapus(url: str, opsi: dict) -> Any:
    return requests.delete(url, **_options(opsi))


@IDSFunction(name="teks", declare="public", arguments={"response": Any}, annotation=str)
def _teks(response: Any) -> str:
    return unwrap_py_value(response).text


@IDSFunction(name="json", declare="public", arguments={"response": Any}, annotation=Any)
def _json(response: Any) -> Any:
    return unwrap_py_value(response).json()


@IDSFunction(name="status", declare="public", arguments={"response": Any}, annotation=int)
def _status(response: Any) -> int:
    return int(unwrap_py_value(response).status_code)


@IDSFunction(name="header", declare="public", arguments={"response": Any}, annotation=dict)
def _header(response: Any) -> dict:
    return dict(unwrap_py_value(response).headers)


@IDSFunction(name="url", declare="public", arguments={"response": Any}, annotation=str)
def _url(response: Any) -> str:
    return str(unwrap_py_value(response).url)


@IDSFunction(name="berhasil", declare="public", arguments={"response": Any}, annotation=bool)
def _berhasil(response: Any) -> bool:
    return bool(unwrap_py_value(response).ok)


@IDSModule(name="_Permintaan", path=Path(__file__).with_suffix(".idsm"))
def module(cls):
    cls.add(_minta, _ambil, _kirim, _taruh, _tambal, _hapus, _teks, _json, _status, _header, _url, _berhasil)
    if __name__ == "__main__":
        cls.write()
