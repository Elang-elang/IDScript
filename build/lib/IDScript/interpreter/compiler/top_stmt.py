from ..ast_nodes               import *
from ...properties.IDSObject   import ( Structure, Method,
                                        Function           )
from ...properties.Modules     import   Module
from ...properties.__helper    import   GetAttr
from ...properties.TypeSystem  import   TypeFunction
from pathlib                   import   Path
from typing                    import   Any
from re                        import   fullmatch


def visit_PublicStatement(
    self,
    node: PublicStatement,
    /,

) -> None:
    scope_name = self.config.scope_name
    scope_type = self.config.scope_type
    name_space = scope_name.current.space
    type_space = scope_type.current.space
    
    name    = node.name.id
    is_type = False
    is_name = False
    if name in type_space:
        is_type = True
    
    if name in name_space:
        is_name = True

    if not is_name:
        if not is_type:
            raise TypeError(f'{name!r} merupakan tipe sejati dan tidak boleh diubah')
        
        raise NameError(f'{name!r} tidak pernah ada pada program')

    
    this = name_space.pop(name)
    if not this.private:
        print(f"Peringatan {name!r} merupakan publik semenjak awal")

    
    constant = this.constant
    private  = False
    scope_name.current.def_name(
        this.name,
        this.type,
        this.value,
        constant = constant,
        private  = private,
    )
    
    if is_type:
        type_space.pop(name)
        scope_type.current.def_name(
            this.name,
            this.type,
            this.value,
            constant = constant,
            private  = private,
        )


def visit_StructureDeclare(
    self,
    node: StructureDeclare,
    /,
    
) -> None:
    name   = node.name.id
    fields = [ self.visit(field)
               for field in node.fields ]
    
    extend = node.extended

    struct = Structure(
        name,
        fields,
        config = self.config
    )
    

    self.config.scope_name.current.def_name(
        name,
        Structure,
        struct,
        constant = True,
        private  = node.private
    )
    
    self.config.scope_type.current.def_name(
        name,
        Structure,
        struct,
        constant = True,
        private  = node.private
    )


def visit_Implementation(
    self,
    node: Implementation,
    /,

) -> None:
    struct    = self.visit(node.name)
    prototype = GetAttr(struct, 'PROTOTYPE')

    def wrapper(func):
        for i, stmt in enumerate(func.body):
            self.visit(stmt)

    
    self.config.enter_scope()
    self.config.scope_type.def_name(
        'Ini',
        Any,
        struct,
        private=True,
        constant=True,
    )
    self.config.scope_name.def_name(
        'Ini',
        Any,
        struct,
        private=True,
        constant=True,
    )
    
    for func in node.funcs:
        name        = func.name.id
        fields      = self.visit(func.params)
        return_type = self.visit(func.type)
        GetAttr(prototype, 'def_method')(
            name,
            fields,
            lambda func   = func: wrapper(func),
            return_type,
            static        =  bool(func.static ),
            private       =  bool(func.private),
            cls           =              struct,
        )

    self.config.leave_scope()
    

def visit_ConstantaDeclare(
    self,
    node: ConstantaDeclare,
    /,

) -> None:
    name = node.name.id
    type = self.visit(node.type)
    expr = self.visit(node.expr)

    self.config.scope_name.current.def_name(
        name,
        type,
        expr,
        constant = True,
        private  = node.private
    )

def visit_TypeDeclare(
    self,
    node: TypeDeclare,
    /,

) -> None:
    name = node.name.id
    raw_expr = node.expr

    expr = self.visit(raw_expr)
    if Expression in type(raw_expr).__bases__:
        if type(expr) is not Structure:
            raise TypeError(f'Untuk tipe harus sesuai yakni harus berupa struktur')
    

    self.config.scope_type.current.def_name(
        name,
        Any,
        expr,
        constant = True,
        private  = node.private
    )


def visit_BlockStatement(
    self,
    node: BlockStatement,
    /,
    
) -> Any:
    self.config.enter_scope()
    try:
        res = None
        for stmt in node.stmts:
            res = self.visit(stmt)

        self.config.leave_scope()
        if res is not None:
            return res
    except:
        raise
    
    finally:
        self.config.leave_scope()


