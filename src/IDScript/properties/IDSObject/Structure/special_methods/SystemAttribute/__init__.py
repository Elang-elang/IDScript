from .AttributeStructure import ( GetAttr as _gs, ForceGetAttr as _fgs,
                                  SetAttr as _ss, ForceSetAttr as _fss, )
from .AttributeFunction  import   GetAttr as _gf, SetAttr      as _sf

from .....TypeSystem     import   CheckType, TypeFunction
from ....Structure.\
               structure import   StructureObjectType

from typing import Any


def Get(cls: Any, name: str, /) -> Any:
    if   CheckType(cls, TypeFunction.__origin__):
        return _gf(cls, name)
    elif CheckType(cls, StructureObjectType):
        return _gs(cls, name)
    raise TypeError(f'Yang dapat diambil atributnya adalah fungsi dan struktur (objek idscript)')

def Set(cls: Any, name: str, value: Any, /) -> None:
    if   CheckType(cls, TypeFunction.__origin__):
        return _sf(cls, name, value)
    elif CheckType(cls, StructureObjectType):
        return _ss(cls, name, value)
    raise TypeError(f'Yang dapat diatur atributnya adalah struktur (objek idscript)')


def ForceGet(cls: Any, name: str, /) -> Any:
    if   CheckType(cls, TypeFunction.__origin__):
        return _gf(cls, name)
    elif CheckType(cls, StructureObjectType):
        return _fgs(cls, name)
    raise TypeError(f'Yang dapat diambil atributnya adalah fungsi dan struktur (objek idscript)')

def ForceSet(cls: Any, name: str, value: Any, /) -> None:
    if   CheckType(cls, TypeFunction.__origin__):
        return _sf(cls, name, value)
    elif CheckType(cls, StructureObjectType):
        return _fss(cls, name, value)
    raise TypeError(f'Yang dapat diatur atributnya adalah struktur (objek idscript)')