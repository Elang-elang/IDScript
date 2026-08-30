from .special_method import ForceGet
from .object import Structure

from typing import Any
import operator


def wrapp(bound: str) -> Any:
    def wrapper(a: Any, b: Any) -> Any:
        if isinstance(a, Structure):
            return ForceGet(a, bound)(b)
        else:
            return getattr(a, bound)(b)
    return wrapper

def eq(a: Any, b: Any) -> bool:
    return wrapp('__eq__')(a, b)

def neq(a: Any, b: Any) -> bool:
    return wrapp('__neq__')(a, b)

def gt(a: Any, b: Any) -> bool:
    return wrapp('__gt__')(a, b)

def lt(a: Any, b: Any) -> bool:
    return wrapp('__lt__')(a, b)

def ge(a: Any, b: Any) -> bool:
    return wrapp('__ge__')(a, b)

def le(a: Any, b: Any) -> bool:
    return wrapp('__le__')(a, b)

def in_(a: Any, b: Any) -> bool:
    return wrapp('__contains__')(a, b)

def not_in(a: Any, b: Any) -> bool:
    return not wrapp('__contains__')(a, b)

def is_(a: Any, b: Any) -> bool:
    return operator.is_(a, b)

def is_not(a: Any, b: Any) -> bool:
    return operator.is_not(a, b)

def or_(a: Any, b: Any) -> bool:
    return wrapp('__or__')(a, b)

def not_(a: Any) -> bool:
    return not wrapp('__bool__')(a)


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