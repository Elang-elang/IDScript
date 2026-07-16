"""Shared generic factory for Structure and Enum types."""

from typing import Any
from typing import Type as T
import builtins

from ..exceptions import IDSAttributeError
from .scope import Scope


def make_generic_factory(
    compiler: Any,
    name: str,
    generic_params_info: list,
    generic_method_asts: list,
    generic_cache: dict,
    build_concrete,
    *,
    set_expected: bool = False,
    maxsize: int = 128,
):
    """Create a factory callable for generic struct or enum types.

    Args:
        compiler: Compiler instance
        name: Type name
        generic_params_info: List of param info dicts from GenericParam handler
        generic_method_asts: List of {params, body, trait} from implementations
        generic_cache: Dict cache keyed by type_args tuple
        build_concrete: Callable(compiler) -> concrete type instance
        set_expected: If True, set _expected_type/name for Ini resolution
        maxsize: Max cache entries before LRU eviction (0 = unlimited)
    """
    _lru = maxsize > 0

    def _touch(key):
        if _lru and key in generic_cache:
            val = generic_cache.pop(key)
            generic_cache[key] = val

    def _store(key, val):
        if not _lru:
            generic_cache[key] = val
            return
        if key in generic_cache:
            del generic_cache[key]
        elif len(generic_cache) >= maxsize:
            generic_cache.pop(next(iter(generic_cache)))
        generic_cache[key] = val

    def factory(*type_args):
        cache_key = type_args
        cached = generic_cache.get(cache_key)
        if cached is not None:
            _touch(cache_key)
            return cached

        inner_parent = compiler.current_scope
        compiler.current_scope = Scope(parent=inner_parent)
        compiler.config.enter_struct(name)
        try:
            for idx, gp in enumerate(generic_params_info):
                arg = type_args[idx] if idx < len(type_args) else None
                if arg is None:
                    arg = T
                compiler.current_scope.declare(gp['name'], Any, arg, True, True)

            concrete = build_concrete(compiler)

            if set_expected:
                old_exp_type = compiler._expected_type
                old_exp_name = compiler._expected_name
                compiler._set_expected(name, concrete)

            for impl_info in generic_method_asts:
                impl_params = impl_info['params']
                impl_body = impl_info['body']
                impl_trait = impl_info['trait']

                impl_parent = compiler.current_scope
                compiler.current_scope = Scope(parent=impl_parent)
                for idx, ip in enumerate(impl_params):
                    ip_info = compiler.v(ip)
                    arg = type_args[idx] if idx < len(type_args) else T
                    compiler.current_scope.declare(ip_info['name'], Any, arg, True, True)
                try:
                    kwargs_methods = compiler.v(impl_body)
                    if impl_trait:
                        trait_obj = compiler.v(impl_trait)
                        trait_obj(kwargs_methods)
                    for kwargs in kwargs_methods:
                        builtins.getattr(concrete, 'set_method')(**kwargs)
                finally:
                    compiler.current_scope = impl_parent

            if set_expected:
                compiler._expected_type = old_exp_type
                compiler._expected_name = old_exp_name

            _store(cache_key, concrete)
            return concrete
        finally:
            compiler.config.leave_struct()
            compiler.current_scope = inner_parent

    return factory
