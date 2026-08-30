from .....TypeSystem         import CheckType, TypeStructure
from ....Structure.structure import Structure, StructureObjectType
from .__helper               import to_ids, to_py
from ..                      import TOKEN

from typing                  import Any



class System:
    @staticmethod
    def _get_getter(
        cls:  StructureObjectType,
        /,
        
    ) -> Any:
        if CheckType(cls, Structure) or type(cls) is Structure:
            return object.__getattribute__
        elif CheckType(cls, TypeStructure) or type(cls) is TypeStructure:
            return TypeStructure.__getattribute__
        raise TypeError(f'Hanya struktur yang dapat diambil atributnya')

    
    @classmethod
    def _get_prototype(
        self,
        cls:  StructureObjectType,
        /,
        
    ) -> Any:
        getter = self._get_getter(cls)
        return getter(cls, 'PROTOTYPE')


    
    @classmethod
    def _force_getter(
        self,
        cls:  StructureObjectType,
        name: str,
        /,
        
    ) -> Any:
        prototype = self._get_prototype(cls)
        try:
            return prototype.get_name(name)
        except AttributeError:
            raise AttributeError(f'{prototype.name_struct} tidak memiliki atribut {name!r}')

    
    @classmethod
    def _soft_getter(
        self,
        cls:  StructureObjectType,
        name: str,
        /,
        
    ) -> Any:
        raw_getter:  Any = self._get_getter(cls)
        prototype:   Any = self._get_prototype(cls)
        getter_attr: Any = raw_getter(cls, '__getattr__')
        
        for method in prototype.methods:
            if method.name == TOKEN.__getattr__.idscript:
                getter_attr = method
                break
            
        try:
            return getter_attr(name)
        except TypeError as e:
            if "missing 1 required positional argument: 'name'" in str(e):
                return getter_attr(cls, name)
        
            
        except AttributeError:
            raise AttributeError(f'{prototype.name_struct} tidak memiliki atribut {name!r}')

    

    @classmethod
    def _force_setter(
        self,
        cls:   StructureObjectType,
        name:  str,
        value: Any,
        /,
        
    ) -> None:
        prototype = self._get_prototype(cls)
        try:
            prototype.set_name(name, value)
        except AttributeError:
            raise AttributeError(f'{prototype.name_struct} tidak memiliki atribut {name!r}')


    @classmethod
    def _soft_setter(
        self,
        cls:   StructureObjectType,
        name:  str,
        value: Any,
        /,
        
    ) -> None:
        raw_getter:  Any = self._get_getter(cls)
        prototype:   Any = self._get_prototype(cls)
        setter_attr: Any = raw_getter(cls, '__setattr__')
        
        for method in prototype.methods:
            if method.name == TOKEN.__setattr__.idscript:
                setter_attr = method
                break
            
        try:
            setter_attr(name, value)
            
        except AttributeError:
            raise AttributeError(f'{prototype.name_struct} tidak memiliki atribut {name!r}')




def ForceGetAttr(cls: StructureObjectType, name: str, /) -> Any:
    return System._force_getter(cls, name)

def GetAttr(cls: StructureObjectType, name: str, /) -> Any:
    return System._soft_getter(cls, name)

def ForceSetAttr(cls: StructureObjectType, name: str, value: Any, /) -> None:
    System._force_setter(cls, name, value)

def SetAttr(cls: StructureObjectType, name: str, value: Any, /) -> None:
    System._soft_setter(cls, name, value)