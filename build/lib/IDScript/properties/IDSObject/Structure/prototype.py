from ...__helper      import GetAttr,      SetAttr
from ..._Reprer       import Reprer
from ...Scoping       import NameSpace
from ...config        import Configure
from ..types          import TypeField
from .property        import Property
from .method          import Method

from typing      import Any, TypedDict, Union
from types       import FunctionType as _ft
from dataclasses import dataclass
from json        import dumps as _d


class TypePrototype(TypedDict):
    name_struct:  str
    properties:   list[Property]
    methods:      list[Method]
    namespace:    list[NameSpace]
    config:       Configure
    called:       bool


@dataclass
class _Binding:
    name_struct:  str
    properties:   list[Property]
    methods:      list[Method]
    namespace:    list[NameSpace]
    config:       Configure
    called:       bool            = False

    
    def search_name(
        self,
        name: str,
        /,
    ) -> Union[ NameSpace.__origin__,
                Property.__origin__,
                Method.__origin__,    ]:
        
        for space    in  self.namespace:
            if space.name     == name:
                return space
        
        for property in self.properties:
            if property.name  == name:
                return property
        
        for method   in    self.methods:
            if method.name    == name:
                return method

        raise NameError(f'Tidak ada atribut {name!r} pada {self.name_struct}')

    
    def get_name(
        self,
        name: str,
        /,
    ) -> Any:
        this = self.search_name(name)
        if isinstance(this, Property.__origin__):
            raise PermissionError(f'Properti {name!r} dari {self.name_struct} belum terdefinisi dan isi tidak dapat diambil')
        if isinstance(this, NameSpace.__origin__):
            return this.value
        return this

    
    def set_name(
        self,
        name:  str,
        value: Any,
        /,
    ) -> None:
        this = self.search_name(name)
        if isinstance(this, NameSpace.__origin__):
            this.value = value
        
        elif isinstance(this,   Method.__origin__):
            raise PermissionError(f'Metode tidak dapat diubah {name!r}')
        
        elif isinstance(this,  Property.__origin__):
            new_this = this(value)
            self.namespace.append(new_this)
    

    def def_method(
        self,
        name:             str,
        fields:           list[TypeField] | list[Any],
        wrapper:          _ft,
        return_type:      Any,
        *,
        static:           bool  = False,
        private:          bool  = True,
        add_config:       bool  = True,
        cls:              Any   = None
        
    ) -> None:
        method = Method(
            name,
            fields,
            wrapper,
            return_type,
            static       =  static,
            private      =  private,
            config       =  None if not add_config else self.config,
            cls          =  cls
        )
        self.methods.append(method)

    
    def def_property(
        self,
        name:  Any,
        type:  Any,
        *,
        constant: bool = False,
        private:  bool = True,
    ) -> None:
        property = Property(
            name,
            type,
            constant = constant,
            private  = private,
        )
        self.properties.append(property)

    
    @staticmethod
    def from_dict(kwds: TypePrototype, /) -> Any:
        return _Binding(**kwds)

    
    def to_dict(self) -> TypePrototype:
        d: TypePrototype = {
            'name_struct': self.name_struct,
            'properties':  self.properties,
            'methods':     self.methods,
            'namespace':   self.namespace,
            'config':      self.config,
            'called':      self.called,
        }
        return d

    
    def copy(self) -> Any:
        d = self.to_dict()
        d_copy: TypePrototype = {
            'name_struct':                       d['name_struct'],
            'properties':  [p.copy()    for p in d['properties']],
            'methods':     [m.copy()    for m in d['methods']   ],
            'namespace':   [n.copy()    for n in d['namespace'] ],
            'config':                            d['config'     ],
            'called':                                       False,
        }
        
        P_copy = _Binding.from_dict(d_copy)
        return P_copy


    def __bind_method__(self, new_cls: Any) -> None:
        if not self.called:
            raise AttributeError(f'Struktur harus pernah dipanggil baru bisa binding')
        
        for i, method in enumerate(self.methods):
            self.methods[i] = GetAttr(method, '__bind__')(new_cls)

    
    def __bind_property__(self, **kwargs: Any) -> None:
        if len(kwargs) != len(self.properties):
            raise AttributeError(f'Properti yang dibutuhkan dari {self.name_struct} adalah {len(self.properties)} yang diberi {len(kwargs)}')

        if len(kwargs) == 0:
            return

        l_idx: list[int] = []
        for idx, property   in enumerate(self.properties):
            name_property = property.name
            value         = kwargs[name_property]
            space         = property.copy(value=value)
            
            self.namespace.append(space)
            l_idx.append(idx)

        
        for i in range(len(l_idx)):
            self.properties.pop(0)

        
        if len(self.properties) != 0:
            raise ValueError(f'Adalah beberapa properti yang belum terdefinisi {', '.join([p.name for p in self.properties])}')


    def binding(self, cls: Any, /, **kwargs: Any) -> None:
        self.__bind_method__(cls)
        self.__bind_property__(**kwargs)
    
    
    def __repr__(self) -> str:
        d: dict   = dict(**self.to_dict())
        d.pop('config')
        
        writer_d  = _d(d, indent=2, default=lambda obj: repr(obj))
        writer    = f'Prototype({writer_d})'
        return writer


class Prototype:
    __type__    = TypePrototype
    __options__ = frozenset({
        'name_struct', 'properties',
        'methods',     'namespace',
        'config'
    })
    
    def __new__(cls, **kwargs) -> _Binding:
        unknown = set(kwargs) - cls.__options__

        if unknown:
            raise ValueError(f'Tidak ada opsi ini {', '.join(unknown)} pada prototipe')

        bind = _Binding(**kwargs)
        return bind