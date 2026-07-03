from pathlib import Path
from typing import Any

from IDScript.maker import IDSFunction, IDSModule
from IDScript.exceptions import IDSTypeError, IDSIndexError, IDSAttributeError

_EMPTY = object()

_NODE_SLOTS = frozenset({"data", "next"})
_LIST_SLOTS = frozenset({"_head", "_tail", "_length", "_frozenset"})


class _DaftarNode:
    __slots__ = tuple(_NODE_SLOTS)

    def __init__(self, data):
        object.__setattr__(self, "data", data)
        object.__setattr__(self, "next", _EMPTY)

    def __getattribute__(self, name):
        if name in _NODE_SLOTS:
            raise IDSAttributeError(f"{name!r} adalah properti privat")
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name in _NODE_SLOTS:
            raise IDSAttributeError(f"{name!r} adalah properti privat")
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        if name in _NODE_SLOTS:
            raise IDSAttributeError(f"{name!r} adalah properti privat")
        object.__delattr__(self, name)


class Daftar:
    __slots__ = tuple(_LIST_SLOTS)

    def __init__(self, *values):
        object.__setattr__(self, "_head", _EMPTY)
        object.__setattr__(self, "_tail", _EMPTY)
        object.__setattr__(self, "_length", 0)
        object.__setattr__(self, "_frozenset", False)

        if len(values) == 1:
            values = values[0]

        for value in values:
            self.masukkan(value)

    def __getattribute__(self, name):
        if name in _LIST_SLOTS:
            raise IDSAttributeError(f"{name!r} adalah properti privat")
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name in _LIST_SLOTS:
            raise IDSAttributeError(f"{name!r} adalah properti privat")
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        if name in _LIST_SLOTS:
            raise IDSAttributeError(f"{name!r} adalah properti privat")
        object.__delattr__(self, name)

    # --- helpers ---

    def _normalize_index(self, index):
        if not isinstance(index, int):
            raise IDSTypeError("Indeks Daftar harus berupa Angka")

        length = object.__getattribute__(self, "_length")
        if index < 0:
            index += length
        if index < 0 or index >= length:
            raise IDSIndexError(index)

        return index

    def _get(self, index):
        index = self._normalize_index(index)
        node = object.__getattribute__(self, "_head")

        for _ in range(index):
            node = object.__getattribute__(node, "next")

        return node

    # --- sort helpers ---

    # --- sort helpers ---

    @staticmethod
    def _sort_key(value, self_sentinel=_EMPTY):
        if isinstance(value, bool):
            return (0, value)
        if isinstance(value, (int, float)):
            return (1, value)
        if isinstance(value, str):
            return (2, len(value), value)
        if isinstance(value, (list, Daftar)):
            if value is self_sentinel:
                return (3, 0)
            return (3, len(value))
        if isinstance(value, dict):
            return (4, len(value))
        from ._Kamus import Kamus
        if isinstance(value, Kamus):
            return (4, len(value))
        if hasattr(value, "__len__"):
            return (5, len(value))
        raise IDSTypeError(
            f"Tipe {type(value).__name__} tidak bisa diurutkan"
        )

    @staticmethod
    def _merge(a, b, reverse, self_sentinel=_EMPTY):
        dummy = _DaftarNode(None)
        tail = dummy

        while a is not _EMPTY and b is not _EMPTY:
            a_data = object.__getattribute__(a, "data")
            b_data = object.__getattribute__(b, "data")

            if (Daftar._sort_key(a_data, self_sentinel) <
                Daftar._sort_key(b_data, self_sentinel)) if not reverse else (
                Daftar._sort_key(a_data, self_sentinel) >
                Daftar._sort_key(b_data, self_sentinel)):
                object.__setattr__(tail, "next", a)
                tail = a
                a = object.__getattribute__(a, "next")
            else:
                object.__setattr__(tail, "next", b)
                tail = b
                b = object.__getattribute__(b, "next")

        object.__setattr__(tail, "next", a if a is not _EMPTY else b)
        return object.__getattribute__(dummy, "next")

    @staticmethod
    def _merge_sort(head, reverse, self_sentinel=_EMPTY):
        if head is _EMPTY or object.__getattribute__(head, "next") is _EMPTY:
            return head

        slow = head
        fast = object.__getattribute__(head, "next")

        while fast is not _EMPTY:
            fast = object.__getattribute__(fast, "next")
            if fast is not _EMPTY:
                slow = object.__getattribute__(slow, "next")
                fast = object.__getattribute__(fast, "next")

        mid = object.__getattribute__(slow, "next")
        object.__setattr__(slow, "next", _EMPTY)

        left = Daftar._merge_sort(head, reverse, self_sentinel)
        right = Daftar._merge_sort(mid, reverse, self_sentinel)

        return Daftar._merge(left, right, reverse, self_sentinel)

    # --- public API ---

    def ambil(self, index):
        node = self._get(index)
        return object.__getattribute__(node, "data")

    def masukkan(self, value):
        if object.__getattribute__(self, "_frozenset"):
            raise IDSTypeError("Tidak bisa di masukkan karena telah di tetap/konstan")

        node = _DaftarNode(value)
        head = object.__getattribute__(self, "_head")
        tail = object.__getattribute__(self, "_tail")

        if head is _EMPTY:
            object.__setattr__(self, "_head", node)
            object.__setattr__(self, "_tail", node)
        else:
            object.__setattr__(tail, "next", node)
            object.__setattr__(self, "_tail", node)

        length = object.__getattribute__(self, "_length")
        object.__setattr__(self, "_length", length + 1)
        return self

    def masuk(self, index, value):
        if object.__getattribute__(self, "_frozenset"):
            raise IDSTypeError("Tidak bisa di masuk/atur karena telah di tetap/konstan")

        node = self._get(index)
        object.__setattr__(node, "data", value)
        return self

    atur = masuk

    def luaskan(self, *values):
        if len(values) == 1:
            values = values[0]
        try:
            for value in values:
                self.masukkan(value)
            return self
        except Exception as e:
            raise IDSAttributeError(e)
        
    def atur_tetap(self):
        object.__setattr__(self, "_frozenset", True)
        return self

    def urut(self, reverse=False):
        if object.__getattribute__(self, "_frozenset"):
            raise IDSTypeError("Tidak bisa di urutkan karena telah di tetap/konstan")

        head = object.__getattribute__(self, "_head")
        if head is _EMPTY:
            return self

        head = Daftar._merge_sort(head, reverse, self)
        object.__setattr__(self, "_head", head)

        tail = head
        while object.__getattribute__(tail, "next") is not _EMPTY:
            tail = object.__getattribute__(tail, "next")
        object.__setattr__(self, "_tail", tail)

        return self

    def salin(self):
        copied = Daftar()
        node = object.__getattribute__(self, "_head")

        while node is not _EMPTY:
            data = object.__getattribute__(node, "data")
            copied.masukkan(data)
            node = object.__getattribute__(node, "next")

        return copied

    def hapus(self, index):
        if object.__getattribute__(self, "_frozenset"):
            raise IDSTypeError("Tidak bisa di hapus karena telah di tetap/konstan")

        index = self._normalize_index(index)
        previous = _EMPTY
        target = object.__getattribute__(self, "_head")

        for _ in range(index):
            previous = target
            target = object.__getattribute__(target, "next")

        if previous is _EMPTY:
            object.__setattr__(self, "_head", object.__getattribute__(target, "next"))
        else:
            object.__setattr__(previous, "next", object.__getattribute__(target, "next"))

        if target is object.__getattribute__(self, "_tail"):
            object.__setattr__(self, "_tail", previous)

        length = object.__getattribute__(self, "_length")
        object.__setattr__(self, "_length", length - 1)

        if object.__getattribute__(self, "_length") == 0:
            object.__setattr__(self, "_head", _EMPTY)
            object.__setattr__(self, "_tail", _EMPTY)

        return self

    # --- dunder ---

    def __getitem__(self, index):
        return self.ambil(index)

    def __setitem__(self, index, value):
        self.masuk(index, value)

    def __delitem__(self, index):
        self.hapus(index)

    def __len__(self):
        return object.__getattribute__(self, "_length")

    def __contains__(self, instance):
        node = object.__getattribute__(self, "_head")

        while node is not _EMPTY:
            data = object.__getattribute__(node, "data")
            if data == instance:
                return True
            node = object.__getattribute__(node, "next")

        return False

    def __iter__(self):
        node = object.__getattribute__(self, "_head")

        while node is not _EMPTY:
            yield object.__getattribute__(node, "data")
            node = object.__getattribute__(node, "next")

    def __repr__(self):
        items = []
        node = object.__getattribute__(self, "_head")
        while node is not _EMPTY:
            data = object.__getattribute__(node, "data")
            if data is self:
                items.append("Daftar<[...]>")
            else:
                items.append(repr(data))
            node = object.__getattribute__(node, "next")
        inner = ", ".join(items)
        if object.__getattribute__(self, "_frozenset"):
            return f"Daftar<Konstan<[{inner}]>>"
        return f"Daftar<[{inner}]>"
	
    def __str__(self):
        return self.__repr__()


@IDSFunction(name="Daftar", declare="public", arguments={"nilai": Any}, annotation=Any)
def _daftar(nilai: Any) -> Daftar:
    return Daftar(nilai)


@IDSFunction(name="adalah_daftar", declare="public", arguments={"nilai": Any}, annotation=bool)
def _adalah_daftar(nilai: Any) -> bool:
    return isinstance(nilai, (list, Daftar))


@IDSModule(name="_Daftar", path=Path(__file__).with_suffix(".idsm"))
def module(cls):
    cls.add(_daftar, _adalah_daftar)
    if __name__ == "__main__":
        cls.write()
