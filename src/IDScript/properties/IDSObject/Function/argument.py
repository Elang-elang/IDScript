from ...__helper      import GetAttr,      SetAttr
from ..._Reprer       import Reprer
from ...Scoping       import FieldSpace, NameSpace

from typing import Any


@Reprer(writer='Argumen')
class Argument:
    def __init__(
        self,
        name:  Any,
        type:  Any,
        /,
        *,
        constant: bool = False,
        
    ) -> None:
        field = FieldSpace(name, type, constant=constant)
        SetAttr(self, 'field', field)

    
    def __getattr__(self, name: str, /) -> Any:
        return GetAttr(self, 'field').__getattr__(name)

    
    def __setattr__(self, name: str, value: Any, /) -> None:
        GetAttr(self, 'field').__setattr__(name, value)

    
    def __delattr__(self, name: str, /) -> Any:
        return GetAttr(self, 'field').__delattr__(name)

    
    def __call__(self, value: Any) -> NameSpace:
        field = GetAttr(self, 'field')
        NP    = field.copy(value=value)
        return NP
        

    def __repr__(self):
        self = GetAttr(self, 'field')
        writer_type     = str(GetAttr(self.type, '__qualname__', default=self.type))
        writer_declare  = '' \
                          if not self.constant else 'konst '
        writer = f'{writer_declare}{self.name}: {writer_type}'
        return writer