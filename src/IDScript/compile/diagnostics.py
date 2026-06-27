"""Compatibility re-export for IDScript diagnostics and exceptions."""

try:
    from ..IDScript.exceptions import *
except ModuleNotFoundError:
    from ..exceptions import *
