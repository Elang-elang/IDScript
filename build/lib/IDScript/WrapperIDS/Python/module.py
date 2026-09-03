from dataclasses import dataclass
from typing      import Any
from pathlib     import Path

from .__helper                                   import check_options, CheckType
from ...properties.IDSObject.Function.function   import Function, TypeFunction
from ...properties.IDSObject.Structure.structure import Structure, StructureObjectType
from ...properties.config                        import Configure
from ...properties.Scoping.namespace             import NameSpace
from .function  import _Binding as _FB
from .structure import _Binding as _SB


@dataclass
class _Binding:
    _config: Configure

    def add_func(self, raw_func: _FB, /) -> None:
        if CheckType(raw_func, _FB):
            func = raw_func.__loader__()
            type = TypeFunction[func.params_type, func.return_type]
            self._config.scope_name.global_scope.def_name(
                func.name,
                type,
                func,
                private=False,
                constant=True,
            )
        
        else:
            raise TypeError(f'Hanya support tipe fungsi dari IDSObject.Python.Function')

    def add_struct(self, raw_struct: _SB) -> None:
        if CheckType(raw_struct, _SB):
            struct = raw_struct.__loader__(self._config)
            self._config.scope_name.global_scope.def_name(
                raw_struct.name,
                StructureObjectType,
                struct,
                private=False,
                constant=True,
            )
            self._config.scope_type.global_scope.def_name(
                raw_struct.name,
                StructureObjectType,
                struct,
                private=False,
                constant=True,
            )
        else:
            raise TypeError(f'Hanya support tipe struktur dari IDSObject.Python.Structure')

    
    def declare(self, name: str, value: Any, /, *, _type: Any = None) -> None:
        resolve_type = _type or type(value)
        
        CheckType(value, resolve_type, soft=False)
        self._config.scope_name.global_scope.def_name(
            name,
            resolve_type,
            value,
            private=False,
            constant=True,
        )

    def __loader__(self) -> Any:
        return self._config


class Module:
    def __init__(self, func: Any) -> Any:
        if func.__qualname__ != 'utama':
            raise NameError(f'Fungsi yang memuat modul harus bernama \'utama\'')
        
        raw_path     = func.__globals__['__file__']
        resolve_path = Path(raw_path)
        self.bind    = _Binding(_config=Configure(
            path     = resolve_path,
            module   = True
        ))
        
        self.func = func
        self.path = resolve_path
        self.func(self.bind)

    def __call__(self):
        return self.bind

    def __repr__(self):
        return f'utama(Module<{str(self.path)}>)'
