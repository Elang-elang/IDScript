from ..__helper     import GetAttr, SetAttr
from .._Reprer      import Reprer
from ..TypeSystem   import CheckType
from .constanta     import (
    SLOTS_PROPERTY, SLOTS_METHODS, SLOTS_ATTRS,
    SLOTS_ALIAS,                   SLOTS_VALUE,
)

from typing  import Any,      Type
from copy    import deepcopy as _d

_inside_copy = False

@Reprer(writer='Penamaan')
class NameSpace:
    __slots__ = frozenset(SLOTS_PROPERTY)
    
    def __init__(
        self,
        name:     str,
        type:     Any,
        value:    Any,
        *,
        constant: bool = False,
        private:  bool = True,
        
    ) -> None:
        CheckType(name,  str,         soft=False)
        CheckType(value, type,        soft=False)
        
        SetAttr(self,    'name',      name)
        SetAttr(self,    'type',      type)
        SetAttr(self,    'value',     value)
        SetAttr(self,    'private',   private)
        SetAttr(self,    'constant',  constant)

    def __getattr__(
        self,
        name: str,
        /,
    ) -> Any:
        if name in SLOTS_ATTRS:
            return GetAttr(self, name)
        
        elif name in SLOTS_ALIAS:
            return GetAttr(self, SLOTS_ALIAS[name])
        
        raise AttributeError(f'Tidak ada atribut {name}')

    def __setattr__(
        self,
        name: str,
        value: Any,
        /,
    ) -> None:
        if _inside_copy:
            SetAttr(self, name, value)
            return
        
        if name not in SLOTS_VALUE:
            if name in {*SLOTS_ATTRS, *SLOTS_ALIAS}:
                raise PermissionError(f'Tidak dapat mengubah {name}')
            raise AttributeError(f'Tidak ada atribut {name}')

        if self.constant:
            raise PermissionError(f'Tidak dapat mengubah isian karena konstant')

        CheckType(value, self.type, soft=False)
        SetAttr(self,    'value',   value)

    def __delattr__(
        self,
        name: str,
        /,
    ) -> None:
        if name in {*SLOTS_ATTRS, *SLOTS_ALIAS}:
            raise PermissionError(f'Tidak dapat menghapus atribut {name}')
        
        raise AttributeError(f'Tidak ada atribut {name}')


    __getitem__ = __getattr__
    __setitem__ = __setattr__
    __delitem__ = __delattr__

    
    def copy(
        self,
        *,
        constant: bool | None = None,
        private:  bool | None = None,
        
    ) -> Any:
        global _inside_copy
        _inside_copy = True
        
        name   = self.name
        type   = self.type
        value  = self.value

        _inside_copy = False
        
        if constant is None:
            constant = self.constant
        
        if private  is None:
            private  = self.private

        return NameSpace(
            name,
            type,
            value,
            constant = constant,
            private  = private,
        )

    
    __deepcopy__ = copy
    __copy__ = copy

    
    def to_dict(self) -> dict[str, Any]:
        d = {}
        NS_copy  =  self.copy()
        for k    in SLOTS_PROPERTY:
            v    =  getattr(NS_copy, k)
            d[k] = v

        return d
    
    
    def __repr__(self) -> str:
        writer_type     = str(GetAttr(self.type, '__qualname__', default=self.type))
        writer_declare  = 'var' \
                          if not self.constant else 'konst'
        writer_private  = 'privat' \
                          if self.private else 'publik'

        writer = f'({writer_private}) {writer_declare} {self.name}: {writer_type} = {self.value};'
        return writer