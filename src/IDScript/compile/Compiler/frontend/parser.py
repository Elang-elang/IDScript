"""Convert IDScript source text into the shared IDScript AST."""

from __future__ import annotations

from pathlib import Path
from typing import cast
from lark import Lark


from ...ids_ast import Compare, CallDynamic, StructFielded, Name, Kamus, Program
from ...parser import Parse


GRAMMAR_FILE = Path(__file__).resolve().parents[3] / "gramm.lark"

_PARSER: Lark | None = None


def _get_parser() -> Lark:
    global _PARSER
    if _PARSER is None:
        _PARSER = Lark(
            GRAMMAR_FILE.read_text(),
            parser="earley",
            ambiguity="resolve",
            propagate_positions=True,
        )
    return _PARSER


def _fix_generic_ambiguity(node):
    """Post-processing: convert Compare nodes that look like generic instantiation patterns.

    Pattern 1 (StructFielded): Compare(Compare(Name < T), ['>'], [Kamus|Attribute(Kamus)])
      → StructFielded(Name, Kamus, type_args=[T])

    Pattern 2 (CallDynamic): Compare(Name, ['<'], [T])
      → CallDynamic(Name, type_args=[T])
    """
    if isinstance(node, Compare):
        if isinstance(node.left, Compare):
            inner = node.left
            if (isinstance(inner.left, Name) and
                inner.ops == ['<'] and len(inner.comparators) == 1 and
                node.ops == ['>'] and len(node.comparators) == 1):
                from ...ids_ast import Attribute as AstAttribute
                c0 = node.comparators[0]
                if isinstance(c0, Kamus):
                    node = StructFielded(
                        struct=inner.left,
                        kwargs=c0,
                        type_args=[inner.comparators[0]]
                    )
                elif isinstance(c0, AstAttribute) and isinstance(c0.value, Kamus):
                    from ...ids_ast import Attribute as AstAttribute2
                    node = AstAttribute2(
                        value=StructFielded(
                            struct=inner.left,
                            kwargs=c0.value,
                            type_args=[inner.comparators[0]]
                        ),
                        attr=c0.attr
                    )
                else:
                    pass  
        elif (isinstance(node.left, Name) and
              node.ops == ['<'] and len(node.comparators) == 1 and
              isinstance(node.comparators[0], Name) and
              node.left.id[0].isupper() and node.comparators[0].id[0].isupper()):
            node = CallDynamic(
                name=node.left,
                type_args=[node.comparators[0]]
            )
    if isinstance(node, (list, tuple)):
        return [_fix_generic_ambiguity(item) for item in node]
    if hasattr(node, '__dataclass_fields__'):
        for attr_name in vars(node):
            old_val = getattr(node, attr_name)
            new_val = _fix_generic_ambiguity(old_val)
            if new_val is not old_val:
                setattr(node, attr_name, new_val)
    return node


def parse_source(code: str, file: str = "<memory.ids>") -> Program:
    parser = _get_parser()
    result = Parse(parser.parse(code), file=file, source=code)
    result = _fix_generic_ambiguity(result)
    return cast(Program, result)
