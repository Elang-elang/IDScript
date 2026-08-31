from ..ast_nodes import *



def module_python(self, path):
    return ModuleLanguage(
        name_language='Python',
        module_path=path.strings
    )

def module_javascript(self, path):
    return ModuleLanguage(
        name_language='JavaScript',
        module_path=path.strings
    )

def top_stmt(self, stmt):
    return stmt

def public_name(self, name):
    return PublicStatement(name=name)

def public_stmt(self, stmt):
    if hasattr(stmt, 'private'):
        stmt.private = False
    return stmt

def private_stmt(self, stmt):
    if hasattr(stmt, 'private'):
        stmt.private = True
    return stmt

def compound_stmt(self, stmt):
    return stmt

def block(self, *stmt):
    return BlockStatement(stmts=list(stmt))

def struct_decl(self, name, *fields):
    return StructureDeclare(
        name=name,
        fields=list(fields),
        extended=None,
    )

def impl_stmt(self, name, *funcs):
    return Implementation(
        name=name,
        funcs=list(funcs)
    )

def method_public_decl(self, f):
    f.private = False
    return f

def method_private_decl(self, f):
    f.private = True
    return f

def static_method_decl(self, name, params, type, *stmts):
    return FunctionDeclare(
        name=name,
        params=params,
        type=type,
        body=list(stmts),
        static=True,
    )

def static_method_decl(self, name, params, type, *stmts):
    return FunctionDeclare(
        name=name,
        params=params,
        type=type,
        body=list(stmts),
    )

def const_decl(self, name, type, value):
    return ConstantaDeclare(
        name=name,
        type=type,
        expr=value
    )

def type_decl(self, name, expr):
    return TypeDeclare(
        name=name,
        expr=expr,
    )

def func_decl(self, name, params, type, *stmts):
    return FunctionDeclare(
        name=name,
        params=params,
        type=type,
        body=list(stmts)
    )


def multi_import(self, pather, kwargs):
    return FromImport(
        path=pather[0],
        mark=pather[1],
        **kwargs
    )

def from_import_fields(self, *args):
    arguments = {
        'fields': [],
        'aliases': [],
    }
    for field, alias in args:
        arguments['fields'].append(field)
        arguments['aliases'].append(alias)
    return arguments

def from_field(self, name, alias = None):
    return [name, alias]


def single_import(self, fields):
    return Import(
        **fields
    )

def import_fields(self, *fields):
    arguments = {
        'paths': [],
        'marks': [],
        'aliases': []
    }
    for path, mark, alias in fields:
        arguments['paths'].append(path)
        arguments['marks'].append(mark)
        arguments['aliases'].append(alias)
    return arguments

def import_field(self, pather, alias = None):
    return [*pather, alias]

def builtins_path(self, path):
    return [path, '<bawaan>']

def module_path(self, name, path):
    return [path, name.id]

def normal_path(self, path):
    return [path, None]


HANDLES = (
    module_python, module_javascript,
    top_stmt, compound_stmt,
    public_stmt, private_stmt, public_name,
    struct_decl, impl_stmt,
    method_public_decl, method_private_decl,
    block, const_decl, type_decl, func_decl,
    multi_import, from_import_fields, from_field,
    single_import, import_fields, import_field,
    builtins_path, module_path, normal_path,
)
