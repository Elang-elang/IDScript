from ...__helper      import ( GetAttr,    SetAttr,
                              setter,     deleter   )
from ..._Reprer       import   Reprer
from ...Scoping       import   FieldSpace, NameSpace
from ..types          import   TypeField
from .argument        import   Argument

from typing import Any


SLOTS = frozenset({'arguments', 'params_type'})


@Reprer(writer='Paramter')
class Parameter:
    __slots__ = SLOTS
    
    def __init__(
        self,
        *fields: TypeField,
        
    ) -> None:
        arguments    = []
        params_type  = []
        for field in fields:
            arguments.append(
                Argument(
                    field['name'],
                    field['type'],
                    constant=field.get('constant', False)
                )
            )
            params_type.append(field['type'])
        
        SetAttr(self, 'arguments',     arguments)
        SetAttr(self, 'params_type', params_type)
        

    def __getattribute__(self, name: str) -> Any:
        if name in SLOTS:
            return GetAttr(self, name)
        raise AttributeError(f'Tidak ada atribut {name}')

    
    __setattr__ = setter
    __delattr__ = deleter
    
    
    def __call__(self, *values: Any) -> list[NameSpace]:
        if len(values) == 0 and len(self) == 0:
            return []

        
        if len(values) != len(self):
            raise AttributeError(f'Argumen yang dibutuhkan {len(self.arguments)} yang diberi {len(values)}')

        
        arguments = []
        for i, value in enumerate(values):
            arg = self.arguments[i]
            try:
                arguments.append(arg.copy(value=value))
            
            except IndexError:
                raise AttributeError(f'Argumen yang dibutuhkan {len(self.arguments)} yang diberi {len(values)}')
            
            except TypeError as e:
                print(e)
                raise TypeError(f'Argumen {arg.name} bertipe {arg.type.__qualname__} yang kamu berikan isi yang bertipe {type(value).__qualname__}')

        return arguments


    def __len__(self) -> int:
        return len(self.arguments)
    
    def __iter__(self) -> Any:
        for arg in self.arguments:
            yield arg

    def __contains__(self, instance: Any):
        return instance in self.arguments
    
    def __repr__(self) -> str:
        return f'Parameter({', '.join(repr(arg) for arg in self.arguments)})'