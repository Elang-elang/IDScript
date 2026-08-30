from ...__helper      import ( GetAttr,          SetAttr,
                               deleter                    )
from ..._Reprer       import   Reprer
from ...Scoping       import   NameSpace
from ...config        import   Configure
from ..types          import   TypeField,   TypeStructure
from .property        import   Property
from .method          import   Method
from .prototype       import   Prototype

from typing import Any

type StructureObjectType = TypeStructure | Structure

class Structure:
    def __init__(
        self,
        name_struct: str,
        fields:      list[TypeField],
        *,
        config:      Configure,
        
    ) -> None:
        properties = []
        for field in fields:
            property = Property(
                field['name'],
                field['type'],
                private=field.get('private', False),
                constant=field.get('constant', False),
            )
            properties.append(property)

        d = {
            'name_struct': name_struct,
            'properties':   properties,
            'methods':              [],
            'namespace':            [],
            'config':           config,
        }
        
        prototype = Prototype(**d)
        SetAttr(self, 'PROTOTYPE', prototype)


    def def_method(
        self,
        *args:    Any,
        **kwargs: Any,
        
    ) -> None:
        GetAttr(self, 'PROTOTYPE').def_method(*args, **kwargs)


    def copy(self) -> Any:
        prototype  = GetAttr(self, 'PROTOTYPE').copy()
        new_struct = Structure(
                     prototype.name_struct,
                                        [],
            config =      prototype.config,
        )
        SetAttr(new_struct, 'PROTOTYPE', prototype)
        return new_struct
    
    
    def __getattr__(
        self,
        name: str,
        /,
        
    ) -> Any:
        if name.startswith('__') and name.endswith('__'):
            if name in ['__name__', '__qualname__']:
                return GetAttr(self, 'PROTOTYPE').name_struct
            return GetAttr(self, name)
        
        prototype   = GetAttr(self, 'PROTOTYPE')
        this        = prototype.search_name(name)
        name_struct = prototype.name_struct
        config      = prototype.config
        if this.private and not config.is_struct(name_struct):
            raise PermissionError(f'Atribut {prototype} merupakan atribut privat')

        return prototype.get_name(name)

    
    def __setattr__(
        self,
        name:  str,
        value: Any,
        /,
        
    ) -> None:
        prototype   = GetAttr(self, 'PROTOTYPE')
        this        = prototype.search_name(name)
        name_struct = prototype.name_struct
        config      = prototype.config
        if this.private and not config.is_struct(name_struct):
            raise PermissionError(f'Atribut {prototype} merupakan atribut privat')
        
        prototype.set_name(name, value)


    def __delattr__(self, name: str) -> None:
        return deleter(self)

    __getattribute__ = __getattr__

    __getitem__ = __getattr__
    __setitem__ = __setattr__
    __delitem__ = __delattr__


    @staticmethod
    def __resolver_method__(cls: Any, method: Any):
        def resolve_method(*args: Any) -> Any:
            return method(cls, *args)
        return resolve_method

    
    def __call__(self, **kwargs: Any) -> type[object]:
        prototype = GetAttr(self, 'PROTOTYPE')
        new_prototype = prototype.copy()
        
        new_prototype.called = True
        
        new_struct = TypeStructure(
            prototype.name_struct,
            (object,),
            { 'PROTOTYPE': new_prototype }
        )
        
        names_method = [
            '__getattribute__',
            '__getattr__',
            '__setattr__',
            '__delattr__',
            '__getitem__',
            '__setitem__',
            '__delitem__',
        ]

        resolver_method = GetAttr(self, '__resolver_method__')
        for name        in names_method:
            method      = GetAttr(Structure, name)
            resolve     = resolver_method(cls=new_struct, method=method)
            TypeStructure.__setattr__( new_struct, name, resolve )

        TypeStructure.__setattr__(new_struct, '__origin__',       self)

        
        new_prototype.binding(new_struct, **kwargs)
        TypeStructure.__setattr__(new_struct, 'PROTOTYPE', new_prototype)
        return new_struct


    def __instancecheck__(self, instance: Any) -> bool:
        return isinstance(instance, TypeStructure)
        

    def __repr__(self) -> str:
        prototype         = GetAttr(self, 'PROTOTYPE')
        name_struct       = prototype.name_struct
        writer_properties = ',\n  '.join([ repr(p)
                                           for p in prototype.properties ])
        writer            = '{}' \
                            if not writer_properties \
                            else f'{{\n{writer_properties}  \n}}'
        
        return f'{name_struct} {writer}'