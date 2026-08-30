from .interpreter        import Compile
#from .type_checker import TypeChecker
from .properties._Reprer import Reprer
from .                   import TOKEN as IDVMToken

@Reprer(writer='Grammar<IDScript>')
class Grammar:
    def __new__(cls) -> str:
        from pathlib import Path
        resolve_path = Path(__file__).parent / 'gramm.lark'
        return resolve_path.read_text()

del Reprer
