from typing import Any
from pathlib import Path
from ...ids_ast import FromImport, ImportAttr
from ...diagnostics import IDSModuleError, IDSRuntimeError
from ..control import Throw


class _VMFunctionProxy:
    def __init__(self, vm: Any, module_key: str, name: str, function: Any):
        self._vm = vm
        self._module_key = module_key
        self._name = name
        self._function = function

    def __call__(self, *args: Any) -> Any:
        try:
            state = self._vm._load_module(self._module_key)
            return self._vm._call(self._function, list(args), state, {})
        except IDSRuntimeError:
            raise
        except Exception as error:
            raise IDSRuntimeError.from_exception(error, file=self._module_key) from error

    def __repr__(self) -> str:
        return f'<VMFunction: {self._name}>'


def FromImport(self, node: FromImport):
    path_module_str = node._from
    if path_module_str.startswith('.'):
        path_module = Path(self.config.path()).parent / Path(path_module_str)
    else:
        path_module = Path(__file__).parent.parent.parent.parent / 'builtins' / Path(path_module_str)

    funcs_wrapp = [self.v(wrapp) for wrapp in node._imports]

    if not path_module.exists():
        raise IDSModuleError(f'Modul {str(path_module)!r} tidak ditemukan')

    if path_module.suffix in {'.idsm', '.idsc'}:
        exports = self._compiled_module_exports(path_module)
        for func_wrapp in funcs_wrapp:
            func_wrapp(exports)
        return

    code = path_module.read_text()
    try:
        from ...entrypoint import Compile
        compile = Compile(code, str(path_module), True)
        exports = compile.exports()

        for func_wrapp in funcs_wrapp:
            func_wrapp(exports)
    except Throw as e:
        raise IDSModuleError(f'Terjadi kesalahan di modul {str(path_module)!r}: {str(e)}') from e
    except:
        raise


def _compiled_module_exports(self, path_module: Path):
    from ...Compiler.bytecode import ModuleCode
    from ...Compiler.runtime import VM
    from ...Compiler.runtime.vm import VMFunction

    module = ModuleCode.from_bytes(path_module.read_bytes())
    vm = VM(module)
    exports = {}
    for name, value in vm.exports().items():
        export_value = value
        if isinstance(value, VMFunction):
            export_value = _VMFunctionProxy(vm, module.path, name, value)
        exports[name] = {
            'type': Any,
            'value': export_value,
            'constant': True,
        }
    return exports


def ImportAttr(self, node: ImportAttr):
    name = node.name.id
    is_priv = node.is_priv
    is_const = node.is_const
    static = node.static

    def wrapp(exports):
        if name == '*' and static and not is_const and not is_priv and not node.alias:
            for name_this, this in exports.items():
                self.current_scope.declare(
                    name_this,
                    this['type'],
                    this['value'],
                    this['constant'],
                    False,
                )
            wrapp.name = '*'
            return True

        if name not in exports:
            raise IDSModuleError(f'Nama {name} tidak pernah didefinisikan')
        this = exports[name]

        alias = None
        if node.alias:
            alias = node.alias.id

        if static:
            self.current_scope.declare(
                alias or name,
                this['type'],
                this['value'],
                this['constant'],
                is_priv,
            )
        else:
            self.current_scope.declare(
                alias or name,
                this['type'],
                this['value'],
                is_const,
                is_priv,
            )

        wrapp.name = name
        return True

    return wrapp


HANDLERS = [
    FromImport, _compiled_module_exports, ImportAttr,
]
