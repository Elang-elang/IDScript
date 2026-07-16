from typing import Any
from ...ids_ast import Kembalikan, Kesalahan, Berhentikan, Lanjutkan, Const, Variable, Final, Assignment, Attribute, Index, Name, Deferensial
from ...diagnostics import IDSError, IDSAttributeError, IDSLoopError, IDSTypeError
from ..control import Throw, Return, Break, Continue
from ..types import EMPTY, default_value
from ..variable import Variable as Var


def Kembalikan(self, node: Kembalikan):
    if self.config.is_infunc():
        old_type = self._expected_type
        old_name = self._expected_name
        try:
            raise Return(self.v(node.value))
        finally:
            self._expected_type = old_type
            self._expected_name = old_name
    raise IDSAttributeError('Statement kembalikan hanya dapat digunakan di dalam fungsi')


def Kesalahan(self, node: Kesalahan):
    value = self.v(node.value)
    raise Throw(value)


def Berhentikan(self, node: Berhentikan):
    if self.config.is_inloop():
        raise Break()
    raise IDSLoopError('Statement berhentikan hanya dapat digunakan di dalam loop')


def Lanjutkan(self, node: Lanjutkan):
    if self.config.is_inloop():
        raise Continue()
    raise IDSLoopError('Statement lanjutkan hanya dapat digunakan di dalam loop')


def Const(self, node: Const):
    name = node.name.id
    ann = self.v(node.type)
    old_type = self._expected_type
    old_name = self._expected_name
    self._set_expected(node.type, ann)
    expr = self.v(node.expr) if node.expr else None
    self._expected_type = old_type
    self._expected_name = old_name
    is_priv = node.is_priv
    if node.is_def:
        if not isinstance(expr, Var):
            raise IDSTypeError(f'Konstanta deferensial {name!r} membutuhkan referensial')
        self.current_scope.declare(name, ann, expr, True, is_priv, True)
        return
    self.current_scope.declare(name, ann, expr, True, is_priv, False)


def Variable(self, node: Variable):
    name = node.name.id
    ann = self.v(node.type)
    old_type = self._expected_type
    old_name = self._expected_name
    self._set_expected(node.type, ann)
    expr = self.v(node.expr) if node.expr is not EMPTY else EMPTY
    self._expected_type = old_type
    self._expected_name = old_name
    if expr is EMPTY:
        expr = default_value(ann)
    if node.is_def:
        if not isinstance(expr, Var):
            raise IDSTypeError(f'Variabel deferensial {name!r} membutuhkan referensial')
        self.current_scope.declare(name, ann, expr, False, False, True)
        return
    self.current_scope.declare(name, ann, expr)


def Final(self, node: Final):
    name = node.name.id
    ann = self.v(node.type)
    old_type = self._expected_type
    old_name = self._expected_name
    self._set_expected(node.type, ann)
    expr = self.v(node.expr)
    self._expected_type = old_type
    self._expected_name = old_name
    if node.is_def:
        if not isinstance(expr, Var):
            raise IDSTypeError(f'Final deferensial {name!r} membutuhkan referensial')
        self.current_scope.declare(name, ann, expr, True, True, True)
        return
    self.current_scope.declare(name, ann, expr, True)


def Assignment(self, node: Assignment):
    expr = self.v(node.expr)
    target = None
    if isinstance(node.target, Deferensial):
        pointer = self.current_scope.getThis(node.target.name.id)
        pointer.pointer_set(expr)
    elif isinstance(node.target, Attribute):
        target = self.v(node.target.value)
        attr = node.target.attr
        setattr(target, attr, expr)
    elif isinstance(node.target, Index):
        target = self.v(node.target.value)
        idx = self.v(node.target.key)
        target[idx] = expr
    elif isinstance(node.target, Name):
        target = node.target.id
        self.current_scope.set(target, expr)
    else:
        raise IDSTypeError('Target assignment harus berupa nama, atribut, indeks, atau deferensial')


HANDLERS = [
    Kembalikan, Kesalahan, Berhentikan, Lanjutkan,
    Const, Variable, Final, Assignment,
]
