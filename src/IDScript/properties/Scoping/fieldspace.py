from ..__helper     import GetAttr, SetAttr
from .._Reprer      import Reprer
from ..TypeSystem   import CheckType
from .namespace     import NameSpace
from .constanta     import (
    SLOTS_PROPERTY, SLOTS_METHODS, SLOTS_ATTRS,
    SLOTS_ALIAS,                   SLOTS_VALUE,
)

from typing  import Any,      Type
from copy    import deepcopy as _d

_inside_copy = False

@Reprer(writer='Penetapan')
class FieldSpace:
    __slots__ = frozenset(SLOTS_PROPERTY)
    
    def __init__(
        self,
        name:     str,
        type:     Type,
        *,
        constant: bool = False,
        private:  bool = True,
        
    ) -> None:
        CheckType(name,  str,         soft=False)
        
        SetAttr(self,    'name',      name)
        SetAttr(self,    'value',     None)
        SetAttr(self,    'type',      type)
        SetAttr(self,    'constant',  constant)
        SetAttr(self,    'private',   private)

    def __getattr__(
        self,
        name: str,
        /,
    ) -> Any:
        if name in SLOTS_VALUE:
            raise AttributeError(f'Tidak ada isian karena belum didefinisi')
        
        elif name in SLOTS_ATTRS:
            return GetAttr(self, name)
        
        elif name in SLOTS_ALIAS:
            return GetAttr(self, SLOTS_ALIAS[name])

        raise AttributeError(f'Tidak ada atribut {name}')

    def __setattr__(
        self,
        name: str,
        value: Any,
        /,
    ) -> Any:
        if _inside_copy:
            SetAttr(self, name, value)
        if name not in SLOTS_VALUE:
            if name in {*SLOTS_ATTRS, *SLOTS_ALIAS}:
                raise PermissionError(f'Tidak dapat mengubah {name}')
            raise AttributeError(f'Tidak ada atribut {name}')

        CheckType(value, self.type, soft=False)
        np = NameSpace(
            self.name,
            self.type,
            value,
            constant = self.constant,
            private  = self.private
        )
        return np

    def __delattr__(
        self,
        name: str,
        /,
    ) -> None:
        if name in {*SLOTS_ATTRS, *SLOTS_ALIAS}:
            raise PermissionError(f'Tidak dapat menghapus atribut {name}')

        elif name in SLOTS_VALUE:
            raise AttributeError(f'Tidak ada isian karena belum didefinisi')
        
        raise AttributeError(f'Tidak ada atribut {name}')


    __getitem__ = __getattr__
    __setitem__ = __setattr__
    __delitem__ = __delattr__

    
    def copy(
        self,
        *,
        value:    Any  | None = None,
        constant: bool | None = None,
        private:  bool | None = None,
        
    ) -> Any:
        name   = self.name
        type   = self.type
        
        if constant is None:
            constant = self.constant
        
        if private  is None:
            private  = self.private

        if value    is None:
            return FieldSpace(
                self.name,
                self.type,
                constant = self.constant,
                private  = self.private,
            )
        
        else:
            CheckType(value, self.type, soft=False)
            return NameSpace(
                self.name,
                self.type,
                value,
                constant = self.constant,
                private  = self.private,
            )

    __deepcopy__ = copy
    __copy__ = copy
    

    def to_dict(self) -> dict[str, Any]:
        d = {}
        NS_copy  =  self.copy()
        for k    in SLOTS_PROPERTY:
            if k == 'value':
                continue
            
            v    =  getattr(NS_copy, k)
            d[k] = v

        return d
    

    def __repr__(self) -> str:
        writer_type     = str(GetAttr(self.type, '__qualname__', default=self.type))
        writer_declare  = 'var' \
                          if not self.constant else 'konst'
        writer_private  = 'privat' \
                          if self.private else 'publik'

        writer = f'({writer_private}) {writer_declare} {self.name}: {writer_type};'
        return writer