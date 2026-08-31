from ...properties.TypeSystem import CheckType
from typing import Any, Literal


def check_options(
    options:     set[str] | frozenset[str],
    get_options: set[str] | frozenset[str]
) -> None:
    if options - get_options:
        raise AttributeError(f'Opsi hanya ada {', '.join(options)}. yang tidak diketahui {', '.join(get_options)}')

def resolver_type(raw_type: Any) -> Any:
    if raw_type is None:
        return Literal[0]
    elif raw_type is bool:
        return Literal[0, 1]
    return raw_type