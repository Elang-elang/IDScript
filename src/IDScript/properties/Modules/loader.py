from ..__helper  import setter, deleter
from .._Reprer   import Reprer

from pathlib  import Path
from typing   import Type, Any
from json     import load as _jloader


@Reprer(writer='Jalur')
class Pather:
    def __init__(
        self,
        path: str | Path,
        /, *,
        module: str | None = None,
        config: 'Configure',
        
    ) -> None:
        resolve_path = Path(path)
        if module is not None:
            resolve_path = Path(config.get_path(module)) / resolve_path

        self.path = resolve_path

    def load(self) -> Any:
        if self.path.suffix == '.json':
            return _jloader(self.path.open())
        
        return self.text()

    def text(self) -> str:
        return self.path.read_text()

    def __repr__(self):
        return f'<Jalur {str(self.path)!r}>'