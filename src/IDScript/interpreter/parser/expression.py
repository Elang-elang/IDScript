from ..ast_nodes import *
from .__helper   import *
from typing      import Any


def expr(self, expr):
    return expr


# unary op
def _not(self, expr):
    return UnaryOp(
        op='not',  operand=expr
    )


# bool op
def _or(self, *exprs):
    return bool_op('or', *exprs)

def _and(self, *exprs):
    return bool_op('and', *exprs)


# comp op
def eq(self, *exprs):
    return comp_op('eq',  *exprs)

def ne(self, *exprs):
    return comp_op('ne', *exprs)

def le(self, *exprs):
    return comp_op('le',  *exprs)

def ge(self, *exprs):
    return comp_op('ge',  *exprs)

def lt(self, *exprs):
    return comp_op('lt',  *exprs)

def gt(self, *exprs):
    return comp_op('gt',  *exprs)

def _in(self, *exprs):
    return comp_op('in',  *exprs)

def _is(self, *exprs):
    return comp_op('is',  *exprs)

def not_in(self, *exprs):
    return comp_op('not_in', *exprs)

def is_not(self, *exprs):
    return comp_op('is_not', *exprs)


# bin op
def add(self, *exprs):
    return bin_op('add',  *exprs)

def sub(self, *exprs):
    return bin_op('sub',  *exprs)

def mul(self, *exprs):
    return bin_op('mul',  *exprs)

def div(self, *exprs):
    return bin_op('div',  *exprs)

def pow(self, *exprs):
    return bin_op('pow',  *exprs)


# term
def term(self, expr):
    return expr

def tuple_expr(self, expr):
    return expr

def func_expr(self, params, type, *body):
    return FunctionExpression(
        params=params,
        type=type,
        body=list(body),
    )


def call_func(self, func, *args):
    return CallFunction(
        func=func,
        args=list(args)
    )

def call_struct(self, struct, *args):
    kwargs: dict[str, Any] = {}
    previos: Name | None = None
    for i, value in enumerate(args, start=1):
        if i % 2 == 0 and previos is not None:
            kwargs[previos.id] = value
            previos = None
        else:
            previos = value
    
    return CallStructure(
        struct=struct,
        kwargs=kwargs,
    )

def attribute(self, value, attr):
    return Attribute(
        value=value,
        attr=attr.id
    )

def index(self, value, key):
    return Index(
        value=value,
        key=key
    )



# literal / constants
def literal(self, const):
    return const

def STRING(self, string):
    return String(
        strings=eval(string)
    )

def INT(self, numbers):
    return Integer(
        numbers=int(numbers)
    )

def FLOAT(self, numbers):
    return Float(
        numbers=float(numbers)
    )

def BOOLEAN(self, cond):
    return Boolean(
        cond = 1
        if str(cond) == 'benar'
        else 0
    )

HANDLES = (
    expr,

    # unary op / bool op
    _not, _or, _and,

    # comp op
    eq, ne, le, ge, lt, gt,
    _in, _is, not_in, is_not,
    add, sub, mul, div, pow,

    # term
    term, func_expr,
    tuple_expr,

    # subscript
    call_func, attribute,
    index, call_struct,

    # literal
    literal,
    STRING, INT, FLOAT, BOOLEAN
)