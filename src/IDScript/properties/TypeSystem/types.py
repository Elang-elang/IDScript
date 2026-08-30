from .._Reprer   import Reprer
from dataclasses import dataclass
from typing      import TypeAliasType, Any, Literal, Union, TypedDict, NotRequired

from types       import FunctionType

"""
Sistem tipe milik IDScript

> Tipe Alias [ Alias : type ]:
- Teks       : str
- AngkaBulat : int
- Float      : float
- Boolean    :  0   |   1
- Angka      : int  | float
- Primitif   : Teks | Angka | Float | Boole
"""

# default type
type Teks       = str
type AngkaBulat = int
type Float      = float

# union type / alias type
type Boolean    = Literal[0, 1]
type Angka      = Union[int, float]

# any alias for default type
type Primitif   = Union[
    Teks, AngkaBulat, Float,
    Boolean, Angka,
]

@Reprer(writer='TipeFungsi', keyword_only=True,)
@dataclass
class TypeFunction:
    """
    Sistem tipe milik IDScript
    
    > Tipe Asli dari pembungkust
    - TypeFunction : merupakan tipe yang terinspirasi dari typing.Callable
                     dan dapat dipanggil seperti generik tipe pada python:
                 
                     ```python
                     >>> TypeFunction[[arg1, arg2], return]
                     ```
                     disini (pada TypeFunction) tidak bisa menanonim panjang argumen
                     dan harus serba eksplisit
    """
    params_type: list[Any]
    return_type: Any

    def __check_return(self, cls: Any, /) -> bool:
        return cls.return_type is self.return_type

    def __check_params(self, cls: Any, /) -> bool:
        return all([
            param_type is self.params_type[i]
            for i, param_type in enumerate(cls.params_type)
        ])

    def __class_getitem__(cls, *args):
        if isinstance(args[0], tuple):
            return cls.__class_getitem__(*args[0])
        
        if len(args) != 2:
            raise TypeError('TypeFunction must be used as Callable[[arg, ...], result]')

        params_type: list[Any] = []
        if isinstance(args[0], list):
            params_type.extend(args[0])
            
        else:
            params_type.append(args[0])

        return_type: Any = args[1]
        return cls(
            params_type=params_type,
            return_type=return_type
        )

    def __instancecheck__(self, instance: Any, /) -> bool:
        return self.check_type(instance)

    def __repr__(self):
        write_params = ', '.join(
            str(param_type)
            for param_type in self.params_type
        )
        
        return f'TypeFunction[[{write_params}], {str(self.return_type)}]'

    def check_type(self, cls: Any) -> bool:
        if type(cls).__name__ not in ('Function', 'Method'):
            return False
        
        return all([
            self.__check_return(cls),
            self.__check_params(cls)
        ])


class TypeField(TypedDict):
    name:     str
    type:     Any
    constant: NotRequired[bool]
    private:  NotRequired[bool]


class TypeStructure(type):
    def __new__(
        cls,
        name:                  str,
        bases:     tuple[Any, ...],
        namespace:  dict[str, Any],
    ) -> type:
        return super().__new__(cls, name, bases, namespace)

    def __getattribute__(cls, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError:
            prototype = cls.__dict__.get('PROTOTYPE')
            if prototype is not None:
                try:
                    return prototype.get_name(name)
                except (NameError, PermissionError):
                    pass
            raise

    def __setattr__(cls, name: str, value: Any) -> None:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            try:
                prototype.set_name(name, value)
                return
            except (NameError, AttributeError):
                pass
        super().__setattr__(name, value)

    def __delattr__(cls, name: str) -> None:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            try:
                this = prototype.search_name(name)
                if isinstance(this, prototype.__class__.__bases__[0].__bases__[0].__dict__.get('Property', type).__origin__):
                    raise PermissionError(f'Tidak dapat menghapus properti {name}')
            except (NameError, AttributeError):
                pass
        super().__delattr__(name)

    def __repr__(self) -> str:
        try:
            return self.__getattribute__('tulisan')
        except:
            return repr(self.__dict__.get('PROTOTYPE'))

    def __instancecheck__(self, instance: Any) -> bool:
        return type(instance) is TypeStructure or 'PROTOTYPE' in dir(instance)
        