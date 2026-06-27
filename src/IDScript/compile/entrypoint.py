"""Entrypoint for parsing, compiling, and running IDScript source code."""

from lark import Lark
from lark import UnexpectedInput
from pathlib import Path
from typing import cast
from .parser import Parse
from .runtime import Compiler
from .ids_ast import Program
from .diagnostics import IDSSyntaxError


BASE_DIR = Path(__file__).resolve().parent

class Compile:
    def __init__(self, code, file: str | Path, is_module=False):
        self.parser = Lark(
            (BASE_DIR.parent / 'gramm.lark').read_text(),
            parser='earley',
            ambiguity='resolve',
            propagate_positions=True,
        )
        self.__compiler__ = Compiler(str(file), is_module=is_module)
        try:
            self.__tree = self.parser.parse(code)
        except UnexpectedInput as err:
            raise IDSSyntaxError.from_lark(err, str(file), code) from err
        self.__raw_code__ = cast(Program, Parse(self.__tree, file=str(file)))
        self.__code__ = self.__compiler__.Program(self.__raw_code__)
    
    def _run_func(self, name, *args):
        func = self.__compiler__.current_scope.get(name)
        if func is None:
            raise AttributeError(f"Function {name!r} not found on global scope")
        
        if not args:
            return func()
        if args and name == 'utama':
            raise AttributeError("Main Function (fungsi utama) doesn't arguments!")
        
        if not args:
            return func()
        return func(*args)

    def sefty_run(self, name, *args):
        try:
            return self._run_func(name, *args)
        except Exception as e:
            print(f"Something was wrong at {name!r}: {str(e)}")

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
