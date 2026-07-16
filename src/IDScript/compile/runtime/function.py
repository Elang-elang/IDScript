"""Wrappable function/method/closure for IDScript runtime."""

from typing import Any, Callable

from ..exceptions import (
    IDSAttributeError,
    IDSRuntimeError,
)
from .control import Return, Throw
from .scope import Scope
from .types import check_types


def _unwrap_pyvalue(v: Any) -> Any:
    return v.isiAsli if hasattr(v, 'isiAsli') else v


def _raise_from_throw(err: Throw) -> None:
    error = err.args[0] if err.args else IDSRuntimeError('Terjadi kesalahan')
    error = _unwrap_pyvalue(error)
    if not isinstance(error, BaseException):
        error = IDSRuntimeError(error)
    raise error


class Function:
    """Wraps a function/method/anonymous-function body for lazy evaluation."""

    def __init__(
        self,
        compiler: Any,
        name: str | None,
        return_type: Any,
        body: list,
        args_config: Any,
        generic_params: list[str] | None = None,
        *,
        is_method: bool = False,
        struct_name: str | None = None,
        lexical_parent: Any = None,
        args_node: Any = None,
        type_node: Any = None,
    ):
        self._compiler = compiler
        self._name = name
        self._return_type = return_type
        self._body = body
        self._args_config = args_config
        self._generic_params = generic_params or []
        self._is_method = is_method
        self._struct_name = struct_name
        self._lexical_parent = lexical_parent
        self._args_node = args_node
        self._type_node = type_node

    @property
    def _c(self):
        return self._compiler

    def __repr__(self):
        if self._name is None or self._name == '<anonim>':
            return '<Function: <anonim>>'
        if self._is_method:
            return f'<Method: {self._name}>'
        return f'<Function: {self._name}>'

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        c = self._c
        generic_args = kwargs.get('generic_params', [])
        arguments = kwargs.get('arguments', list(args))

        if self._is_method:
            return self._method_call(c, generic_args, arguments)
        return self._function_call(c, generic_args, arguments)

    def _method_call(self, c: Any, generic_args: list, arguments: list) -> Any:
        lexical_parent = self._lexical_parent
        saved_scope = c.current_scope
        c.current_scope = Scope(parent=lexical_parent)
        c.config.enter_func()
        c.config.enter_struct(self._struct_name)
        try:
            if generic_args and self._generic_params:
                return self._generic_wrapper(c, generic_args, arguments, scope_managed=True)
            return self._wrapper_func(c, arguments)
        finally:
            c.current_scope = saved_scope
            c.config.leave_struct()
            c.config.leave_func()

    def _function_call(self, c: Any, generic_args: list, arguments: list) -> Any:
        parent = c.current_scope
        c.current_scope = Scope(parent=parent)
        c.config.enter_func()
        try:
            if generic_args and self._generic_params:
                return self._generic_wrapper(c, generic_args, arguments, scope_managed=False)
            return self._wrapper_func(c, arguments)
        finally:
            c.current_scope = parent
            c.config.leave_func()

    def _generic_wrapper(
        self, c: Any, generic_args: list, arguments: list, *, scope_managed: bool
    ) -> Any:
        if not scope_managed:
            parent = c.current_scope
            c.current_scope = Scope(parent=parent)
            c.config.enter_func()
            try:
                self._declare_generic_params(c, generic_args)
                return self._wrapper_func(c, arguments)
            finally:
                c.current_scope = parent
                c.config.leave_func()
        else:
            self._declare_generic_params(c, generic_args)
            return self._wrapper_func(c, arguments)

    def _declare_generic_params(self, c: Any, generic_args: list) -> None:
        from typing import Type as T
        for idx, param_name in enumerate(self._generic_params):
            if len(generic_args) <= idx:
                raise IDSAttributeError(
                    f'{self._name}() kekurangan argumen generik wajib {param_name!r}'
                )
            c.current_scope.declare(param_name, T, generic_args[idx], True, True)

    def _wrapper_func(self, c: Any, arguments: list) -> Any:
        c._set_expected(self._type_node, self._return_type)
        arguments = list(arguments)

        if self._is_method:
            args_config = self._args_config
            try:
                if args_config and arguments:
                    for i, arg in enumerate(args_config['wrapp']):
                        if i < len(arguments):
                            arg(arguments[i])
                        else:
                            raise IDSAttributeError(
                                f'{self._name}() kekurangan argumen wajib {arg.__name__!r}'
                            )
                if arguments and not args_config:
                    raise IDSAttributeError(
                        f'{self._name}() menerima 0 argumen tetapi diberi {len(arguments)}'
                    )
                for stmt in self._body:
                    c.v(stmt)
            except Return as res:
                result = None
                if res.args:
                    result = res.args[0]
                check_types(result, self._return_type)
                return result
            except Throw as err:
                _raise_from_throw(err)
            except:
                raise
            finally:
                c._clear_expected()
        else:
            args = c.v(self._args_node) if self._args_node else None
            try:
                if args and arguments:
                    for i, arg in enumerate(args['wrapp']):
                        if i < len(arguments):
                            arg(arguments[i])
                        else:
                            raise IDSAttributeError(
                                f'{self._name}() kekurangan argumen wajib {arg.__name__!r}'
                            )
                if arguments and not args:
                    raise IDSAttributeError(
                        f'{self._name}() menerima 0 argumen tetapi diberi {len(arguments)}'
                    )
                for stmt in self._body:
                    c.v(stmt)
            except Return as res:
                result = None
                if res.args:
                    result = res.args[0]
                check_types(result, self._return_type)
                return result
            except Throw as err:
                _raise_from_throw(err)
            except:
                raise
            finally:
                c._clear_expected()
