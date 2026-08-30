from IDScript.WrapperIDS.Python import Function, Module
from re import findall
from typing import Any

@Function
def Format(object: str, subject: Any) -> str:
    if not findall(r'\{\}', object):
        raise TypeError(f'Dalam teks objek, kamunharu memberikan kurung ({'{}'!r}) agar terbaca')
    result = object.format(subject)
    return result


@Module
def utama(cls) -> None:
    cls.add_func(Format)