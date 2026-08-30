from .. import TOKEN

def to_ids(name: str) -> str:
    this_token = getattr(TOKEN, name)
    return this_token.idscript

def to_py(name: str, alias: bool = True) -> str:
    this_token = getattr(TOKEN, name)
    if alias:
        return this_token.alias
    
    return this_token.python