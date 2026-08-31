class TOKEN_ELEMENT:
    def __getattr__(self, name: str, /) -> str:
        if name in ['python', 'alias', 'idscript']:
            return object.__getattribute__(self, name)
        
        raise AttributeError(f'Tidak ada atribut {name}')

    
    def __setattr__(self, name: str, value: object) -> None:
        raise PermissionError(f'Tidak ada izin untuk mengganti isi atribut')

    
    def __delattr__(self, name: str, /) -> None:
        raise PermissionError(f'Tidak ada izin untuk menghapud isi atribut')


class TOKEN_PY_NAME(TOKEN_ELEMENT):
    def __init__(self, python: str, alias: str, idscript: str):
        object.__setattr__(self, 'python',     python)
        object.__setattr__(self, 'alias',       alias)
        object.__setattr__(self, 'idscript', idscript)

    def __repr__(self):
        return self.python


class TOKEN_IDS_NAME(TOKEN_ELEMENT):
    def __init__(self, python: str, alias: str, idscript: str):
        object.__setattr__(self, 'python',     python)
        object.__setattr__(self, 'alias',       alias)
        object.__setattr__(self, 'idscript', idscript)

    def __repr__(self):
        return self.idscript

    
class TOKEN_ALIAS(TOKEN_ELEMENT):
    def __init__(self, python: str, alias: str, idscript: str):
        object.__setattr__(self, 'python',     python)
        object.__setattr__(self, 'alias',       alias)
        object.__setattr__(self, 'idscript', idscript)

    def __repr__(self):
        return self.alias


def generate_token(d: dict[str, str]) -> tuple[TOKEN_ELEMENT, TOKEN_ELEMENT, TOKEN_ELEMENT]:
    python    = TOKEN_PY_NAME(**d)
    alias     = TOKEN_ALIAS(**d)
    idscript  = TOKEN_IDS_NAME(**d)
    return (python, alias, idscript)



import json, pathlib
resolve_path = pathlib.Path(__file__).parent / 'TOKEN.json'
TOKEN = json.load(open(resolve_path))
for d in TOKEN['names']:
    res = generate_token(d)
    for i, name in enumerate(d.values()):
        globals()[name] = res[i]

del (
    json,                   TOKEN,
    TOKEN_ELEMENT,    TOKEN_ALIAS,
    TOKEN_IDS_NAME, TOKEN_PY_NAME,
    d,           i, name,     res,
    generate_token
)