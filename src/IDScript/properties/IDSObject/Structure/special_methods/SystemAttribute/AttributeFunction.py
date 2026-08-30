from .....TypeSystem         import CheckType, TypeFunction
from .__helper               import to_ids, to_py
from ..                      import TOKEN

from typing                  import Any

class System:
    __getter = object.__getattribute__

    @classmethod
    def _getter(cls, func: TypeFunction.__origin__, name: str, /) -> Any:
        if CheckType(func, TypeFunction.__origin__):
            raise TypeError(f'Hanya fungsi yang dapat diambil atributnya')

        match name:
            case 'nama':
                return cls.__getter(func, 'name')
            case _:
                raise PermissionError(f'Atribut yang hanya bisa dilihat pada fungsi adalah nama saja')

    @staticmethod
    def _setter(func: TypeFunction.__origin__, name: str, value: Any, /) -> None:
        raise PermissionError(f'Atribut fungsi tidak bisa diubah')

def GetAttr(func: TypeFunction.__origin__, name: str, /) -> Any:
    return System._getter(func, name)

def SetAttr(func: TypeFunction.__origin__, name: str, value: Any, /) -> Any:
    return System._setter(func, name, value)