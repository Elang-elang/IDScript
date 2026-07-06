"""Entrypoint for parsing, compiling, and running IDScript source code."""

from lark import Lark
from lark import UnexpectedInput
from pathlib import Path
from typing import cast
from .parser import Parse
from .runtime import Compiler
from .ids_ast import Program
from .diagnostics import IDSAttributeError, IDSSyntaxError


BASE_DIR = Path(__file__).resolve().parent

_PARSER: Lark | None = None

def _get_parser() -> Lark:
    global _PARSER
    if _PARSER is None:
        _PARSER = Lark(
            (BASE_DIR.parent / 'gramm.lark').read_text(),
            parser='earley',
            ambiguity='resolve',
            propagate_positions=True,
        )
    return _PARSER


class Compile:
    def __init__(
        self,
        code: str,
        file: str | Path= "<idscript input>",
        is_module: bool = False
    ):
        self.__compiler__ = self.make_interpreter(file, is_module)
        self.__raw_code__ = cast(Program, self.ast(code, file))
        self.__code__ = self.__compiler__.Program(self.__raw_code__)
    
    @staticmethod
    def ast(
        code: str,
        file: str | Path = "<idscript input>"
    ):
        parser = _get_parser()
        try:
            tree = parser.parse(code)
            return Parse(tree, str(file), source=code)
        except UnexpectedInput as err:
            raise IDSSyntaxError.from_lark(err, str(file), code) from err
    
    @staticmethod
    def make_interpreter(
        file: str | Path = "<idscript input>",
        is_module: bool = False
    ):
        return Compiler(str(file), is_module=is_module)

    def _run_func(self, name, *args):
        func = self.__compiler__.current_scope.get(name)
        if func is None:
            raise IDSAttributeError(f"Fungsi {name!r} tidak ditemukan pada scope global")
        
        if not args:
            return func()
        if args and name == 'utama':
            raise IDSAttributeError("Fungsi utama tidak menerima argumen")
        
        if not args:
            return func()
        return func(*args)

    def sefty_run(self, name, *args):
        try:
            return self._run_func(name, *args)
        except Exception as e:
            print(f"Terjadi kesalahan saat menjalankan {name!r}: {str(e)}")

    def run(self, name, *args): return self._run_func(name, *args)
    def test(self, name, *args): return self.sefty_run(name, *args)

    def main(self, sefty: bool = False):
        if sefty:
            exit(self.sefty_run('utama'))
        
        return self.run('utama')
    
    def exports(self):
        return self.__compiler__.global_scope.exports()

def main():
    res = Compile((BASE_DIR.parent.parent.parent / 'Example/main.ids').read_text(), 'main.ids')
    return res
if __name__ == "__main__":
    main().main()
