from typing import Any

def getter(
    self: Any,
    name: str | None = None,
    /,

) -> None:
    raise AttributeError('Tidak dapat mendapatkan atribut')
    
def setter(
    self:  Any,
    name:  str | None = None,
    value: Any        = None,
    /,

) -> None:
    raise AttributeError('Tidak dapat mengubah atribut')
    
def deleter(
    self: Any,
    name: str | None = None,
    /,

) -> None:
    raise AttributeError('Tidak dapat menghapus atribut')