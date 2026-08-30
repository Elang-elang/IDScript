from ..ast_nodes               import *
from ...properties.IDSObject   import (
                                        Structure,     MethodSystem,
                                        Function,      Method,
                                        Property,
                                        NameOperation,              )
from ...properties.TypeSystem  import   CheckType,     TypeFunction
from ...properties.Scoping     import   NameSpace

from typing import Any

# constanta
compare_ops = {
    'eq':      NameOperation.eq,
    'ne':      NameOperation.ne,
    'gt':      NameOperation.gt,
    'ge':      NameOperation.ge,
    'lt':      NameOperation.lt,
    'le':      NameOperation.le,
    'in':      NameOperation.in_,
    'not_in':  NameOperation.not_in,
    'is':      NameOperation.is_,
    'is_not':  NameOperation.is_not,
}

bin_ops = {
    'add':  NameOperation.add,
    'sub':  NameOperation.sub,
    'mul':  NameOperation.mul,
    'div':  NameOperation.truediv,
    'pow':  NameOperation.pow,
}




def visit_UnaryOp(
    self,
    node: UnaryOp,
    /,
    
) -> bool:
    operand = self.visit(node.operand)
    return NameOperation.not_(operand)


def visit_BoolOp(
    self,
    node: BoolOp,
    /,
    
) -> int | Any:
    op     = node.op
    values = [ self.visit(value)
               for value in node.values ]
    
    match op:
        case 'or':
            res = NameOperation.or_(values[0], values[1])
        
        case 'and':
            res = values[0] and values[1]

    if res is True or \
       res is False or \
       res is None:
        return int(res)
    
    return res


def visit_Compare(
    self,
    node: Compare,
    /,
    
) -> int:
    left  = self.visit(node.left)
    ops   = node.ops
    comparators = [ self.visit(comp)
                    for comp in node.comparators ]

    res = True
    for i, comp in enumerate(comparators):
        func = compare_ops[ops[i]]
        res  = res and func(left, comp)
        left = comp

    return int(res)

def visit_BinOp(
    self,
    node: BinOp,
    /,
    
) -> Any:
    left  = self.visit(node.left)
    op    = node.op
    right = self.visit(node.right)
    func  = bin_ops[op]
    return func(left, right)


def visit_FunctionExpression(
    self,
    node: FunctionExpression,
    /,
    
) -> Function:
    name   = '<anonim>'
    fields = self.visit(node.params)
    type   = self.visit(node.type)

    def wrapp_handler_stmt():
        for stmt in node.body:
            self.visit(stmt)

    function = Function(
        name,
        fields,
        wrapp_handler_stmt,
        type,
        config=self.config,
    )

    return function


def visit_CallFunction(
    self,
    node: CallFunction,
    /,
    
) -> Any:
    func = self.visit(node.func)
    args = [ self.visit(arg)
             for arg in node.args ]

    
    CheckType(func, (Function.__origin__, Method.__origin__), soft=False)
    return func(*args)


def visit_CallStructure(
    self,
    node: CallStructure,
    /,
    
) -> Structure:
    struct = self.visit(node.struct)
    kwds   = { name: self.visit(value)
                     for name, value in node.kwargs.items() }

    # print(struct)
    CheckType(struct, Structure, soft=False)
    res = struct(**kwds)
    return res
        

def visit_Attribute(
    self,
    node: Attribute,
    /,
    
) -> Any:
    value = self.visit(node.value)
    this  = MethodSystem.Get(value, node.attr)
    return this


def visit_Index(
    self,
    node: Index,
    /,
    
) -> Any:
    value = self.visit(node.value)
    key   = self.visit(node.key)
    return MethodSystem.ForceGet(value, 'ambil_item')(key)


def visit_String(
    self,
    node: String,
    /,
    
) -> str:
    return node.strings

def visit_Integer(
    self,
    node: Integer,
    /,
    
) -> int:
    return int(node.numbers)

def visit_Float(
    self,
    node: Float,
    /,
    
) -> float:
    return float(node.numbers)

def visit_Boolean(
    self,
    node: Boolean,
    /,
    
) -> int:
    return int(node.cond)


HANDLES = [
    func
    for name, func in globals().items()
    if name.startswith('visit_')
]