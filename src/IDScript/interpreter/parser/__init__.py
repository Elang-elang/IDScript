from . import (
    simple_stmt, top_stmt,
    expression, type_ann,
    core,
)

parts = [
    part
    for name, part in globals().items()
    if not name.startswith('_')
    and 'HANDLES' in dir(part)
]


from lark  import v_args

inline = v_args(inline=True)
_p = core.Parser

for mod in parts:
    for fn in mod.HANDLES:
        setattr(
            _p,
            fn.__name__, 
            inline(fn)
        )

class __Parser:
    def __init__(self):
        self._p = _p()
        
    def __call__(self, ctx):
        return self._p.transform(ctx)

    def __repr__(self):
        return 'Parser'

Parser = __Parser()