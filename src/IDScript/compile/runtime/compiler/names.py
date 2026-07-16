from typing import (
    Any, List, Dict, TypedDict, Callable, Type as T,
    Union, Literal, Optional, cast, get_origin,
)
from ...ids_ast import (
    Type, TypeDef, InterFace, InterFaceBody,
    KEMBALIKAN, FUNGSI, DAFTAR, KAMUS, SERIKAT, LITERAL, Dynamic, Name,
)
from ...diagnostics import IDSTypeError
from ..scope import Scope
from ..types import EMPTY, Result, IniType


def Type(self, node: Type):
    t = node.type
    if not isinstance(t, type):
        t = self.v(t)
    if node.option:
        return Optional[t]
    return t


def TypeDef(self, node: TypeDef):
    alias = node.alias.id
    value = self.v(node.value)

    if not node.args:
        self.current_scope.declare(alias, T, value, True, node.is_priv)
        return

    def wrapper(*arguments):
        names = [arg.id for arg in node.args]
        parent = self.current_scope
        self.current_scope = Scope(parent=parent)
        for idx, val in enumerate(arguments):
            self.current_scope.declare(names[idx], T, val, True, True)
        names = names[len(arguments):]
        if names:
            for name in names:
                self.current_scope.declare(name, T, Any, True, True)
        try:
            return self.v(node.value)
        except:
            raise
        finally:
            self.current_scope = parent

    wrapper.__name__ = alias
    self.current_scope.declare(alias, Callable[..., Any], wrapper, True, node.is_priv)


def InterFace(self, node: InterFace):
    alias = node.alias.id
    types_attrs = self.v(node.args)
    typeddict = cast(Any, TypedDict)(
        alias,
        types_attrs
    )
    type_value = type(typeddict)
    self.current_scope.declare(
        alias,
        type_value,
        typeddict,
        True,
        node.is_priv
    )


def InterFaceBody(self, node: InterFaceBody):
    keys_name = [self.v(key) for key in node.keys]
    values_type = [self.v(value) for value in node.values]
    result = {}
    for key, val in zip(keys_name, values_type):
        result[key] = val
    return result


def KEMBALIKAN(self, node: KEMBALIKAN):
    ok = self.v(node.oke_type)
    err = self.v(node.error_type)
    return Result[ok, err]


def FUNGSI(self, node: FUNGSI):
    annotation = node.annotation
    if not node.args:
        return Callable[[], annotation]
    args = [self.v(arg) for arg in node.args]
    return Callable[args, annotation]


def DAFTAR(self, node: DAFTAR):
    body = self.v(node.body)
    return cast(Any, List)[body]


def KAMUS(self, node: KAMUS):
    key = self.v(node.key)
    val = self.v(node.value)
    return cast(Any, Dict)[key, val]


def SERIKAT(self, node: SERIKAT):
    types = [self.v(b) for b in node.bodies]
    if not types:
        return Any
    result = types[0]
    for t in types[1:]:
        result = Union[result, t]
    return result


def LITERAL(self, node: LITERAL):
    types = [self.v(b) for b in node.bodies]
    if not types:
        return Any
    result = types[0]
    for t in types[1:]:
        result = Literal[result, t]
    return result


def Dynamic(self, node: Dynamic):
    builtin_types = {'daftar': list, 'kamus': dict, 'hasil': tuple}
    if node.name.id in builtin_types:
        py_type = builtin_types[node.name.id]
        args = [self.v(arg) for arg in node.args]
        if args:
            if py_type is list:
                if len(args) == 1:
                    return cast(Any, List)[args[0]]
                return tuple[tuple(args)]
            if py_type is dict:
                return cast(Any, Dict)[args[0], args[1]] if len(args) >= 2 else cast(Any, Dict)[Any, Any]
            if py_type is tuple:
                return tuple[tuple(args)] if len(args) > 1 else tuple[args[0], ...]
        return py_type
    saved_exp_type = self._expected_type
    saved_exp_name = self._expected_name
    self._expected_type = EMPTY
    self._expected_name = EMPTY
    typedef = self.v(node.name)
    self._expected_type = saved_exp_type
    self._expected_name = saved_exp_name
    factory = getattr(typedef, '__generic_factory__', None)
    if factory is not None:
        args = [self.v(arg) for arg in node.args]
        return factory(*args)
    if not callable(typedef):
        raise IDSTypeError(f'{node.name.id!r} bukan typedef dinamis')
    args = [self.v(arg) for arg in node.args]
    return typedef(*args)


def Name(self, node: Name):
    if node.id == 'Ini':
        struct_name = self.config.struct_name
        if struct_name is EMPTY:
            return IniType()
        if self._expected_type is not None and self._expected_name == struct_name:
            return self._expected_type
        return self.current_scope.get(struct_name)
    val = self.current_scope.get(node.id)
    if self._expected_type is not None and self._expected_name == node.id:
        if hasattr(val, '__generic__') and val.__generic__:
            return self._expected_type
    if hasattr(val, '__generic__') and val.__generic__:
        factory = getattr(val, '__generic_factory__', None)
        if factory is not None:
            defaults = []
            all_defaults = True
            for gp in val.__generic__:
                if gp.get('default'):
                    defaults.append(gp['default'])
                else:
                    all_defaults = False
                    break
            if all_defaults and defaults:
                resolved_defaults = [self.v(d) for d in defaults]
                return factory(*resolved_defaults)
    return val


HANDLERS = [
    Type, TypeDef, InterFace, InterFaceBody,
    KEMBALIKAN, FUNGSI, DAFTAR, KAMUS, SERIKAT, LITERAL, Dynamic, Name,
]
