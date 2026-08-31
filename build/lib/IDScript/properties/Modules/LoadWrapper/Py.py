from ....WrapperIDS.Python.module  import Module as TYPE_MODULE
from ..._Reprer                    import Reprer

from typing   import Any, Literal
from pathlib  import Path
import importlib.util

def get_module(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(path.name, path)
    if spec is None:
        raise ImportError(f'Tidak ada module pada {str(path)}')
    
    module = importlib.util.module_from_spec(spec)
    if getattr(spec, 'loader', None) is None:
        module.__loader__.exec_module(module)
    
    else:
        spec.loader.exec_module(module)
    
    return module

@Reprer(writer='Loader<Python>', posisional_only=True)
class Python:
    def __init__(
        self,
        path: Path,
        /,
        
    ) -> None:
        if not path.exists():
            raise ModuleNotFoundError(self.path)
        
        self.path = path
        self.code = self.path.read_text()


    def __loader__(self) -> Any:
        namespace: dict[str, Any] = {
            '__file__': str(self.path)
        }
        try:
            module = get_module(self.path)
            namespace.update(module.__dict__)
            
        except Exception as e:
            try:
                raise e
            finally:
                print(f'Kesalahan {self.path}: {e}')
        
        counter = 0
        for key, value in namespace.items():
            if isinstance(value, TYPE_MODULE):
                if key != 'utama':
                    raise TypeError(f'Pemuat modul harus bernama \'utama\'')
                
                counter += 1
            
            if counter > 2:
                raise TypeError(f'Pemuat modul harus dan hanya harus ada 1 saja setiap berkas modul')

        
        utama = namespace['utama']
        result = utama().__loader__()
        return result
    
    def load(self):
        return self.__loader__()
    
    def __repr__(self):
        return f"Loader<Python>({self.path})"
