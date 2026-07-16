from .core import Compiler
from . import statements
from . import declarations
from . import controlflow
from . import expressions
from . import modules
from . import names

for _mod in (statements, declarations, controlflow, expressions, modules, names):
    for _fn in _mod.HANDLERS:
        setattr(Compiler, _fn.__name__, _fn)
