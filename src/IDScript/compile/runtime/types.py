"""Runtime type-checking helpers for IDScript values."""

from typeguard import check_type
from typing import (
    Dict, List, Literal, Union, Callable,
    Any, Type,
    get_args, get_origin
)

from ..diagnostics import IDSTypeError

EMPTY = object()
Result = Union


class IniType:
    """Sentinel type for 'Ini' (Self) in trait definitions."""
    def __repr__(self): return '<Ini>'
    def __eq__(self, other): return True
    def __hash__(self): return hash('<Ini>')
    def __call__(self, *args, **kwargs):
        raise IDSTypeError('Ini tidak dapat digunakan di luar sifat/antarmuka')


def check_types(value: Any, types: Type | str) -> bool:
    try:
        if types is Any:
            return True
        if types is Type:
            # Bare typing.Type (unbound generic) accepts any value
            return True
        if value is None and (types is None or types is type(None)):
            return True
        try:
            py_class = object.__getattribute__(types, '__PY_CLASS__')
        except (AttributeError, TypeError):
            py_class = None
    
        if py_class is not None:
            if value is types or isinstance(value, py_class):
                return True
            # Struct inheritance: check if value's struct has all properties
            # that the target type requires (structural subtyping via extend)
            if hasattr(value, '__PROTOTYPE__'):
                value_schema = value.__PROTOTYPE__.get('schema', {})
                target_schema = types.__PROTOTYPE__.get('schema', {})
                value_props = {n for n, f in value_schema.items() if not f.get('is_method')}
                target_props = {n for n, f in target_schema.items() if not f.get('is_method')}
                return target_props.issubset(value_props)
            return False
        if isinstance(types, str) and type(value).__name__ == types:
            return True
        if isinstance(types, tuple):
            return any(check_types(value, item) for item in types)
        # Optional[Type] (Union[Type, None]) — treat like bare Type for unbound generics
        origin = getattr(types, '__origin__', None)
        args = getattr(types, '__args__', ())
        if origin is Union and Type in args:
            return True
        check_type(value, types)
        return True

    except Exception as e:
        raise IDSTypeError(
            "Tipe tidak sesuai dengan isianya\n"
            f"diharapkan: {types}\ndiberikan: {type(value).__name__}"
        )


def default_value(ann: Type):
    origin = get_origin(ann)
    if not origin:
        if ann is type(None):
            return None
        if ann in (str, int, float, bool):
            return ann()
        if ann is Result:
            return None
        raise IDSTypeError('Nilai default hanya tersedia untuk tipe dasar')
    
    args = get_args(ann)
    if origin in (list, dict):
        return origin()
    elif origin == Union:
        return args[0]()
    elif origin == Literal:
        return args[0]
    elif origin == Callable:
        return type(
            '<Function: <Anonymous>>',
            (object,),
            {
                '__init__': lambda _: None,
                '__call__': lambda _, *args: None,
                '__repr__': lambda _: '<Function: <Anonymous>>',
            }
        )()
