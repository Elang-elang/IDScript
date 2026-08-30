from .__helper    import ( setter,   deleter,
                           GetAttr,  SetAttr  )
from ._Reprer     import   Reprer
from .Scoping     import   Scope,    TypeScope
from .TypeSystem  import   Primitif

from typing   import Any, Literal
from pathlib  import Path
from os       import listdir
from json     import dumps as _d


class Scoping:
    def __init__(self) -> None:
        scope = Scope['Global']()
        SetAttr(self, 'global',   scope)
        SetAttr(self, 'current',  scope)
        SetAttr(self, 'stack',  [scope])

    
    def enter_scope(self) -> None:
        scope     = GetAttr(self,     'current')
        stack     = GetAttr(self,       'stack')
        new_scope = Scope['Local'](parent=scope)
        stack.append(new_scope)
        
        SetAttr(self, 'current',      new_scope)
        SetAttr(self, 'stack',            stack)

    
    def leave_scope(self) -> None:
        # print(object.__getattribute__(self, '__dict__'))
        stack     = GetAttr(self,         'stack')
        stack.pop(-1)
        SetAttr(self, 'current',        stack[-1])

    
    def extend_scope(
        self,
        scope: Scope['Global'],
        *,
        copy:      bool = True,
        filter:    bool = True,
        
    ) -> None:
        self.global_scope.extend_space(
            scope,
            copy   = copy,
            filter = filter,
        )

    
    def __getattr__(
        self,
        name: str,
        /,
        
    ) -> TypeScope | Any:
        if   name in ['current', 'current_scope']:
            return GetAttr(self, 'current')
        elif name in ['global',   'global_scope']:
            return GetAttr(self, 'global')
        elif name in [
            'enter_scope', 'leave_scope'
        ]:
            return GetAttr(self, name)
        
        raise AttributeError(f'Tidak ada atribut {name!r}')

    
    __setattr__ = setter
    __delattr__ = deleter

    
    def __repr__(self) -> str:
        return f'Scoping {repr(self.global_scope)}'


class Configure:
    def __init__(
        self,
        path:   str | Path,
        module:       bool,
        
    ) -> None:
        self.scope_name: Scoping = Scoping()
        self.scope_type: Scoping = Scoping()
        self.path:       Path    = Path(path)
        self.filename:   str     = self.path.name
        self.module:     bool    = module
        
        self._stack_inside_function:    list[bool]      = []
        self._stack_inside_loop:        list[bool]      = []
        self._stack_inside_structure:   list[str ]      = []

        self.modules:          dict[str, Path] = {
            '<bawaan>': Path(__file__).parent.parent / 'Builtins',
        }
        
        self.__loader_builtins__()
    

    def __loader_builtins__(self) -> None:
        global_type = self.scope_type.global_scope
        global_name = self.scope_name.global_scope
        types       = Primitif.__value__.__args__
        
        for alias_type in types:
            name_type  = alias_type.__name__
            type_alias = type(alias_type)
            global_type.def_name(
                name_type,
                type_alias,
                alias_type,
                constant=True,
            )
        
        global_type.def_name(
            'Primitif',
            type(Primitif),
            Primitif,
            constant=True,
        )
    
    
    def enter_scope(self) -> None:
        self.scope_name.enter_scope()
        self.scope_type.enter_scope()

    
    def leave_scope(self) -> None:
        self.scope_name.leave_scope()
        self.scope_type.leave_scope()

    
    def enter_func(self) -> None:
        self._stack_inside_function.append(True)

    
    def leave_func(self) -> None:
        self._stack_inside_function.pop(-1)

        
    def enter_loop(self) -> None:
        self._stack_inside_loop.append(True)

    
    def leave_loop(self) -> None:
        self._stack_inside_loop.pop(-1)

    
    def enter_struct(self, name: str) -> None:
        self._stack_inside_structure.append(name)

    
    def leave_struct(self) -> None:
        self._stack_inside_structure.pop(-1)

    
    def extend_scope(
        self,
        scope: Scope['Global'],
        data:  Literal['name', 'type'] = 'name',
        *,
        copy:    bool = True,
        filter:  bool = True,
        
    ) -> None:
        match data:
            case 'type':
                self.scope_type.extend_scope(scope)
            case _:
                self.scope_name.extend_scope(scope)
    
    
    def is_struct(
        self,
        name: str,
        /,
        
    ) -> bool:
        if not self._stack_inside_structure: return False
        return self._stack_inside_structure[-1] == name

        
    def get_module(
        self,
        name: str | None = None,
        /,
        
    ) -> Path:  
        try:
            if name is None:
                return self.path.parent
            
            return self.modules[name]
        
        except KeyError as e:
            raise ModuleNotFoundError(f'Tidak ada jalur modul dari modul {str(name)!r}')

    def to_dict(self) -> dict[str, Any]:
        d = {
            'data_berkas': {
                'jalur_berkas': str(self.path),
                'jalur_induk':  str(self.path.parent),
                'nama_berkas':  self.filename,
                'tipe_berkas': 'modul'
                                if self.module
                                else 'utama'
            },
            'data_modul': {
                'modul_yang_terdaftar': [
                    {
                        'nama':  name,
                        'jalur': str(path),
                    }
                    for name, path in self.modules.items()
                ],
                'modul_berkas_seinduk': [
                    {
                        'nama':  file,
                        'jalur': str(self.path / file),
                    }
                    for i, file in enumerate(listdir(self.path.parent))
                    if Path(file).suffix in ('ids', 'idsm', 'idsc')
                ]
            },
            'data_lingkup': {
                'lingkup_nama': self.scope_name,
                'lingkup_tipe': self.scope_type,
            }
        }
        return d

    def __getattr__(self, name: str, /,) -> Any:
        match name:
            case 'global_name':
                return self.scope_name.global_scope
            case 'current_name':
                return self.scope_name.current_name
            
            case 'global_type':
                return self.scope_type.global_scope
            case 'current_type':
                return self.scope_type.current_name

            case 'inside_function':
                return self._stack_inside_function[-1]
            case 'inside_loop':
                return self._stack_inside_loop[-1]
            case ('inside_structure' | 'inside_struct'):
                return self._stack_inside_structure[-1]

            case _:
                return GetAttr(self, name)

    def __repr__(self) -> str:
        writer_d = _d(self.to_dict(), indent=2, default=repr)
        writer   = f'Interpreter {writer_d}'
        return writer