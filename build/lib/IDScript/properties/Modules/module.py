from ..__helper   import ( setter,  deleter,
                           GetAttr, SetAttr, )

from .._Reprer    import Reprer
from ..Scoping    import Global

from typing       import Any
from dataclasses  import dataclass
from re           import fullmatch
from pathlib      import Path

# Constanta
NAME_PATTERN = r'[a-zA-Z_][a-zA-Z0-9_]+'


@dataclass
class _Binding:
    path:      Path
    compiler:  Any
    name:      str | None = None

    def resolve_name(self) -> str:
        if self.name is not None:
            return self.name

        resolve_path = str(self.path.name)
        match_name = fullmatch(NAME_PATTERN, resolve_path)
        if match_name:
            result = match_name.group()
            self.name = result
            return result

        raise NameError(f'Tidak ada alias dan penamaan yang valid untuk impor dengan jalur ini {self.path}')

    
    def exists_path(self) -> bool:
        return self.path.exists()

    
    def resolve(self) -> None:
        if not self.exists_path():
            raise FileNotFoundError(f'Berkas tidak ditemukan: {str(self.path)}')

        self.resolve_name()

    
    def compile(self) -> None:
        self.resolve()
        
        code = self.path.read_text()
        script = self.compiler(
            code=code,
            file_path=str(self.path),
            module=True,
        )
        
        script.run()
        return script.compiler.config.global_scope



@Reprer(writer='Modul', posisional_only=True)
class Module:
    def __init__(
        self,
        path:      str | Path,
        compiler:  Any,
        name:      str | None = None,
        /,
        
    ) -> None:
        _bind = _Binding(
            path     = Path(path),
            compiler = compiler,
            name     = name,
        )

        scope = _bind.compile()
        
        SetAttr(self, 'bind',  _bind)
        SetAttr(self, 'scope', scope).export_space()

        
    def __getattr__(
        self,
        name: str,
        /,
        
    ) -> Any:
        bind    = GetAttr(self,  'bind')
        scope   = GetAttr(self, 'scope')
        
        try:
            return scope[name]
        except KeyError:
            raise AttributeError(f'Atribut {name!r} tidak ada pada modul {bind.name}')

    
    __getitem__ = __getattr__
    
    __setattr__ = setter
    __delattr__ = deleter
    __setitem__ = setter
    __delitem__ = deleter

    
    def __iter__(self) -> Any:
        for name, space in GetAttr(self, 'scope').items():
            yield { name: space }

    def __contains__(self, name) -> bool:
        return name in list(iter(self))
    
    def __repr__(self) -> str:
        bind = GetAttr(self, 'bind')
        return f'<Modul {bind.name!r} pada {bind.path!r}>'