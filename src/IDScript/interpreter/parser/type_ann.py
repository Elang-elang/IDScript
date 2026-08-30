from ..ast_nodes import *


def type_ann(self, name):
    return TypeAnnotation(name=name)

def type_func(self, *types):
    type = types[-1]
    params = types[:-1]
    return TypeFunction(
        params=list(params),
        type=type,
    )


HANDLES = (
    type_ann,
    type_func,
)