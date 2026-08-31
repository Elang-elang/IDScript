from typing import Any

def GetAttr(
    cls:  Any,
    name: str,
    /, *,
    default: Any | None = None,
    
) -> Any:
    try:
        return object.__getattribute__(cls, name)
    
    except:
        if default is not None:
            return default
        
        raise

def SetAttr(
    cls: Any,
    name: str,
    value: Any,
    /,
    
) -> None:
    try:
        return object.__setattr__(cls, name, value)
    
    except:
        raise


def DelAttr(
    cls: Any,
    name: str,
    /,
    
) -> None:
    try:
        return object.__delattr__(cls, name)
    
    except:
        raise


def HasAttr[T: type](
    cls: T,
    name: str,
    /,
) -> bool:
    return name in dir(cls) or hasattr(cls, name)
