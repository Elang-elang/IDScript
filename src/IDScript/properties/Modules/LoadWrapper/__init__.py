from ..._Reprer   import Reprer

from typing      import Any,   Literal
from pathlib     import Path


ALIAS = {
    'Python':        'Python',
    'Py':            'Python',
    'JavaScript':    'JavaScript',
    'Js':            'JavaScript'
}

NAMES = set()
for k, v in ALIAS.items():
    NAMES.add(k)
    NAMES.add(v)


TYPES = Literal[*NAMES]

@Reprer(writer='Loader')
class Loader:
    def __init__(self, *args, **kwargs) -> None:
        raise PermissionError(f'Diharuskan memanggil class dengan Loader[Arg](...)')
    
    def __class_getitem__(cls, name: TYPES)-> Any:
        if name not in NAMES:
            raise NameError(f'Tidak ada nama: {name!r}')

        if name in ALIAS:
            name = ALIAS[name]

        match name:
            case 'Python':
                from .Py import Python
                return Python
            case 'JavaScript':
                from .Js import JavaScript
                return JavaScript
            case _:
                raise ModuleNotFoundError(f'Modul belum termuat {name}')