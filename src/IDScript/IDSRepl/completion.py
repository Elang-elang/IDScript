from __future__ import annotations

import ast
import time
from typing import Any

from ..compile.runtime.scope import GlobalScope

_SCOPE_CACHE_TTL = 0.5  # seconds — invalidate scope cache after this

_FILTERED_ATTRS: frozenset[str] = frozenset({
    # Python dunder methods (also filtered by startswith('__'))
    '__class__', '__dict__', '__module__', '__annotations__', '__slots__',
    # Old interpreter internal helpers (IDScript Structure/Enum internals)
    'set_method', 'add_method', 'declare', 'add_field',
    'has_field', 'get_field', '_maps', '_scope',
    'getThis', 'get_address', 'copy_address', 'pointer_get', 'pointer_set',
    'is_priv', 'is_const', 'is_pointer', 'export',
    # New VM internal dataclass fields
    'struct', 'values', 'is_module_file', 'variants',
    'code', 'module_key', 'target', 'params',
    'schema', 'enum',
})


def _safe_get_attr(value: Any, name: str) -> Any | None:
    try:
        return getattr(value, name, None)
    except Exception:
        return None


def _get_filtered_attrs(value: Any) -> list[str]:
    names: set[str] = set()
    for attr in dir(value):
        if attr in _FILTERED_ATTRS or attr.startswith('__'):
            continue
        names.add(attr)
    fields = _safe_get_attr(value, 'fields')
    if isinstance(fields, dict):
        for fname in fields:
            if not fname.startswith('_'):
                names.add(fname)
    methods = _safe_get_attr(value, 'methods')
    if isinstance(methods, dict):
        for mname in methods:
            if not mname.startswith('_'):
                names.add(mname)
    return sorted(names)


# Maps IDScript type names → Python types for attribute resolution
_TYPE_ALIASES: dict[str, Any] = {
    'Angka': int,
    'Teks': str,
    'Float': float,
    'Boolean': bool,
    'Kosong': type(None),
    'Apapun': Any,
    'daftar': list,
    'kamus': dict,
    'hasil': tuple,
    'Daftar': list,
    'Kamus': dict,
    'benar': True,
    'salah': False,
    'kosong': None,
}


class IDSScopeCompleter:
    def __init__(self, runtime: Any) -> None:
        self._runtime = runtime
        self._names_cache: dict[str, Any] | None = None
        self._cache_time: float = 0.0

    def collect_scope_names(self) -> dict[str, Any]:
        now = time.monotonic()
        if self._names_cache is not None and (now - self._cache_time) < _SCOPE_CACHE_TTL:
            return self._names_cache
        names: dict[str, Any] = dict(_TYPE_ALIASES)
        if hasattr(self._runtime, 'global_scope'):
            gs = self._runtime.global_scope
            if isinstance(gs, GlobalScope):
                try:
                    for mapping in gs._maps:
                        for key, var in mapping.items():
                            names[key] = var.value
                except Exception:
                    pass
        self._names_cache = names
        self._cache_time = now
        return names

    def complete_prefix(self, prefix: str) -> list[str]:
        if not prefix:
            return []
        return sorted(
            name for name in self.collect_scope_names()
            if name.startswith(prefix)
        )

    def ghost_suggestion(self, text: str) -> str | None:
        word = self.last_word(text)
        if not word:
            return None
        matches = self.complete_prefix(word)
        if len(matches) == 1 and matches[0] != word:
            return matches[0][len(word):]
        return None

    def last_word(self, text: str) -> str:
        text = text.rstrip()
        if not text:
            return ''
        dot_pos = text.rfind('.')
        if dot_pos >= 0:
            return text[dot_pos + 1:]
        for i in range(len(text) - 1, -1, -1):
            ch = text[i]
            if not (ch.isalnum() or ch == '_'):
                return text[i + 1:]
        return text

    _SAFE_AST_NODES = frozenset({
        ast.Expression, ast.Expr,
        ast.Name, ast.Attribute, ast.Subscript, ast.Index, ast.Slice,
        ast.Constant, ast.Load, ast.Store,
        ast.List, ast.Tuple, ast.Dict, ast.Set,
        ast.UnaryOp, ast.UAdd, ast.USub, ast.Not, ast.Invert,
        ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv,
        ast.Mod, ast.Pow, ast.LShift, ast.RShift, ast.BitOr, ast.BitXor,
        ast.BitAnd, ast.MatMult,
        ast.BoolOp, ast.And, ast.Or,
        ast.Compare, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE,
        ast.Is, ast.IsNot, ast.In, ast.NotIn,
        ast.IfExp,
    })

    def _resolve_expr(self, expr: str) -> Any:
        names = self.collect_scope_names()
        if expr in names:
            return names[expr]
        if '.' in expr:
            parts = expr.split('.')
            base = self._resolve_expr(parts[0])
            if base is not None:
                current = base
                for part in parts[1:]:
                    try:
                        current = getattr(current, part)
                    except AttributeError:
                        return None
                return current
        try:
            tree = ast.parse(expr, mode='eval')
            for node in ast.walk(tree):
                if type(node) not in self._SAFE_AST_NODES:
                    return None
            code = compile(tree, '<completion>', 'eval')
            return eval(code, {'__builtins__': {}}, names)
        except Exception:
            return None

    def complete_attribute(self, expr: str, attr_prefix: str) -> list[str]:
        value = self._resolve_expr(expr)
        if value is None:
            return []
        attrs = _get_filtered_attrs(value)
        if attr_prefix:
            attrs = [a for a in attrs if a.startswith(attr_prefix)]
        return attrs
