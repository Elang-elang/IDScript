from ..__helper     import setter, deleter
from .._Reprer      import Reprer
from ..TypeSystem   import CheckType
from .namespace     import NameSpace
from .fieldspace    import FieldSpace
from .constanta     import SCOPES as TYPE_SCOPE

from abc     import ABCMeta, ABC, abstractproperty, abstractmethod
from typing  import Any, Type, Self, Union
from json    import dumps as _d


class TypeScope(ABC):
    @abstractmethod
    def __init__(
        self,
        *,
        parent: Any
    ) -> None:
        pass

    
    @abstractproperty
    def space(self) -> Any:
        pass
    
    @abstractproperty
    def parent_space(self) -> Any:
        pass


    
    def this_space(
        self,
        name: str,
        /,
        
    ) -> Union[NameSpace, FieldSpace]:
        if name in self.space:
            return self.space.get(name)
        
        elif self.parent_space:
            if isinstance(self.parent_space, dict):
                if name in self.parent_space:
                    return self.parent_space[name]
            
            if isinstance(self.parent_space, TypeScope):
                return self.parent_space.this_space(name)

        print(self)
        raise NameError(f'Tidak ada {name!r} pada space ini')

    
    def extend_space(
        self,
        cls:     Any,
        *,
        copy:    bool = True,
        filter:  bool = True,
    ) -> Self:
        
        sbj = cls.space
        obj = self.space
        
        if filter:
            for name, space in obj.items():
                if name in sbj:
                    sbj.pop(name)
        
        
        if copy:
            obj.update({
                name: space.copy()
                for name, space in sbj.items()
            })
        
        else:
            obj.update(sbj)
        
        return self


    def copy_space(
        self,
        /,
        
    ) -> dict[str, Any]:
        d = {}
        for k, v in self.space.items():
            d[k] = v.copy()

        d_copy = d.copy()
        return d_copy


    def export_space(self) -> dict[str, Any]:
        d = {}
        for k, v in self.space.items():
            if not v.private:
                d[k] = v
        
        d_copy = d.copy()
        return d_copy
    
    
    def has_name(
        self,
        name: str,
        /,
        
    ) -> bool:
        return name in self.space or name in self.parent_space

    
    def get_name(
        self,
        name: str,
        /,
        
    ) -> Any:
        if not self.has_name(name):
            raise NameError(f'Nama yang tak terdefinisi {name!r}')
        
        this = self.this_space(name)
        return this.value

    
    def set_name(
        self,
        name: str,
        value: Any,
        /,
        
    ) -> None:
        if not self.has_name(name):
            raise NameError(f'Nama yang tak terdefinisi {name!r}')
        
        this = self.this_space(name)

        CheckType(value, this.type, soft=False)
        this.value = value

    
    def def_name(
        self,
        name:      str,
        type:      Type | Any,
        value:     Any  | None = None,
        *,
        constant:  bool        = False,
        private:   bool        = True,
    ) -> None:
        if name in self.space:
            raise NameError(f'Nama yang terdefinisi {name!r}')
        
        if value is None:
            self.space[name] = FieldSpace(
                name,
                type,
                constant = constant,
                private  = private
            )
            
        else:
            self.space[name] = NameSpace(
                name,
                type,
                value,
                constant = constant,
                private  = private
            )


    
    @abstractmethod
    def __repr__(self) -> str:
        pass

    
    def __contains__(self, name):
        return self.has_name(name)



class Global(TypeScope):
    def __init__(
        self,
        *,
        parent: Any = None,
        
    ) -> None:
        object.__setattr__(self, '_scope', {})

    space = property(
        lambda self: object.__getattribute__(self, '_scope'),
        setter,
        deleter
    )
    
    parent_space = property(
        lambda self: {},
        setter,
        deleter
    )
    
    def __repr__(self) -> str:
        space = object.__getattribute__(self, 'space').values()
        writer_space = _d(
            {'Global':          list(space)},
            indent  =                     2,
            default = lambda obj: repr(obj),
        )
        return writer_space


@Reprer(writer='Local')
class Local(TypeScope):
    def __init__(
        self,
        *,
        parent: Any = None,
        
    ) -> None:
        self._parent = parent
        self._scope  = {}
    
    space = property(
        lambda self: self._scope,
        setter,
        deleter
    )
    
    parent_space = property(
        lambda self: self._parent,
        setter,
        deleter
    )

    def __repr__(self) -> str:
        space = self.space.values()
        writer_space = _d(
            {'Local':          list(space)},
            indent  =                     2,
            default = lambda obj: repr(obj),
        )
        return writer_space


class Scope:
    @staticmethod
    def __new__(
        name: TYPE_SCOPE,
        /,
        
    ) -> Union[Global, Local]:
        if name.lower()   == 'global':
            return Global
        elif name.lower() == 'local':
            return Local
        else:
            raise TypeError(f'{name!r} bukanlah tipe yang termasuk dari tipe Local atau Global')

    @staticmethod
    def __class_getitem__(
        name: TYPE_SCOPE,
        /,
        
    ) -> Union[Global, Local]:
        return Scope.__new__(name)