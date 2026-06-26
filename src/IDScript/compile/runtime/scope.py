"""Nested runtime scope used by the IDScript compiler."""

from __future__ import annotations

from typing import Any, Dict
from .types import check_types
from .variable import Variable as Var

class GlobalScope:
    def __init__(self):
        self.__scope: Dict[str, Var] = {}

    def getThis(self, name):
        this = self.__scope.get(name)
        if not this:
            raise NameError(f'{name!r} is not defined')
        return this

    def declare(self, name, type, value=None, constant=False, is_priv=True, is_pointer=False, *arg, **kwargs):
        if name in self.__scope:
            raise NameError(f'{name!r}')

        self.__scope[name] = Var(
            **{
                'name': name,
                'type': type,
                'value': value,
                'constant': constant,
                'is_priv': is_priv,
                'is_pointer': is_pointer
            }
        )
    
    def set(self, name, value):
        this = self.getThis(name)
        if this.is_const:
            raise NameError(f'{name!r}')

        if this.is_pointer:
            this.pointer_set(value)
        else:
            check_types(value, this.type)
            this.value = value

    def get(self, name):
        this = self.getThis(name)
        return this.value

    def has(self, name):
        try:
            return not not self.get(name)

        except NameError:
            return False
    
    def exports(self):
        exports = {}
        if not self.__scope:
            return exports
        
        for k, v in self.__scope.items():
            if v.is_priv:
                continue

            exports[k] = v
        return exports


class Scope:
    def __init__(self, *, parent: GlobalScope | Scope | None = None):
        self.__parent: GlobalScope | Scope | None = parent
        self.__scope: Dict[str, Var] = {}

    def getThis(self, name):
        this = self.__scope.get(name)
        if not this and self.__parent:
            this = self.__parent.getThis(name)
    
        if not this:
            raise NameError(f'{name!r} is not defined')

        return this

    def declare(self, name, type, value=None, constant=False, is_priv=True, is_pointer=False):
        if name in self.__scope:
            raise NameError(f'{name!r}')

        if is_pointer or check_types(value, type):
            self.__scope[name] = Var(
                **{
                    'name': name,
                    'type': type,
                    'value': value,
                    'constant': constant,
                    'is_priv': is_priv,
                    'is_pointer': is_pointer
                }
            )
    
    def set(self, name, value):
        this = self.getThis(name)
        if this.is_const:
            raise NameError(f'{name!r}')

        if this.is_pointer:
            this.pointer_set(value)
        else:
            check_types(value, this.type)
            this.value = value

    def get(self, name):
        this = self.getThis(name)
        return this.value

    def has(self, name):
        try:
            return not not self.get(name)
        except NameError:
            return False
