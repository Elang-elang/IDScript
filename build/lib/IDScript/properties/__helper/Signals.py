from typing import Any

class ContinueSignal(Exception): ...
class BreakSignal(Exception):    ...

class ReturnSignal(Exception):
    __slots__ = {'value'}
    def __init__(self, value: Any):
        self.value = value
        super().__init__(value)