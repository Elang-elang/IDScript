from IDScript.WrapperIDS.Python import *
from typing import Any
from pathlib import Path
import importlib.util


def get_module(name: str, path: Path):
    path = Path(__file__).parent / path

    spec   = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

Daftar = get_module("daftar", Path("../daftar.py")).Daftar
Kondisi = get_module("boolean", Path("../boolean.py")).Kondisi


b = lambda s: s.encode()

@Structure
class Bitetual:
    string: bytes

public_method = Bitetual.Method(public=True)

@Bitetual.Method(public=True, static=True)
def inisiasi(string: str | bytes, /) -> Bitetual:
    if isinstance(string, str):
        string = b(string)
    return Bitetual(string=string)

@public_method
def kapitalisme(cls: Bitetual) -> Bitetual:
    return Bitetual.inisiasi(cls.string.capitalize())

@public_method
def tengahkan(cls: Bitetual, width: int, fillchar: str) -> Bitetual:
    if len(fillchar) > 1:
        raise TypeError(f'Kami membutuh karakter bukan text')
    return Bitetual.inisiasi(cls.string.center(width, b(fillchar)))

@public_method
def hitung(cls: Bitetual, text: str) -> int:
    return cls.string.count(b(text))

@public_method
def dekode(cls: Bitetual, encoding: str) -> Any:
    from tekstual import Tekstual
    return Tekstual.inisiasi(cls.string.decode(encoding))

@public_method
def berakhiran(cls: Bitetual, text: str) -> Kondisi:
    return Kondisi.inisiasi(cls.string.endswith(b(text)))

@public_method
def berawalan(cls: Bitetual, text: str) -> Kondisi:
    return Kondisi.inisiasi(cls.string.startswith(b(text)))

@public_method
def cari(cls: Bitetual, text: str, start: int, end: int) -> int:
    return cls.string.find(b(text), start, end)

@public_method
def indeks(cls: Bitetual, text: str, start: int, end: int) -> int:
    return cls.string.index(b(text), start, end)

@public_method
def gabungkan(cls: Bitetual, values: Daftar) -> Bitetual:
    from tekstual import Tekstual
    daftar_iter = values.iteratorPy()
    new_iter  = []
    for value in daftar_iter:
        if isinstance(value, str):
            new_iter.append(b(value))
        
        elif isinstance(value, Tekstual):
            new_iter.append(b(value.ke_teks()))
        elif isinstance(value, Bitetual):
            new_iter.append(b(value.ke_teks()))
        else:
            raise TypeError(f'Isi daftar harus berupa Teks, Tekstual atau Bitetual')
        
    
    return Bitetual.inisiasi(cls.string.join(new_iter))

@public_method
def kapitilkan(cls: Bitetual) -> Bitetual:
    return Bitetual.inisiasi(cls.string.lower())

@public_method
def kapitalkan(cls: Bitetual) -> Bitetual:
    return Bitetual.inisiasi(cls.string.upper())

@public_method
def perubahan(cls: Bitetual, old: str, new: str) -> Bitetual:
    return Bitetual.inisiasi(cls.string.replace(b(old), b(new)))

@public_method
def ada_angka(cls: Bitetual) -> Kondisi:
    return Kondisi.inisiasi(cls.string.isalnum())

@public_method
def merupakan_abjad(cls: Bitetual) -> Kondisi:
    return Kondisi.inisiasi(cls.string.isalpha())

@public_method
def merupakan_ascii(cls: Bitetual) -> Kondisi:
    return Kondisi.inisiasi(cls.string.isascii())

@public_method
def merupakan_digit(cls: Bitetual) -> Kondisi:
    return Kondisi.inisiasi(cls.string.isdigit())

@public_method
def merupakan_spasi(cls: Bitetual) -> Kondisi:
    return Kondisi.inisiasi(cls.string.isspace())

@public_method
def merupakan_judul(cls: Bitetual) -> Kondisi:
    return Kondisi.inisiasi(cls.string.istitle())

@public_method
def merupakan_kapitil(cls: Bitetual) -> Kondisi:
    return Kondisi.inisiasi(cls.string.islower())

@public_method
def merupakan_kapital(cls: Bitetual) -> Kondisi:
    return Kondisi.inisiasi(cls.string.iskapital())


@public_method
def tulisan(cls: Bitetual) -> str:
    writer = str(cls.string)[2:-1]
    return f'Bitetual("{writer}")'
    
@public_method
def ke_teks(cls: Bitetual) -> str:
    return str(cls.string)[2:-1]

@public_method
def panjang(cls: Bitetual) -> int:
    return len(cls.string)

@Bitetual.Method
def ambil_item(cls: Bitetual, index: int) -> Any:
    return cls.string[index]

@Bitetual.Method
def atur_item(cls: Bitetual, index: int, value: str) -> Any:
    cls.string[index] = value



@Module
def utama(cls) -> None:
    cls.add_struct(Bitetual)