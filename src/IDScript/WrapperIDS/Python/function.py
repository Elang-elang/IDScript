from dataclasses import dataclass
from typing      import Any
import inspect

from .__helper                                 import check_options
from ...properties.IDSObject.Function.function import Function as _OF

@dataclass(repr=False)
class _Binding:
    name:        str
    type_params: list[Any] | tuple[Any]
    return_type: Any
    handler:     Any

    def __loader__(self) -> _OF:
        return _OF(
            self.name,
            self.type_params,
            self.handler,
            self.return_type,
            config=None
        )

    def __repr__(self):
        return f'{self.name}({ ', '.join([ repr(p)
                                           for p in self.type_params ])}): {self.return_type}'


class Function:
    __options__ = frozenset({'name', 'type_params', 'return_type'})
    def __new__(
        cls,
        func = None,
        /,
        **kwargs: Any,
        
    ) -> Any:
        if kwargs and func is None:
            check_options(cls.__options__, set(kwargs))
        
        elif func is not None and not kwargs:
            new_options = cls.__resolve_options__(func)
            kwargs.update(new_options)
        
        else:
            raise ValueError(f'Function (binding/pendaftaran) harus merupakan dekorator')
        
        
        def get_handler(func: Any) -> _Binding:
            return _Binding(
                name        = kwargs.get('name', func.__name__),
                type_params = kwargs['type_params'],
                return_type = kwargs['return_type'],
                handler     = func
            )

        if func is not None:
            return get_handler(func)

        
        return get_handler

    @staticmethod
    def __resolve_options__(func):
        name = func.__name__
        about_func = inspect.signature(func)

        # resolve return type
        return_type = about_func.return_annotation
        if return_type is inspect._empty:
            return_type = Any

        params = list(about_func.parameters.values())

        # validate params & resolve
        type_params = []
        for param in params:
            if param.kind.value not in (0, 1):
                raise TypeError(f'Parameter yang harus didaftar adalah parameter posisional dan posisional atau keyword (normal arguments)')
            
            type_params.append( param.annotation
                                if param.annotation is not inspect._empty
                                else int
                                    if param.annotation is None
                                    else Any )

        return {
            'name':        name,
            'type_params': type_params,
            'return_type': return_type,
        }