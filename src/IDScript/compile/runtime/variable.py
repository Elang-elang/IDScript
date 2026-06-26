from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from .types import check_types
from .config import Config
from copy import deepcopy

class Variable:
    def __init__(
        self,
        *,
        name: str,
        type: Any,
        value: Any = None,
        constant: bool = False,
        is_priv: bool = True,
        is_pointer: bool = False,
    ):
        if is_pointer:
            if not isinstance(value, Variable):
                raise TypeError(f'Pointer {name!r} membutuhkan referensial variable')
            check_types(value.value, type)
        else:
            check_types(value, type)

        self.__prototype__ = {
            'name': name,
            'type': type,
            'value': value,
            'constant': constant,
            'is_priv': is_priv,
            'is_pointer': is_pointer,
        }

    @property
    def name(self):
        return self.__prototype__['name']

    @property
    def value(self):
        return self.__prototype__['value']

    @value.setter
    def value(self, value):
        check_types(value, self.type)
        self.__prototype__['value'] = value

    @property
    def type(self):
        return self.__prototype__['type']

    @property
    def is_const(self):
        return self.__prototype__['constant']

    @property
    def is_priv(self):
        return self.__prototype__['is_priv']

    @property
    def is_pointer(self):
        return self.__prototype__['is_pointer']

    is_private = is_priv
    is_point = is_pointer

    def __repr__(self):
        if self.is_pointer:
            return hex(id(self.value))
        return f'<Variable: {self.name}>'

    def __getitem__(self, key):
        return self.__prototype__[key]

    def export(self):
        if self.is_priv:
            return
        return self.__prototype__

    def get_address(self):
        return self

    def set_address(self):
        self = self.__prototype__['value']
        return

    def copy_address(self):
        return deepcopy(self)

    copy = copy_address

    def pointer_get(self):
        if self.is_pointer:
            return self.__prototype__['value'].value
        else:
            raise MemoryError(f'{self.name} doesnt Pointer')

    def pointer_set(self, value):
        if self.is_pointer:
            check_types(value, self.value.type)
            self.value.value = value
        else:
            raise MemoryError(f'{self.name} doesnt Pointer')
