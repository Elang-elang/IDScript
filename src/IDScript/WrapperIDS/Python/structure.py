from dataclasses import dataclass, field
from typing      import Any,       Literal
import inspect

from .__helper                                   import CheckType, check_options, resolver_type
from ...properties.IDSObject.Structure.structure import Structure as _S, TypeStructure, TypeField, Configure, Method


class Public:
    def __init__(self, origin) -> Any:
        self.__origin__ = origin

    def __call__(self, *args, **kwargs) -> Any:
        return self.__origin__(*args, **kwargs)
    
    def __class_getitem__(cls, origin) -> Any:
        return Public(origin)

    def __repr__(self) -> str:
        return f'Public[{self.__origin__}]'

    def __instancecheck__(self, instance) -> bool:
        return isinstance(self.__origin__, instance)

    def __todict__(self) -> dict[str, Any]:
        return {
            'type': resolver_type(self.__origin__),
            'private': False,
            'constant': False,
        }
    

@dataclass(repr=False)
class _Binding:
    name:          str
    fields:        list[TypeField]
    def_methods:   list[Any] = field(default_factory=list)
    is_loaded:     bool      = False
    struct:        Any       = None


    def Method(self, func = None, /, *, static: bool = False, public: bool = False, **kwargs):
        if kwargs:
            raise ValueError(f'Opsi hanya ada dua yakni: static dan public')
        
        def get_handler(func):
            res = self.__resolver__(func=func)
            def def_m(func=func) -> Any:
                m = Method(
                    res['name'],
                    res['type_params'],
                    res['resolve_func'],
                    res['return_type'],
                    config  = None,
                    static  = static,
                    private = not public,
                    cls     = None,
                )
                return m
                
            self.def_methods.append(def_m())
            return func

        if func is not None:
            return get_handler(func)
        
        return get_handler

    @staticmethod
    def __resolver__(func):
        about_func   = inspect.signature(func)
        resolve_func = func

        # resolve return type
        return_type = about_func.return_annotation
        if return_type is inspect._empty:
            return_type = Any

        if return_type   is None or \
           return_type   is type(None):
            return_type  = Literal[0]
            def resolve_func(*args):
                func(*args)
                return 0

        elif return_type is bool:
            return_type  = Literal[0, 1]
            resolve_func = lambda *args: int(func(*args))

        params = list(about_func.parameters.values())

        # validate params & resolve
        type_params = []
        for param in params:
            if param.kind.value not in (0, 1):
                raise TypeError(f'Parameter yang harus didaftar adalah parameter posisional dan posisional atau keyword (normal arguments)')
            
            type_params.append( param.annotation
                                if param.annotation is not inspect._empty \
                                else Any \
                                    if param.annotation is not None           and \
                                       param.annotation is not type(None)     and \
                                       param.annotation is not bool               \
                                    else Any )

        return {
            'name':         func.__name__,
            'type_params':  type_params,
            'return_type':  return_type,
            'resolve_func': resolve_func
        }
    
    def __loader__(self, config: Configure, /) -> _S:
        struct    = _S(self.name, self.fields, config=config)
        prototype     = object.__getattribute__(struct, 'PROTOTYPE')
        for m in self.def_methods:
            m.__bind__(struct)
            prototype.methods.append(m)

        self.struct = struct
        self.is_loaded = True
        return struct
    

    def __call__(self, **kwargs) -> Any:
        if not self.is_loaded:
            raise TypeError(f'Binding belum terdaftar')
        
        return self.struct(**kwargs)

    def __getattr__(self, name: str, /) -> Any:
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            if self.is_loaded:
                try:
                    getter = self.struct.__dict__.get(
                        '__getattribute__',
                        lambda name: getattr(self.struct, name)
                    )
                
                    return getter(name)
            
                except (NameError, PermissionError):
                    pass
            raise
        

    def __setattr__(self, name: str, value: Any, /) -> None:
        if self.is_loaded:
            try:
                setter = self.struct.__dict__.get(
                    '__setattr__',
                    lambda name=name, value=value: setattr(self.struct, name, value)
                )
                
                setter(name, value)
            
            except (NameError, PermissionError):
                raise
        else:
            object.__setattr__(self, name, value)
        

    def __delattr__(self, name: str, /) -> None:
        raise PermissionError(f'Tidak dapat menghapus properti {name}')

    def __getitem__(self, name: str, /) -> Any:
        if self.is_loaded:
            try:
                getter = self.struct.__dict__.get(
                    '__getattribute__',
                    lambda name: getattr(self.struct, name)
                )
                
                return getter('ambil_item')(name)
            
            except AttributeError:
                raise
        
        
    def __setitem__(self, name: str, value: Any, /) -> Any:
        if self.is_loaded:
            try:
                getter = self.struct.__dict__.get(
                    '__getattribute__',
                    lambda name: getattr(self.struct, name)
                )
                
                return getter('atur_item')(name, value)
            
            except AttributeError:
                raise

        
    def __delitem__(self, name: str, /) -> Any:
        if self.is_loaded:
            try:
                getter = self.struct.__dict__.get(
                    '__getattribute__',
                    lambda name: getattr(self.struct, name)
                )
                
                return getter('hapus_item')(name)
            
            except AttributeError:
                raise
    
        

    def __instancecheck__(self, instance: Any) -> bool:
        res: list[bool] = []
        if self.is_loaded:
            res.append(isinstance(instance, self.struct))
        
        elif isinstance(instance, TypeStructure):
            d = instance.__dict__
            res.append(d.get('PROTOTYPE').name_struct == self.name)
            
        else:
            res.append(type(instance) is _Binding)
            res.append(hasattr(instance, 'fields'))
            if hasattr(instance, 'fields'):
                res.append(len(instance.fields) == len(self.fields))
                for i, field in enumerate(instance.fields):
                    res.append(field == self.fields[i])

        return all(res)
            

    def __repr__(self) -> str:
        if self.is_loaded:
            return repr(self.struct)
        
        return f'Struktur<{self.name}>'



class Structure:
    __options__ = frozenset({'name', 'fields'})
    def __new__(self, cls = None, /, **kwargs: Any) -> Any:
        bind = None
        if not kwargs and cls is not None:
            bind = self.__binding_from_class__(cls)
            return bind
        
        elif kwargs and cls is None:
            if not kwargs.get('fields'):
                kwargs['fields'] = []

            if not kwargs.get('name'):
                kwargs['name'] = None
            
            check_options(self.__options__, set(kwargs))
            fields = kwargs['fields']
            
            CheckType(fields, list[TypeField], soft=False)
            def get_handler(cls: Any) -> _Binding:
                bind = _Binding(
                    name   = kwargs.get('name', cls.__name__),
                    fields = fields,
                )
                return bind
            
            return get_handler

        raise ValueError(f'Structure (binding/pendaftaran) harus merupakan dekorator')

    @staticmethod
    def __binding_from_class__(cls: Any) -> _Binding:
        annotation = cls.__annotations__
        fields: list[TypeField] = []
        for name, value in annotation.items():
            if hasattr(cls, name):
                raise NameError(f'Tidak ada default value (isi bawaan) pada properti struktur')

            if type(value) is Public:
                value = value.__todict__()
            else:
                value = {
                    'type': resolver_type(value),
                    'private': True,
                    'constant': False,
                }

            fields.append({
                'name': name,
                **value
            })
        
        bind = _Binding(name=cls.__name__, fields=fields)
        return bind
