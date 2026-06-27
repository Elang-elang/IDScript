"""Convert IDScript source text into the shared IDScript AST."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from lark import Lark

from ...ids_ast import Program
from ...parser import Parse


GRAMMAR_FILE = Path(__file__).resolve().parents[3] / "gramm.lark"


def parse_source(code: str, file: str = "<memory.ids>") -> Program:
    parser = Lark(GRAMMAR_FILE.read_text(), parser="earley", ambiguity="resolve", propagate_positions=True)
    return cast(Program, Parse(parser.parse(code), file=file))
