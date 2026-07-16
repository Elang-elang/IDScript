import types as pytypes
from typing import Any, Optional, get_origin
import builtins
import operator
from ...ids_ast import (
    Expression, UnaryOp, BoolOp, Compare, BinOp, Attribute, Index,
    Call, CallDynamic, Info, Referensial, Deferensial, SalinReferensial,
    StructFielded, Constant, Daftar, Kamus, ExprFunc,
)
from ...diagnostics import IDSAttributeError, IDSTypeError
from ..structure import Structure as Struct
from ..function import Function as RuntimeFunction
from ..enum import EnumValue, StructVariant, TupleVariant
from .modules import _VMFunctionProxy


def Expression(self, node: Expression):
    return self.v(node.value)


def UnaryOp(self, node: UnaryOp):
    return not self.v(node.operand)


def BoolOp(self, node: BoolOp):
    op = node.op
    values = [self.v(value) for value in node.values]
    match op:
        case 'or':
            return values[0] or values[1]
        case 'and':
            return values[0] and values[1]


def Compare(self, node: Compare):
    left = self.v(node.left)
    ops = node.ops
    comparators = [self.v(comp) for comp in node.comparators]
    compare_ops = {
        '==': operator.eq,
        '!=': operator.ne,
        '>': operator.gt,
        '>=': operator.ge,
        '<': operator.lt,
        '<=': operator.le,
        'in': lambda a, b: a in b,
        'not in': lambda a, b: a not in b,
        'is': operator.is_,
        'is not': operator.is_not,
    }

    res = True
    for i, comp in enumerate(comparators):
        res = res and compare_ops[ops[i]](left, comp)
        left = comp

    return res


def BinOp(self, node: BinOp):
    left = self.v(node.left)
    op = node.op
    right = self.v(node.right)
    bin_ops = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
        '**': operator.pow,
    }
    return bin_ops[op](left, right)


def Attribute(self, node: Attribute):
    val = self.v(node.value)
    attr = node.attr
    return builtins.getattr(val, attr)


def Index(self, node: Index):
    val = self.v(node.value)
    key = self.v(node.key)
    return val[key]


_CALLABLE_TYPES = (
    RuntimeFunction, _VMFunctionProxy,
    pytypes.FunctionType, pytypes.BuiltinFunctionType,
    pytypes.MethodType, pytypes.BuiltinMethodType,
    pytypes.LambdaType, type,
    EnumValue, StructVariant, TupleVariant,
)


def Call(self, node: Call):
    func = self.v(node.func)
    if not callable(func):
        raise IDSTypeError(f'{func} bukanlah sebuah fungsi/metode')
    if not node.args and not node.generic:
        return func()
    args = [self.v(arg) for arg in node.args]
    if not node.generic:
        return func(*args)
    generic = [self.v(arg) for arg in node.generic]
    return func(
        arguments=args,
        generic_params=generic
    )


def CallDynamic(self, node: CallDynamic):
    name = self.v(node.name)
    type_args = [self.v(ta) for ta in node.type_args]
    factory = getattr(name, '__generic_factory__', None)
    if factory is not None:
        return factory(*type_args)
    raise IDSTypeError(f'{node.name.id} bukan tipe generik')


def Info(self, node: Info):
    value = self.current_scope.get(node.name.id)
    return self._info_name(value)


def Referensial(self, node: Referensial):
    return self.current_scope.getThis(node.name.id)


def Deferensial(self, node: Deferensial):
    return self.current_scope.getThis(node.name.id).pointer_get()


def SalinReferensial(self, node: SalinReferensial):
    variable = self.current_scope.getThis(node.name.id)
    if variable.is_pointer:
        return variable.value
    return variable.copy_address()


def _info_name(self, value: Any) -> str:
    from ..enum import Enum, EnumValue, StructVariant, TupleVariant

    if value is None:
        return 'Kosong'
    if isinstance(value, bool):
        return 'Boolean'
    if isinstance(value, int):
        return 'Angka'
    if isinstance(value, float):
        return 'Float'
    if isinstance(value, str):
        return 'Teks'
    if isinstance(value, list):
        return 'Daftar'
    if isinstance(value, dict):
        return 'Kamus'
    if isinstance(value, Enum):
        return 'Enum'
    if isinstance(value, (EnumValue, StructVariant, TupleVariant)):
        return 'VarianEnum'
    if isinstance(value, Struct) or (
        hasattr(value, '__PROTOTYPE__') and hasattr(value, '__FIELDS__')
    ):
        return 'Struktur'
    if isinstance(value, type) and hasattr(value, '__annotations__') and hasattr(value, '__total__'):
        return 'Antarmuka'
    if isinstance(value, type) or get_origin(value) is not None:
        return 'Tipe'
    if callable(value) or 'Function' in repr(value) or 'Method' in repr(value):
        return 'Fungsi'
    return 'Objek'


def StructFielded(self, node: StructFielded):
    struct = self.v(node.struct)
    kwargs = self.v(node.kwargs)

    if node.type_args:
        factory = getattr(struct, '__generic_factory__', None)
        if factory is not None:
            type_args = [self.v(ta) for ta in node.type_args]
            struct = factory(*type_args)

    if type(struct) is not Struct:
        raise IDSAttributeError(f'{str(struct)} bukan struktur')

    return struct(**kwargs)


def Constant(self, node: Constant):
    return node.value


def Daftar(self, node: Daftar):
    if not node.elts:
        return []
    return [self.v(v) for v in node.elts]


def Kamus(self, node: Kamus):
    if not node.keys and not node.values:
        return {}
    keys = [self.v(k) for k in node.keys]
    values = [self.v(v) for v in node.values]
    res = {}
    for i, key in enumerate(keys):
        res[key] = values[i]
    return res


def ExprFunc(self, node: ExprFunc):
    name = '<anonim>'
    return_type = self.v(node.attrs.type)
    body = node.body.bodies or []

    generic_params = []
    if names := node.attrs.generic:
        generic_params = [name.id for name in names]

    fn = RuntimeFunction(
        self, name, return_type, body, None,
        generic_params,
        is_method=False,
        lexical_parent=None,
        args_node=node.attrs.args,
        type_node=node.attrs.type,
    )
    return fn


HANDLERS = [
    Expression, UnaryOp, BoolOp, Compare, BinOp, Attribute, Index,
    Call, CallDynamic, Info, Referensial, Deferensial, SalinReferensial,
    _info_name, StructFielded, Constant, Daftar, Kamus, ExprFunc,
]
