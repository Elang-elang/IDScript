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


@Structure
class Tekstual:
    string: str

public_method = Tekstual.Method(public=True)

@Tekstual.Method(public=True, static=True)
def inisiasi(string: str, /) -> Tekstual:
    return Tekstual(string=string)

@public_method
def kapitalisme(cls: Tekstual) -> Tekstual:
    return Tekstual.inisiasi(cls.string.capitalize())

@public_method
def tengahkan(cls: Tekstual, width: int, fillchar: str) -> Tekstual:
    if len(fillchar) > 1:
        raise TypeError(f'Kami membutuh karakter bukan text')
    return Tekstual.inisiasi(cls.string.center(width, fillchar))

@public_method
def hitung(cls: Tekstual, text: str) -> int:
    return cls.string.count(text)

@public_method
def enkode(cls: Tekstual, encoding: str) -> Any:
    from bitetual import Bitetual
    return Bitetual.inisiasi(cls.string.encode(encoding))

@public_method
def berakhiran(cls: Tekstual, text: str) -> Kondisi:
    return Kondisi.inisiasi(int(cls.string.endswith(text)))

@public_method
def berawalan(cls: Tekstual, text: str) -> Kondisi:
    return Kondisi.inisiasi(cls.string.startswith(text))

@public_method
def cari(cls: Tekstual, text: str, start: int, end: int) -> int:
    return cls.string.find(text, start, end)

@public_method
def format(cls: Tekstual, subject: Any) -> Tekstual:
    res = cls.string.format(subject)
    if res == cls.string:
        raise TypeError(f'Harus menggunakan format {{}} pada string agar terbaca. contoh `Tekstual("a = {{}}").format(1)`')
    
    return Tekstual.inisiasi(res)

@public_method
def format_daftar(cls: Tekstual, subject: Daftar) -> Tekstual:
    daftar_iter = subject.iteratorPy()
    res = cls.string.format(*daftar_iter)
    if res == cls.string:
        raise TypeError(f'Harus menggunakan format {{}} pada string agar terbaca. contoh `Tekstual("a = {{}}").format(1)`')

    return Tekstual.inisiasi(res)

@public_method
def indeks(cls: Tekstual, text: str, start: int, end: int) -> int:
    return cls.string.index(text, start, end)

@public_method
def gabungkan(cls: Tekstual, values: Daftar) -> Tekstual:
    daftar_iter = values.iteratorPy()
    new_iter    = []
    for value in daftar_iter:
        if isinstance(value, str):
            new_iter.append(value)
        elif isinstance(value, Tekstual):
            new_iter.append(value.ke_teks())
        else:
            raise TypeError(f'Isi daftar harus berupa Teks atau Tekstual')
        
    return Tekstual.inisiasi(cls.string.join(new_iter))

@public_method
def kapitilkan(cls: Tekstual) -> Tekstual:
    return Tekstual.inisiasi(cls.string.lower())

@public_method
def kapitalkan(cls: Tekstual) -> Tekstual:
    return Tekstual.inisiasi(cls.string.upper())

@public_method
def perubahan(cls: Tekstual, old: str, new: str) -> Tekstual:
    return Tekstual.inisiasi(cls.string.replace(old, new))

@public_method
def ada_angka(cls: Tekstual) -> Kondisi:
    return Kondisi.inisiasi(cls.string.isalnum())

@public_method
def merupakan_abjad(cls: Tekstual) -> Kondisi:
    return Kondisi.inisiasi(cls.string.isalpha())

@public_method
def merupakan_ascii(cls: Tekstual) -> Kondisi:
    return Kondisi.inisiasi(cls.string.isascii())

@public_method
def merupakan_desimal(cls: Tekstual) -> Kondisi:
    return Kondisi.inisiasi(cls.string.isdecimal())

@public_method
def merupakan_identifier(cls: Tekstual) -> Kondisi:
    return Kondisi.inisiasi(cls.string.isidentifier())

@public_method
def merupakan_digit(cls: Tekstual) -> Kondisi:
    return Kondisi.inisiasi(cls.string.isdigit())

@public_method
def merupakan_angka(cls: Tekstual) -> Kondisi:
    return Kondisi.inisiasi(cls.string.isnumberic())

@public_method
def dapat_tertulis(cls: Tekstual) -> Kondisi:
    return Kondisi.inisiasi(cls.string.isprintable())

@public_method
def merupakan_spasi(cls: Tekstual) -> Kondisi:
    return Kondisi.inisiasi(cls.string.isspace())

@public_method
def merupakan_judul(cls: Tekstual) -> Kondisi:
    return Kondisi.inisiasi(cls.string.istitle())

@public_method
def merupakan_kapitil(cls: Tekstual) -> Kondisi:
    return Kondisi.inisiasi(cls.string.islower())

@public_method
def merupakan_kapital(cls: Tekstual) -> Kondisi:
    return Kondisi.inisiasi(cls.string.iskapital())



@public_method
def tulisan(cls: Tekstual) -> str:
    return f'Tekstual("{cls.string}")'
    
@public_method
def ke_teks(cls: Tekstual) -> str:
    return cls.string

@public_method
def panjang(cls: Tekstual) -> int:
    return len(cls.string)

@Tekstual.Method
def ambil_item(cls: Tekstual, index: int) -> Any:
    return cls.string[index]

@Tekstual.Method
def atur_item(cls: Tekstual, index: int, value: str) -> Any:
    cls.string[index] = value


@Module
def utama(cls) -> None:
    cls.add_struct(Tekstual)