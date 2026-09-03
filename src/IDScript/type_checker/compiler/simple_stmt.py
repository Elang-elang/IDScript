from ..ast_nodes                           import   *
from ...properties.TypeSystem              import   TypeField,        TypeStructure
from ...properties.IDSObject               import   Structure,        MethodSystem
from ...properties.__helper                import ( ReturnSignal, ContinueSignal,
                                                    BreakSignal,                  )


def visit_VariableDeclare(
    self,
    node: VariableDeclare,
    /,

) -> None:
    name = node.name.id
    type = self.visit(node.type)
    expr = self.visit(node.expr)
    
    self.config.scope_name.current.def_name(
        name,
        type,
        expr,
    )


def visit_ReturnStatement(
    self,
    node: ReturnStatement,
    /,

) -> None:
    if not self.config.inside_function:
        raise TypeError("'kembalikan' digunakan hanya pada fungsi")

    value = self.visit(node.value)
    raise ReturnSignal(value)


def visit_ContinueStatement(
    self,
    node: ContinueStatement,
    /,
    
) -> None:
    if not self.config.inside_loop:
        raise TypeError("'lanjutkan' digunakan hanya pada perulangan")
    
    raise ContinueSignal()


def visit_BreakStatement(self, node: BreakStatement):
    if not self.config.inside_loop:
        raise TypeError("'hentikan' digunakan hanya pada perulangan")
    raise BreakSignal()


def visit_WriteOut(
    self,
    node: WriteOut,
    /,
    
) -> None:
    obj                = self.visit(node.value)
    writer: str | None = None
    if isinstance(obj, TypeStructure):
        handler   = MethodSystem.ForceGet(obj, 'tulisan')
        writer    = handler()
    else:
        writer = eval(repr(obj))

    return None


def visit_ReadIn(
    self,
    node: ReadIn,
    /,

) -> None:
    this = self.config.current_scope.this_namespace(node.name.id)
        
    if this.type is not str:
        raise TypeError(f'Tipe dari {this.name!r} harus berupa Teks')
    
    if this.constant:
        raise TypeError(f'{this.name} merupakan tidak dapat diubah (konstant)')

    return None


def visit_Name(
    self,
    node: Name,
    /,

) -> Any:
    value = self.config.scope_name.current.get_name(node.id)
    return value


def visit_Parameter(self, node: Parameter):
    if not node.params:
        return []
    fields = [self.visit(param) for param in node.params]
    return fields


def visit_Field(
    self,
    node: Field,
    /,

) -> TypeField:
    d = {
        'name':      node.name.id,
        'type':      self.visit(node.type),
        'private':   True,
        'constant':  False,
    }
    
    if node.private  is not None:
        d['private'] = node.private
    if node.constant is not None:
        d['contant'] = node.constant

    return d



HANDLES = [
    func
    for name, func in globals().items()
    if name.startswith('visit_')
]