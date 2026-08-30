from ..ast_nodes                    import *
from ...properties.__helper.Signals import *


def simple_stmt(self, stmt):
    return stmt


def var_decl(self, name, type, value):
    return VariableDeclare(
        name=name,
        type=type,
        expr=value
    )


def return_stmt(self, value):
    return ReturnStatement(value=value)

def continue_stmt(self):
    return ContinueStatement()


def break_stmt(self):
    return BreakStatement()

def write_stmt(self, expr):
    return WriteOut(value=expr)

def read_stmt(self, name):
    return ReadIn(name=name)

def NAME(self, name):
    return Name(id=str(name))

def params(self, *fields):
    return Parameter(
        params=list(fields)
    )

def field(self, name, type):
    return Field(
        name=name,
        type=type
    )

def public_struct_field(self, field):
    field.private = False
    return field

def private_struct_field(self, field):
    field.private = True
    return field


HANDLES = (
    simple_stmt, var_decl,
    
    return_stmt, continue_stmt,
    break_stmt,
    
    write_stmt, read_stmt,

    public_struct_field,
    private_struct_field,
    NAME, params, field
)