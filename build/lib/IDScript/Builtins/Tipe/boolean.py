from IDScript.WrapperIDS.Python import *
from typing import Any, Literal

@Structure
class Kondisi:
    boolean: Literal[0, 1]

public_method = Kondisi.Method(public=True)
private_method = Kondisi.Method

@Kondisi.Method(public=True, static=True)
def inisiasi(boolean: int | bool) -> Kondisi:
    if type(boolean) is int:
        boolean = bool(boolean)
    return Kondisi(boolean=int(boolean))

@public_method
def cek(cls: Kondisi, cek: Literal[0, 1] = 1) -> int:
    return int(cls.boolean == cek)

@public_method
def atur(cls: Kondisi, boolean: int) -> Kondisi:
    Kondisi.boolean = int(bool(boolean))



@public_method
def tulisan(cls: Kondisi) -> str:
    writer = "Benar" \
             if bool(cls.boolean) \
             else "Salah"

    return f"Kondisi({writer})"

@public_method
def ke_angka(cls: Kondisi) -> int:
    return cls.boolean

@public_method
def kondisi(cls: Kondisi) -> int:
    return cls.boolean

@public_method
def ke_teks(cls: Kondisi) -> str:
    writer = "Benar" \
             if bool(cls.boolean.cek_kebenaran()) \
             else "Salah"
    return writer.lower()

@Kondisi.Method(public=True, static=True)
def cek_jangkauan(jangkauan: Any) -> int:
    if type(jangkauan) is int:
        return int(jangkauan in [0, 1])
    elif isinstance(jangkauan, Kondisi):
        return True
    elif type(jangkauan) is str:
        return int(jangkauan.lower() in ['benar', 'salah'])
    return False

@Module
def utama(cls)-> None:
    cls.add_struct(Kondisi)
    