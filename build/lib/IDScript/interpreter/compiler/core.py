from ...properties.config              import Configure
from ...properties.Modules.LoadWrapper import Loader
from ..ast_nodes                       import *

from typing   import Any, Literal as Lit
from pathlib  import Path


class Compiler:
    def __init__(
        self,
        file_path: str,
        module:    bool = False,
        
    ) -> None:
        self.config = Configure(file_path, module)
    
    def __repr__(self):
        return repr(self.config)

    
    def visit_Program(
        self,
        node: Program,
        /,
        
    ) -> Any:
        res: Any = None
        for stmt in node.stmts:
            res = self.visit(stmt)

        if res is not None:
            return res

    
    def visit_ModuleLanguage(
        self,
        node: ModuleLanguage,
        /,
        
    ) -> None:
        language = node.name_language
        path = self.config.path.parent / Path(node.module_path)
        if not path.exists():
            raise FileNotFoundError(path)

        part: str = ''
        match language:
            case 'Python':
                if path.suffix != '.py':
                    raise FileExistsError(f'{str(path)} harus berupa file Python')
                part = 'Py'
            case _:
                raise ModuleNotFoundError(f'bahasa yang tidak diketahui atau belum tersedia {language}')

        loader:  Any = Loader[part](path)
        config:  Any = loader.load()

        self.config.scope_name.extend_scope(config.scope_name.global_scope)
        self.config.scope_type.extend_scope(config.scope_type.global_scope)
    
    def visit[T](
        self,
        node: T,
        /,
        
    ) -> Any:
        method = getattr(
            self, f"visit_{type(node).__name__}",
            lambda node: self.__error_node_defined(node)
        )
        # print(f'{node}\n')
        return method(node)
    

    def __error_node_defined[T](
        self,
        node: T,
        /,
    
    ) -> None:
        raise NotImplementedError(f'Tidak ada node {str(node)!r}')