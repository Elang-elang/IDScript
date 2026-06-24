"""Internal control-flow exceptions for return and throw statements."""

class _SIMPLE(Exception):
    pass

class Throw(_SIMPLE): pass
class Return(_SIMPLE): pass
class Break(_SIMPLE): pass
class Continue(_SIMPLE): pass
