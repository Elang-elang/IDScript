"""Small low-level helpers used by IDScript runtime objects."""

from .types import EMPTY
from pathlib import Path

def getattr(cls, name, default=EMPTY, /):
    try:
        return object.__getattribute__(cls, name)
    except AttributeError:
        if default is EMPTY:
            raise
        return default

def setattr(cls, name, value, /):
    return object.__setattr__(cls, name, value)

def hasattr(cls, name, /):
    try:
        getattr(cls, name)
        return True
    except AttributeError:
        return False

class Config:
    def __init__(
        self,
        filepath: str | Path = '<memory>',
        is_modulefile: bool = False,
        /,
    ):
        self._struct_name: str | None = None
        self._infunc: bool = False
        self._inloop: bool = False
        self._filepath: Path = Path(filepath)
        self._is_modulefile: bool = is_modulefile
        self._stack_struct_name: list = [None]
        self._stack_infunc: list[bool] = []
        self._stack_inloop: list[bool] = []

    def enter_struct(self, name):
        previous = self._struct_name
        self._struct_name = name
        self._stack_struct_name.append(previous)

    def leave_struct(self):
        previous_stack = self._stack_struct_name.pop(-1)
        self._struct_name = previous_stack

    def enter(self, name):
        self.enter_struct(name)

    def leave(self, previous=None):
        self.leave_struct()

    def is_struct_name(self, name: str | None):
        return self._struct_name == name

    def enter_func(self):
        self._stack_infunc.append(self._infunc)
        self._infunc = True

    def leave_func(self):
        self._infunc = self._stack_infunc.pop(-1) if self._stack_infunc else False

    def is_infunc(self):
        return self._infunc

    def enter_loop(self):
        self._stack_inloop.append(self._inloop)
        self._inloop = True

    def leave_loop(self):
        self._inloop = self._stack_inloop.pop(-1) if self._stack_inloop else False

    def is_inloop(self):
        return self._inloop

    def is_module(self):
        return self._is_modulefile

    def path(self):
        return str(self._filepath)
    
    filepath = path
    
    @property
    def filename(self):
        return self._filepath.name
    
    @property
    def struct_name(self):
        return self._struct_name if self._struct_name else EMPTY
    
    @property
    def inside_loop(self):
        return self._inloop
    
    @property
    def inside_function(self):
        return self._infunc
    
    def __dict__(self):
        return {
            'filepath': self._filepath,
            'module': self._is_modulefile,
            'stacks': {
                'function': self._stack_infunc,
                'loop': self._stack_inloop,
                'struct_name': self._stack_struct_name
            }
        }
    
    def __repr__(self):
        return f"<Config: {str(self._filepath) if self._is_modulefile else 'Utama'}>"
