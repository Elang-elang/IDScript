from ..ast_nodes import *
from lark        import Transformer

class Parser(Transformer):
    pass

def prog(self, *stmt):
    return Program(stmts=list(stmt))

def sub_prog(self, stmt):
    return stmt
    
def stmt(self, stmt):
    return stmt

HANDLES = (
    prog, sub_prog, stmt
)