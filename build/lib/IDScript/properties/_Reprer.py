from .TypeSystem.system  import CheckType
from dataclasses         import dataclass
from typing              import Any
from .__helper.object_op import GetAttr

@dataclass
class Binding:
    posisional_only: bool = False
    keyword_only: bool    = False
    writer: str | None    = None

    def __check_argument(self) -> None:
        if self.keyword_only and self.posisional_only:
            raise ValueError(f'Argumen harus salah satu atau tidak keduanya')

    def __check_writer(self, cls) -> None:
        if self.writer is None:
            self.writer = cls.__name__
        return None

    def checker(self, cls) -> None:
        self.__check_argument()
        self.__check_writer(cls)

    def loader(self, cls):
        self.checker(cls)

        def caller(this, *args, **kwargs) -> object:
            if self.keyword_only:
                if args:
                    raise TypeError(f'{cls.__name__}() takes 0 positional arguments but {len(args)} were given')
                return cls(**kwargs)
            elif self.posisional_only:
                if kwargs:
                    raise TypeError(f'{cls.__name__}() takes 0 keyword arguments but {len(kwargs)} were given')
                return cls(*args)
            else:
                return cls(*args, **kwargs)
        
        obj = type(
            cls.__name__,
            (cls,),
            {
                '__init__':     lambda _: None,
                '__call__':     caller,
                '__repr__':     lambda _: self.writer,
                '__origin__':   cls,
                '__getitem__':  lambda _, *args: cls.__class_getitem__(*args),
                
                '__instancecheck__': lambda _, instance:                               CheckType(cls, instance),
                '__getattribute__':  lambda _, name: cls if name == '__origin__' else getattr(cls,        name),
                '__getattr__':       lambda _, name: cls if name == '__origin__' else getattr(cls,        name),
                '__setattr__':       lambda _, name, value:                           setattr(cls, name, value),
                '__delattr__':       lambda _, name:                                  delattr(cls,        name),
            }
        )
        return obj()

class HelperRepr:
    __options__ = frozenset({
        'posisional_only',
        'keyword_only',
        'writer',
    })
    
    def __new__(self, **options: Any) -> object:
        if options:
            unknown = set(options) - self.__options__
            if unknown:
                raise PermissionError(f'Apa opsi ini {', '.join(unknown)}. yang benar adalah {', '.join(self.__options__)}')

        bind = Binding(**options)
        
        def wrapper(cls: type[object]) -> type[object]:
            return bind.loader(cls)

        return wrapper

# Alias
Reprer = HelperRepr