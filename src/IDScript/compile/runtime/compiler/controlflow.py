from typing import Any, cast
from ...ids_ast import (
    If, For, While, Try, ExceptionHandler, Switch,
    MatchValue, MatchSingleton, MatchCapture, MatchAs, MatchOr,
    MatchSequence, MatchDots, MatchMapping, MatchStruct, Name,
)
from ...diagnostics import IDSError, IDSValueError, IDSRuntimeError
from ..scope import Scope
from ..control import Throw, Return, Break, Continue


def If(self, node: If):
    if self.v(node.test):
        return self.v(node.body)
    if node.orelse:
        return self.v(node.orelse)


def For(self, node: For):
    iterable = self.v(node.iter)
    for item in iterable:
        parent = self.current_scope
        self.current_scope = Scope(parent=parent)

        self.config.enter_loop()
        try:
            values = item
            if len(node.target) == 1:
                values = [item]
            for index, target in enumerate(node.target):
                value = values[index]
                self.current_scope.declare(
                    target.name.id,
                    self.v(target.type),
                    value,
                    target.constant,
                )
            self.v(node.body)
        except Continue:
            continue
        except Break:
            break
        except:
            raise
        finally:
            self.current_scope = parent
            self.config.leave_loop()
    else:
        if node.orelse:
            return self.v(node.orelse)


def While(self, node: While):
    while self.v(node.test):
        parent = self.current_scope
        self.current_scope = Scope(parent=parent)

        self.config.enter_loop()
        try:
            self.v(node.body)
        except Continue:
            continue
        except Break:
            break
        except:
            raise
        finally:
            self.current_scope = parent
            self.config.leave_loop()
    else:
        if node.orelse:
            return self.v(node.orelse)


def Try(self, node: Try):
    handled = False
    try:
        self.v(node.body)
    except (Throw, IDSError) as err:
        if not node.handler:
            raise
        error = err.args[0] if err.args else IDSRuntimeError('Terjadi kesalahan')
        self._handle_exception(node.handler[0], error)
        handled = True
    except Return:
        raise
    except Exception as err:
        if not node.handler:
            raise
        self._handle_exception(node.handler[0], err)
        handled = True
    else:
        if node.orelse:
            self.v(node.orelse)
    finally:
        if node.finalbody:
            self.v(node.finalbody)
    return handled


def _handle_exception(self, handler: ExceptionHandler, error: Any):
    parent = self.current_scope
    self.current_scope = Scope(parent=parent)
    try:
        self.current_scope.declare(handler.alias.id, Any, error)
        self.v(handler.body)
    finally:
        self.current_scope = parent


def Switch(self, node: Switch):
    subject = self.v(node.subject)
    default_case = None
    for case in node.cases:
        if case.pattern is None:
            default_case = case
            continue
        if self._match_pattern(case.pattern, subject):
            return self.v(case.body)
    if default_case:
        return self.v(default_case.body)


def _bind_name(self, name: Name, value: Any):
    try:
        self.current_scope.set(name.id, value)
    except Exception:
        self.current_scope.declare(name.id, Any, value)


def _match_pattern(self, pattern: Any, value: Any) -> bool:
    if isinstance(pattern, MatchValue):
        if isinstance(pattern.value, Name):
            try:
                return self.v(pattern.value) == value
            except Exception:
                self._bind_name(pattern.value, value)
                return True
        if isinstance(pattern.value, (str, int, float, bool)) or pattern.value is None:
            return pattern.value == value
        return self.v(pattern.value) == value

    if isinstance(pattern, MatchSingleton):
        return value is pattern.value

    if isinstance(pattern, MatchCapture):
        self._bind_name(pattern.name, value)
        return True

    if isinstance(pattern, MatchAs):
        if self._match_pattern(pattern.pattern, value):
            self._bind_name(pattern.name, value)
            return True
        return False

    if isinstance(pattern, MatchOr):
        return any(self._match_pattern(item, value) for item in pattern.patterns)

    if isinstance(pattern, MatchSequence):
        if not isinstance(value, (list, tuple)):
            return False

        dots_indexes = [
            index
            for index, item in enumerate(pattern.patterns)
            if isinstance(item, MatchDots)
        ]
        if not dots_indexes:
            if len(value) != len(pattern.patterns):
                return False
            return all(
                self._match_pattern(item_pattern, value[index])
                for index, item_pattern in enumerate(pattern.patterns)
            )

        if len(dots_indexes) > 1:
            raise IDSValueError('Pattern bongkar ganda belum didukung')

        dots_index = dots_indexes[0]
        before = pattern.patterns[:dots_index]
        after = pattern.patterns[dots_index + 1:]
        if len(value) < len(before) + len(after):
            return False

        for index, item_pattern in enumerate(before):
            if not self._match_pattern(item_pattern, value[index]):
                return False

        offset = len(value) - len(after)
        for index, item_pattern in enumerate(after):
            if not self._match_pattern(item_pattern, value[offset + index]):
                return False

        sequence_dots = cast(MatchDots, pattern.patterns[dots_index])
        self._bind_name(sequence_dots.name, list(value[dots_index:offset]))
        return True

    if isinstance(pattern, MatchMapping):
        if not isinstance(value, dict):
            return False

        remaining = dict(value)
        mapping_dots: MatchDots | None = None
        for key_node, item_pattern in zip(pattern.keys, pattern.patterns):
            if isinstance(item_pattern, MatchDots):
                mapping_dots = item_pattern
                continue

            key = self.v(key_node)
            if key not in value or not self._match_pattern(item_pattern, value[key]):
                return False
            remaining.pop(key, None)
        if mapping_dots:
            self._bind_name(mapping_dots.name, remaining)
        return True

    if isinstance(pattern, MatchStruct):
        cls = self.v(pattern.cls)
        try:
            py_class = object.__getattribute__(cls, '__PY_CLASS__')
        except (AttributeError, TypeError):
            py_class = cls if isinstance(cls, type) else None

        if py_class is None or not isinstance(value, py_class):
            return False

        properties = value.to_dict(include_private=True)
        if not properties:
            return False

        remaining = dict(properties)
        struct_dots: MatchDots | None = None
        for keyword_node, item_pattern in zip(pattern.keys, pattern.patterns):
            if isinstance(item_pattern, MatchDots):
                struct_dots = item_pattern
                continue

            key = self.v(keyword_node)
            if key not in properties or not self._match_pattern(item_pattern, properties[key]):
                return False
            remaining.pop(key, None)
        if struct_dots:
            self._bind_name(struct_dots.name, remaining)
        return True

    if isinstance(pattern, MatchDots):
        raise IDSValueError("Pola bongkar '...' belum didukung sebagai pattern utama")
    return False


HANDLERS = [
    If, For, While, Try, _handle_exception, Switch,
    _bind_name, _match_pattern,
]
