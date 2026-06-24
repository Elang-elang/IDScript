"""IDScript Compiler - package root."""

import sys
import types

from .runtime import Compiler as _RuntimeCompiler

Compiler = _RuntimeCompiler
__all__ = ["Compile", "Compiler", "Parse"]


def __getattr__(name):
    if name == "Compile":
        from .entrypoint import Compile
        return Compile
    if name == "Parse":
        from .parser import Parse
        return Parse
    if name == "Compiler":
        return _RuntimeCompiler
    raise AttributeError(name)


class _CompilePackage(types.ModuleType):
    def __getattribute__(self, name):
        if name == "Compiler":
            return _RuntimeCompiler
        return super().__getattribute__(name)


sys.modules[__name__].__class__ = _CompilePackage
