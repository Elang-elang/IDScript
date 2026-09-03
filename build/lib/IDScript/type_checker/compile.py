from lark import Lark
from typing import cast
from pathlib import Path
from .compiler import Compiler
from ..interpreter.parser import Parser
from ..interpreter.ast_nodes import Program

GRAMMAR = Path(__file__).parent.parent / "gramm.lark"

PARSER = Lark(
    GRAMMAR.read_text(),
    start='prog',
    ambiguity="resolve",
    propagate_positions=True,
)

class Compile:
    def __init__(
        self,
        *,
        code:      str,
        file_path: str,
        module:    bool
    ):
        self.__compiler__ = self.get_interp(
            file_path, module
        )
        self.__ctx__ = cast(
            Program, self.get_ast(code)
        )

    @property
    def compiler(self):
        return self.__compiler__
    
    @staticmethod
    def get_ast(code):
        global PARSER
        ctx = PARSER.parse(code)
        return Parser(ctx)

    @staticmethod
    def get_interp(file, is_module=False):
        return Compiler(str(file), is_module)

    def run(self):
        return self.__compiler__.visit(self.__ctx__)

    def run_func(self, name: str, *args) -> None:
        self.__compiler__.config.scope_name.global_scope.get_name(name)(*args)
