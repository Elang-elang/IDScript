from ..ast_nodes              import *
from ...properties.TypeSystem import TypeFunction as _TF


def visit_TypeAnnotation(
    self,
    node: TypeAnnotation,
    /,

) -> Any:
    # print(self.config.scope_type)
    return self.config.scope_type.current.get_name(node.name.id)


def visit_TypeFunction(
    self,
    node: TypeFunction,
    /,

) -> _TF.__origin__:
    type_params = [ self.visit(param)
                    for param in node.params ]
    return_type = self.visit(node.type)
    
    return _TF(
        type_params = type_params,
        return_type = return_type,
    )


HANDLES = [
    func
    for name, func in globals().items()
    if name.startswith('visit_')
]