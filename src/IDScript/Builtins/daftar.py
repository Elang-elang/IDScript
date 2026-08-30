from IDScript.WrapperIDS.Python import *
from typing import Any


def resolver_index(index, values):
        index += 1
        while index < 0:
            index = len(values) + 1 - index
        return index


@Structure
class Daftar:
    values: Any
    frozen: int | bool
    const_length: int



@Daftar.Method(static=True, public=True)
def inisiasi(const_length: int = 0) -> Daftar:
    return Daftar(values=[], const_length=const_length, frozen=0)


@Daftar.Method(public=True)
def masukkan(ini: Daftar, value: Any, index: int = -1) -> None:
    if bool(ini.frozen) is True:
        raise ValueError(f'Sudah ditetapkan')

    index = resolver_index(index, ini.values)
    if bool(ini.const_length) is True:
        if index >= ini.const_length:
            raise IndexError(f'Panjang telah ditetapkan')
    
    ini.values.insert(index, value)

@Daftar.Method(public=True)
def bersihkan(ini: Daftar) -> None:
    if bool(ini.frozen):
        raise ValueError(f'Sudah ditetapkan')

    ini.values.clear()

@Daftar.Method(public=True)
def pop(ini: Daftar, index: int = -1) -> Any:
    if bool(ini.frozen):
        raise ValueError(f'Sudah ditetapkan')

    return ini.values.pop(index)

@Daftar.Method(public=True)
def sortir(ini: Daftar, reversed: int = 0) -> None:
    if bool(ini.frozen):
        raise ValueError(f'Sudah ditetapkan')
        
    ini.values.sort(reversed=int(reversed))

@Daftar.Method(public=True)
def atur_tetap(ini: Daftar) -> None:
    if int(ini.frozen):
        print(f'Peringatan: daftar ini telah dari awal sudah di frozen (tetap)')
    ini.frozen = 1
    



@Daftar.Method
def ambil_item(ini: Daftar, index: int) -> Any:
    return ini.values[index]

@Daftar.Method
def atur_item(ini: Daftar, index: int, value: Any) -> None:
    if bool(ini.frozen):
        raise ValueError(f'Sudah ditetapkan')
    
    ini.values[index] = value

@Daftar.Method
def termasuk(ini: Daftar, value: Any) -> int:
    return int(value in ini.values)

@Daftar.Method(public=True)
def panjang(ini: Daftar) -> int:
    return len(ini.values)

@Daftar.Method
def cek_jangkauan(ini: Daftar, jangkauan: Any) -> int:
    res = [isinstance(ini.values, jangkauan)]
    if not all(res): return 0

    res.append(ini.frozen is jangkauan.frozen)
    res.append(ini.length is jangkauan.length)
    return int(all(res))



@Daftar.Method
def tulisan(ini: Daftar) -> str:
    new_v = []
    for v in ini.values:
        if v is ini.values:
            new_v.append('[ ... ]')
        if v is None:
            new_v.append('...')
        else:
            new_v.append(repr(v))
    
    writer = f'[ {", ".join(new_v)} ]'
    return writer if not ini.frozen else f'Tetap({writer})'


@Module
def utama(cls) -> None:
    cls.add_struct(Daftar)