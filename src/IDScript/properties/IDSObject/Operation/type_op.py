from ..Structure.special_methods.SystemAttribute          import ForceGet
from ..Structure.special_methods.SystemAttribute.__helper import to_ids, to_py
from ..Structure.structure                                import StructureObjectType
from ..Function.function                                  import Function
from ...TypeSystem                                        import TypeStructure, CheckType, Primitif, get_primitive_type
from ...__helper                                          import GetAttr

from typing import Any
import operator


def wrapp(bound: str) -> Any:
    
    def wrapper[A, B](a: A, b: B, bound=bound) -> Any:
        return_type: Any = int
        if CheckType(a, StructureObjectType):
            ids_bound          = to_ids(         bound)
            handler            = ForceGet(a, ids_bound)
            return_type        = handler.return_type
            
        else:
            py_bound           = to_py(         bound)
            handler            = GetAttr(a,  py_bound)
            return_type = {
                str: get_primitive_type()['Teks'],
                int: get_primitive_type()['AngkaBulat'],
                float: get_primitive_type()['Float'],
                bool: get_primitive_type()['Boolean'],
                type(None): get_primitive_type()['AngkaBulat'],
                type(lambda: None): Function
            }.get(type(a), get_primitive_type()['AngkaBulat'])
            
        return return_type
        
    return wrapper


def eq(a: Any, b: Any) -> Any:
    return wrapp('__eq__')(a, b)

def ne(a: Any, b: Any) -> Any:
    return wrapp('__ne__')(a, b)

def gt(a: Any, b: Any) -> Any:
    return wrapp('__gt__')(a, b)

def lt(a: Any, b: Any) -> Any:
    return wrapp('__lt__')(a, b)

def ge(a: Any, b: Any) -> Any:
    return wrapp('__ge__')(a, b)

def le(a: Any, b: Any) -> Any:
    return wrapp('__le__')(a, b)

def in_(a: Any, b: Any) -> Any:
    return wrapp('__contains__')(a, b)

def not_in(a: Any, b: Any) -> Any:
    return wrapp('__contains__')(a, b)

def is_(a: Any, b: Any) -> Any:
    return get_primitive_type()['Boolean']

def is_not(a: Any, b: Any) -> Any:
    return get_primitive_type()['Boolean']

def or_(a: Any, b: Any) -> Any:
    return wrapp('__or__')(a, b)

def not_(a: Any) -> Any:
    return get_primitive_type()['Boolean']


def add(a: Any, b: Any) -> Any:
    return wrapp('__add__')(a, b)

def sub(a: Any, b: Any) -> Any:
    return wrapp('__sub__')(a, b)

def truediv(a: Any, b: Any) -> Any:
    return wrapp('__truediv__')(a, b)

def mul(a: Any, b: Any) -> Any:
    return wrapp('__mul__')(a, b)

def pow(a: Any, b: Any) -> Any:
    return wrapp('__pow__')(a, b)