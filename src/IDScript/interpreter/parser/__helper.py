from ..ast_nodes import (
    BoolOp, Compare, BinOp
)

def bool_op(op, *exprs) -> BoolOp:
    return BoolOp(
        op     = op,
        values = list(exprs)
    )

def comp_op(op, *exprs) -> Compare:
    ops         = [op]
    left        = exprs[0]
    comparators = [exprs[1]]
    if isinstance(exprs[1], Compare):
        right       = exprs[1]
        ops.extend(right.ops)
        comparators = [right.left, *right.comparators]

    return Compare(
        left        = left,
        ops         = ops,
        comparators = comparators
    )

def bin_op(op, *exprs)  -> BinOp:
    return BinOp(
        left  = exprs[0],
        op    = op,
        right = exprs[1]
    )