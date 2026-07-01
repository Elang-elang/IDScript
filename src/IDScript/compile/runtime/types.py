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


def check_types(value: Any, types: Type | str) -> bool:
    try:
        if types is Any:
            return True
        if value is None and (types is None or types is type(None)):
            return True
        try:
            py_class = object.__getattribute__(types, '__PY_CLASS__')
        except (AttributeError, TypeError):
            py_class = None
    
        if py_class is not None:
            return value is types or isinstance(value, py_class)
        if isinstance(types, str) and type(value).__name__ == types:
            return True
        if isinstance(types, tuple):
            return any(check_types(value, item) for item in types)
        check_type(value, types)
        return True

    except Exception as e:
        raise IDSTypeError(
            "Tipe tidak sesuai dengan isianya\n"
            f"tipe {value} != {types}"
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


# class Typedef:
#     def __init__(self, wrapp):
#         self.wrapp = wrapp
#     def __call__(self, *args):
#         return self.wrapp(*args)
#     def __repr__(self):
#         return f'<Typedef: {self.wrapp.name}>'
# 
# class Interface:
#     def __init__(self, keys: List[str], values: List[Type]):
#         self._keys = keys
#         self._values = values
#         self._dict = {}
#     def __getitem__(self, key, /):
#         if key not in self._keys:
#             return KeyError(key)
#         if key not in self._dict:
#             return EMPTY
#         return self._dict[key]
#     def __setitem__(self, key, value, /):
#         if key not in self._keys:
#             raise KeyError(key)
#         if not isinstance(value, self._values[self._keys.index(key)]):
#             raise TypeError(value)
#         self._dict[key] = value
#     def __delitem__(self, key):
#         return NotImplemented
#     def get(self, key, default=EMPTY, /):
#         try:
#             return self[key]
#         except:
#             return default
#     def has(self, key, /):
#         return key in self._keys
#     def set(self, key, value, /):
#         self[key] = value
#     def default(self):
#         for key in self._keys:
#             self[key] = EMPTY
#     def setdefault(self):
#         self.default()
#     def __repr__(self):
#         return f'<InterFace <Protected Dict> >'
#     def __str__(self):
#         return str(self._dict)
#     def __dict__(self):
#         return self._dict
#     def __iter__(self):
#         return iter(self._dict)
#     def __contains__(self, instance, /):
#         return instance in self._dict
#     ...
