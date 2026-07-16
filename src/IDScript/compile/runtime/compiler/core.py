"""AST visitor and runtime evaluator for IDScript."""

from typing import Any
import builtins

from ...ids_ast import GenericParam, Program, Top, Block, Statement, Dynamic, Name
from ...exceptions import IDSError
from ...diagnostics import (
    IDSRuntimeError,
    IDSValueError,
    annotate_exception,
    get_source,
    runtime_exception,
)
from ..scope import GlobalScope
from ..control import Throw, Return, Break, Continue
from ..types import EMPTY, IniType
from ..config import Config


class Compiler:
    def __init__(self, file, is_module=False):
        self.v = self.visit
        self._handler_cache = {}

        self.global_scope = GlobalScope()
        self.current_scope = self.global_scope
        self.config = Config(file, is_module)

        self._expected_type = None
        self._expected_name = None

        from ...builtin import ALL
        for n, t, v in ALL:
            self.global_scope.declare(n, t, v, True, True)

        self.global_scope.declare(
            'BERKAS',
            str,
            self.config.path() if self.config.is_module() else 'utama',
            True,
            True,
        )

    def visit(self, __node):
        node_type = type(__node).__name__
        method = self._handler_cache.get(node_type)
        if method is None:
            method = builtins.getattr(self, node_type, self._undefined_node)
            self._handler_cache[node_type] = method
        try:
            return method(__node)
        except (Return, Throw, Break, Continue):
            raise
        except IDSRuntimeError as error:
            raise annotate_exception(error, get_source(__node)) from error
        except IDSError as error:
            raise annotate_exception(error, get_source(__node)) from error
        except Exception as error:
            span = get_source(__node)
            annotated = annotate_exception(error, span)
            raise runtime_exception(annotated, span=span, file=self.config.path()) from error

    def _undefined_node(self, __node):
        raise IDSValueError(f'Node/token {type(__node).__name__!r} belum didefinisikan')

    def _set_expected(self, type_node_or_name, concrete_type=None):
        """Set expected type context for inference of bare generic names."""
        if concrete_type is not None:
            self._expected_type = concrete_type
            if isinstance(type_node_or_name, str):
                self._expected_name = type_node_or_name
            elif hasattr(type_node_or_name, 'type'):
                inner = type_node_or_name.type
                if isinstance(inner, Dynamic):
                    self._expected_name = inner.name.id
                elif isinstance(inner, Name):
                    self._expected_name = inner.id
                else:
                    self._expected_name = None
            else:
                self._expected_name = None
            return
        inner = type_node_or_name.type if hasattr(type_node_or_name, 'type') else type_node_or_name
        if isinstance(inner, Dynamic):
            self._expected_name = inner.name.id
        elif isinstance(inner, Name):
            self._expected_name = inner.id
        elif isinstance(inner, str):
            self._expected_name = inner
        else:
            self._expected_name = None
        self._expected_type = concrete_type if concrete_type is not None else self.v(type_node_or_name)

    def _clear_expected(self):
        self._expected_type = None
        self._expected_name = None

    def GenericParam(self, node: GenericParam):
        bound = None
        if node.bound:
            bound = self.v(node.bound)
        return {
            'name': node.name.id,
            'bound': bound,
            'default': node.default,
        }

    def Program(self, node: Program):
        try:
            if node.bodies:
                for body in node.bodies:
                    self.v(body)
        except ImportError:
            raise
        except IDSRuntimeError:
            raise
        except Exception as e:
            raise IDSRuntimeError.from_exception(e, file=self.config.path()) from e

    def Top(self, node: Top):
        return self.v(node.body)

    def Block(self, node: Block):
        for body in node.bodies or []:
            self.v(body)

    def Statement(self, node: Statement):
        if node.body:
            return self.v(node.body)