def visit_FunctionDeclare(self, node: FunctionDeclare):
    name          = node.name.id
    fields        = self.visit(node.params)
    return_type   = self.visit(node.type)

    def wrapp_handler_stmt():
        for stmt in node.body:
            self.visit(stmt)

    function = Function(
        name,
        fields,
        wrapp_handler_stmt,
        return_type,
        config=self.config,
    )

    params_type = [ t['type']
                    for t in fields ]
    type_func = TypeFunction[ params_type, return_type ]

    self.config.scope_name.current.def_name(
        name,
        type_func,
        function,
        constant = True,
        private  = node.private
    )


def visit_FromImport(
    self,
    node: FromImport,
    /,
    
) -> None:
    from ..compile import Compile
    raw_path       = self.visit(node.path)
    file_path      = Path(raw_path)
    module_path    = self.config.get_module(node.mark)
    fields         = [ field.id
                       for field in node.fields ]
    
    aliases = []
    for alias in node.aliases:
        aliases.append(alias.id if alias else None)
    
    resolve_path = module_path / file_path
    

    if not resolve_path.exists():
        raise ModuleNotFoundError(f'Tidak ada modul berkas {str(resolve_path)}')

    if resolve_path.is_dir():
        dir_path = resolve_path
        resolve_path /= "utama.ids"
        if not resolve_path.exists():
            raise ModuleNotFoundError(f'Tidak ada modul berkas utama pada folder ini: {str(dir_path)}')
    
    code = resolve_path.read_text()
    compiler = Compile(
        code=code,
        file_path=str(resolve_path),
        module=True,
    )
    compiler.run()

    this_config = compiler.compiler.config
    scope_name  = this_config.scope_name
    scope_type  = this_config.scope_type
    export_name = scope_name.global_scope.export_space()
    export_type = scope_type.global_scope.export_space()

    for i, field in enumerate(fields):
        if field in export_name:
            space = export_name[field]
            self.config.scope_name.current.def_name(
                aliases[i] or space.name,
                space.type,
                space.value,
                constant=space.constant,
                private=False
            )
        
            if field in export_type:
                space = export_type[field]
                self.config.scope_type.current.def_name(
                    aliases[i] or space.name,
                    space.type,
                    space.value,
                    constant=space.constant,
                    private=False
                )
            continue
        
        raise AttributeError(f'Tidak ada nama {field!r} pada {str(resolve_path)!r}')


def visit_Import(self, node: Import):
    from ..compile import Compile
    paths = [ self.visit(path)
              for path in node.paths ]
    marks = node.marks
    
    aliases = []
    for alias in node.aliases:
        aliases.append( alias.id
                        if   alias
                        else None  )

    for i, raw_path  in enumerate(paths):
        file_path    = Path(raw_path)
        
        module_path  = self.config.get_module(marks[i])
        resolve_path = module_path / file_path
        if not resolve_path.exists():
            raise ModuleNotFoundError(f'Tidak ada modul berkas {str(resolve_path)}')

        if resolve_path.is_dir():
            dir_path = resolve_path
            resolve_path /= "utama.ids"
            if not resolve_path.exists():
                raise ModuleNotFoundError(f'Tidak ada modul berkas utama pada folder ini: {str(dir_path)}')
            
            if not aliases[i]:
                match_name = fullmatch(r'[a-zA-Z_][a-zA-Z0-9_]+', dir_path.name)
                if match_name:
                    aliases[i] = match_name.group()
                else:
                    raise NameError(f'Nama folder yang tidak relevan {dir_path.name}. Solusinya: berikan saja alias')
    
        module: Module = Module( resolve_path, compile )
        bind           = GetAttr( module, 'bind')
        
        self.config.scope.def_name(
            aliases[i] or bind.name,
            Module,
            module,
            constant=True,
            private=False
        )


HANDLES = [
    func
    for name, func in globals().items()
    if name.startswith('visit_')
]