"""Nested runtime scope using ChainMap for efficient lookup."""

from __future__ import annotations

from collections import ChainMap
from typing import Any, Dict

from ..diagnostics import IDSNameError
from .types import check_types
from .variable import Variable as Var


class GlobalScope:
    def __init__(self):
        self._maps: list[Dict[str, Var]] = [{}]

    def _scope(self) -> ChainMap[str, Var]:
        return ChainMap(*self._maps)

    def getThis(self, name):
        try:
            return self._scope()[name]
        except KeyError:
            raise IDSNameError(f'{name!r} tidak terdefinisi')

    def declare(self, name, type, value=None, constant=False, is_priv=True, is_pointer=False, *arg, **kwargs):
        if name in self._maps[0]:
            raise IDSNameError(f'{name!r} sudah dideklarasikan')
        self._maps[0][name] = Var(
            name=name, type=type, value=value,
            constant=constant, is_priv=is_priv, is_pointer=is_pointer,
        )

    def set(self, name, value):
        for m in self._maps:
            if name in m:
                var = m[name]
                if var.is_const:
                    raise IDSNameError(f'{name!r} adalah konstanta dan tidak dapat diubah')
                if var.is_pointer:
                    var.pointer_set(value)
                else:
                    check_types(value, var.type)
                    var.value = value
                return
        raise IDSNameError(f'{name!r} tidak terdefinisi')

    def get(self, name):
        return self.getThis(name).value

    def has(self, name):
        try:
            self.get(name)
            return True
        except IDSNameError:
            return False

    def exports(self):
        exports = {}
        for m in self._maps:
            for k, v in m.items():
                if not v.is_priv and k not in exports:
                    exports[k] = v
        return exports


class Scope:
    def __init__(self, *, parent: GlobalScope | Scope | None = None):
        self._maps: list[Dict[str, Var]] = [{}]
        if parent is not None:
            self._maps.extend(parent._maps)

    def _scope(self) -> ChainMap[str, Var]:
        return ChainMap(*self._maps)

    def getThis(self, name):
        try:
            return self._scope()[name]
        except KeyError:
            raise IDSNameError(f'{name!r} tidak terdefinisi')

    def declare(self, name, type, value=None, constant=False, is_priv=True, is_pointer=False):
        if name in self._maps[0]:
            raise IDSNameError(f'{name!r} sudah dideklarasikan')
        if is_pointer or check_types(value, type):
            self._maps[0][name] = Var(
                name=name, type=type, value=value,
                constant=constant, is_priv=is_priv, is_pointer=is_pointer,
            )

    def set(self, name, value):
        for m in self._maps:
            if name in m:
                var = m[name]
                if var.is_const:
                    raise IDSNameError(f'{name!r} adalah konstanta dan tidak dapat diubah')
                if var.is_pointer:
                    var.pointer_set(value)
                else:
                    check_types(value, var.type)
                    var.value = value
                return
        raise IDSNameError(f'{name!r} tidak terdefinisi')

    def get(self, name):
        return self.getThis(name).value

    def has(self, name):
        try:
            self.get(name)
            return True
        except IDSNameError:
            return False
