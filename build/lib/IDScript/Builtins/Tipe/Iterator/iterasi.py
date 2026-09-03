from IDScript.WrapperIDS.Python import *
from typing import Any, List

def resolver_index(index, values):
        index += 1
        while index < 0:
            index = len(values) + 1 - index
        return index


@Structure
class Iterasi:
    iterator: List[Any]
    length: int
    type: Any

public  = Iterasi.Method(public=True)
private = Iterasi.Method

@Iterasi.Method(public=True, static=True)
def inisiasi(length: int) -> Iterasi:
    return Iterasi(iterator=[], length=length, type=0)

@public
def masukkan(ini: Iterasi, index: int, value: Any) -> None:
    if ini.type is 0:
        t_value = type(value)
        ini.type = t_value

    if not isinstance(value, ini.type):
        raise TypeError(f'Harus mengikuti tipe dari isian pertama {ini.type}')

    index = resolver_index(index, ini.iterator)
    if index > ini.length and ini.length != -1:
        raise IndexError(f'Panjang telah ditetapkan {ini.length}. Namun melebihi dan menjadi {index + 1}')

    ini.iterator.insert(index, value)

@public
def ambilkan(ini: Iterasi, index: int) -> Any:
    index = resolver_index(index, ini.iterator)
    if index < ini.length:
        return ini.iterator[index]
    return 0

@public
def hapus_isi(ini: Iterasi, value: Any) -> None:
    if not isinstance(value, ini.type):
        raise TypeError(f'Harus mengikuti tipe dari isian pertama {ini.type}')
    ini.iterator.remove(value)

@public
def pemetaan(ini: Iterasi, func: Any) -> None:
    for value in ini.iterator:
        func(value)

@public
def pemetaan_indeks(ini: Iterasi, func: Any) -> None:
    for i, value in enumerate(ini.iterator):
        func(i, value)


@public
def bersihkan(ini: Iterasi) -> None:
    ini.iterator.clear()

@public
def sortir(ini: Iterasi, reversed: int | bool = 0) -> None:
    ini.iterator.sort(bool(reversed))

@public
def ambil_item(ini: Iterasi, index: int) -> Any:
    try:
        return ini.iterator[index]
    except IndexError:
        raise IndexError(f'Panjang telah ditetapkan {ini.length}. Namun melebihi dan menjadi {index + 1}')

@public
def atur_item(ini: Iterasi, index: int, value: Any) -> None:
    try:
        if ini.type is None or not ini.iterator:
            return ini.masukkan(index, value)
        
        if not isinstance(value, ini.type):
            raise TypeError(f'Harus mengikuti tipe dari isian pertama {ini.type}')
        
        ini.iterator[index] = value
    except IndexError:
        raise IndexError(f'Panjang telah ditetapkan {ini.length}. Namun melebihi dan menjadi {index + 1}')

@public
def hapus_item(ini: Iterasi, index: int) -> None:
    try:
        del ini.iterator[index]
    except IndexError:
        raise IndexError(f'Panjang telah ditetapkan {ini.length}. Namun melebihi dan menjadi {index + 1}')

@public
def termasuk(ini: Iterasi, value: Any) -> int:
    return int(value in ini.iterator)

@public
def panjang(ini: Iterasi) -> int:
    return len(ini.iterator)

@public
def tulisan(ini: Iterasi) -> str:
    return f'Iterasi<{str(ini)}>'

@public
def kondisi(ini: Iterasi) -> int:
    return int(any(ini.iterator))

@public
def ke_teks(ini: Iterasi) -> str:
    writers = []
    for value in ini.iterator:
        if value is ini:
            writers.append('Iterasi<[ ... ]>')
        else:
            writers.append(str(value))

    if len(writers) < ini.length:
        writers += ['...'] * (ini.length - len(writers))

    return f'[ {', '.join(writers)} ]'

@public
def salin(ini: Iterasi) -> Iterasi:
    new_iterator = ini.iterator.copy()
    return Iterasi(iterator=new_iterator, length=ini.length, type=ini.type)

@public
def salin_mendalam(ini: Iterasi) -> Iterasi:
    from copy import deepcopy
    new_iterator = deepcopy(ini.iterator)
    return Iterasi(iterator=new_iterator, length=ini.length, type=ini.type)

@public
def cek_jangkauan(ini: Iterasi, instance: Any) -> int:
    return int(getattr(instance, '__origin__', None) is ini.struct)

@Module
def utama(cls) -> None:
    cls.add_struct(Iterasi)