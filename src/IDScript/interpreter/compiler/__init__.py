from . import (
    simple_stmt, top_stmt,
    expression, type_ann, 
)

parts = [
    part
    for name, part in globals().items()
    if not name.startswith('_')
    and 'HANDLES' in dir(part)
]

from .core import Compiler as _c
for mod in parts:
    for fn in mod.HANDLES:
        if fn.__name__.startswith('visit_'):
            setattr(_c, fn.__name__, fn)

Compiler = _c
