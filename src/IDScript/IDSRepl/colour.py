from ..compile.exceptions import _ANSI as COLOUR


RESET = COLOUR["reset"]
BOLD = COLOUR["bold"]
DIM = COLOUR["dim"]
RED = COLOUR["red"]
GREEN = COLOUR["green"]
YELLOW = COLOUR["yellow"]
BLUE = COLOUR["blue"]
MAGENTA = COLOUR["magenta"]
CYAN = COLOUR["cyan"]
GRAY = COLOUR["gray"]


_RESULT_COLORS = {
    int: YELLOW,
    float: CYAN,
    str: GREEN,
    bool: YELLOW,
    type(None): DIM,
}


def fmt_val(v: object) -> str:
    color = _RESULT_COLORS.get(type(v), MAGENTA)
    return f"{color}{v}{RESET}"
