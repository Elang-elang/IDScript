import asyncio
import importlib
import inspect
from pathlib import Path
from typing import Any

from IDScript.maker import IDSFunction, IDSModule, unwrap_py_value, wrap_py_value


namespace: dict[str, Any] = {
    "asyncio": asyncio,
    "importlib": importlib,
}


class Pengingatan:
    def __init__(self, fungsi: Any, args: list[Any]):
        self.fungsi = unwrap_py_value(fungsi)
        self.args = [unwrap_py_value(arg) for arg in args]

    def jalankan(self) -> Any:
        if not callable(self.fungsi):
            raise TypeError("pengingatan membutuhkan fungsi yang dapat dipanggil")
        return self.fungsi(*self.args)

    def __await__(self):
        async def _runner():
            result = self.jalankan()
            if inspect.isawaitable(result):
                return await result
            return result

        return _runner().__await__()

    def __repr__(self) -> str:
        name = getattr(self.fungsi, "__name__", repr(self.fungsi))
        return f"<Pengingatan {name}>"


def _run_awaitable(value: Any) -> Any:
    value = unwrap_py_value(value)
    if isinstance(value, Pengingatan):
        value = value.jalankan()
    if not inspect.isawaitable(value):
        return value
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(value)

    result: dict[str, Any] = {}

    def _thread_runner() -> None:
        try:
            result["value"] = asyncio.run(value)
        except BaseException as error:
            result["error"] = error

    import threading

    thread = threading.Thread(target=_thread_runner, daemon=True)
    thread.start()
    thread.join()
    if "error" in result:
        raise result["error"]
    return result.get("value")


@IDSFunction(name="evaluasi", declare="public", arguments={"code": str}, annotation=Any)
def _evaluasi(code: str) -> Any:
    return eval(code, namespace)


@IDSFunction(name="jalankan", declare="public", arguments={"code": str}, annotation=None)
def _jalankan(code: str) -> None:
    exec(code, namespace)


@IDSFunction(name="impor", declare="public", arguments={"module": str}, annotation=Any)
def _impor(module: str) -> Any:
    value = importlib.import_module(module)
    namespace[module.split(".", 1)[0]] = value
    namespace[module.rsplit(".", 1)[-1]] = value
    return value


@IDSFunction(name="ambil", declare="public", arguments={"nama": str}, annotation=Any)
def _ambil(nama: str) -> Any:
    return namespace[nama]


@IDSFunction(name="atur", declare="public", arguments={"nama": str, "nilai": Any}, annotation=None)
def _atur(nama: str, nilai: Any) -> None:
    namespace[nama] = unwrap_py_value(nilai)


@IDSFunction(name="hapus", declare="public", arguments={"nama": str}, annotation=None)
def _hapus(nama: str) -> None:
    namespace.pop(nama, None)


@IDSFunction(name="punya", declare="public", arguments={"nama": str}, annotation=bool)
def _punya(nama: str) -> bool:
    return nama in namespace


@IDSFunction(name="daftar", declare="public", arguments={}, annotation=list)
def _daftar() -> list:
    return sorted(namespace)


@IDSFunction(name="bersihkan", declare="public", arguments={}, annotation=None)
def _bersihkan() -> None:
    namespace.clear()
    namespace["asyncio"] = asyncio
    namespace["importlib"] = importlib


@IDSFunction(name="pengingatan", declare="public", arguments={"fungsi": Any, "args": list}, annotation=Any)
def _pengingatan(fungsi: Any, args: list) -> Pengingatan:
    return Pengingatan(fungsi, args)


@IDSFunction(name="penungguan", declare="public", arguments={"nilai": Any}, annotation=Any)
def _penungguan(nilai: Any) -> Any:
    return wrap_py_value(_run_awaitable(nilai))


@IDSModule(name="_Python", path=Path(__file__).with_suffix(".idsm"))
def module(cls):
    cls.add(
        _evaluasi,
        _jalankan,
        _impor,
        _ambil,
        _atur,
        _hapus,
        _punya,
        _daftar,
        _bersihkan,
        _pengingatan,
        _penungguan,
    )
    if __name__ == "__main__":
        cls.write()
