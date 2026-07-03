from collections.abc import MutableMapping
from pathlib import Path
from typing import Any

from IDScript.maker import IDSFunction, IDSModule
from IDScript.exceptions import IDSTypeError, IDSAttributeError, IDSKeyError
from ._Daftar import Daftar

_EMPTY = object()

_NODE_SLOTS = frozenset({"key", "value", "next"})
_DICT_SLOTS = frozenset({"_head", "_tail", "_length", "_frozenset"})


class _Kamus:
    __slots__ = tuple(_NODE_SLOTS)

    def __init__(self, key, value):
        object.__setattr__(self, "key", key)
        object.__setattr__(self, "value", value)
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


class Kamus(MutableMapping):
    __slots__ = tuple(_DICT_SLOTS)

    def __init__(self, *items, **kwargs):
        object.__setattr__(self, "_head", _EMPTY)
        object.__setattr__(self, "_tail", _EMPTY)
        object.__setattr__(self, "_length", 0)
        object.__setattr__(self, "_frozenset", False)

        if len(items) == 1 and isinstance(items[0], (list, Daftar, dict, Kamus)):
            iterable = items[0]
            if isinstance(iterable, (dict, Kamus)):
                iterable = iterable.items()
            for key, value in iterable:
                self.masukkan(key, value)
        else:
            for item in items:
                key, value = item
                self.masukkan(key, value)

        for key, value in kwargs.items():
            self.masukkan(key, value)

    # ---------- private helpers ----------

    def __getattribute__(self, name):
        if name in _DICT_SLOTS:
            raise IDSAttributeError(f"{name!r} adalah properti privat")
        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name in _DICT_SLOTS:
            raise IDSAttributeError(f"{name!r} adalah properti privat")
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        if name in _DICT_SLOTS:
            raise IDSAttributeError(f"{name!r} adalah properti privat")
        object.__delattr__(self, name)

    def _node_for(self, key):
        node = object.__getattribute__(self, "_head")
        while node is not _EMPTY:
            if object.__getattribute__(node, "key") == key:
                return node
            node = object.__getattribute__(node, "next")
        return _EMPTY

    def _get(self, key, default=_EMPTY):
        node = self._node_for(key)
        if node is _EMPTY:
            if default is not _EMPTY:
                return default
            raise IDSKeyError(key)
        return object.__getattribute__(node, "value")

    @staticmethod
    def _sort_key(key):
        if isinstance(key, bool):
            return (0, key)
        if isinstance(key, (int, float)):
            return (1, key)
        if isinstance(key, str):
            return (2, len(key), key)
        raise IDSKeyError(
            f"Key tipe {type(key).__name__} tidak valid untuk Kamus"
        )

    @staticmethod
    def _merge(a, b, reverse):
        dummy = _Kamus(None, None)
        tail = dummy
        while a is not _EMPTY and b is not _EMPTY:
            ak = object.__getattribute__(a, "key")
            bk = object.__getattribute__(b, "key")
            if (Kamus._sort_key(ak) < Kamus._sort_key(bk)) if not reverse else (
                Kamus._sort_key(ak) > Kamus._sort_key(bk)
            ):
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
    def _merge_sort(head, reverse):
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
        left = Kamus._merge_sort(head, reverse)
        right = Kamus._merge_sort(mid, reverse)
        return Kamus._merge(left, right, reverse)

    # ---------- public API ----------

    def ambil(self, key, default=None):
        if not isinstance(key, (str, int, float, bool)):
            raise IDSKeyError(
            f"Key tipe {type(key).__name__} tidak valid untuk Kamus"
        )
        
        return self._get(key, default)

    def masukkan(self, key, value):
        if object.__getattribute__(self, "_frozenset"):
            raise IDSTypeError(
                "Tidak bisa di masukkan karena telah di tetap/konstan"
            )
        
        if not isinstance(key, (str, int, float, bool)):
            raise IDSKeyError(
            f"Key tipe {type(key).__name__} tidak valid untuk Kamus"
        )
        
        node = self._node_for(key)
        if node is not _EMPTY:
            object.__setattr__(node, "value", value)
            return self
        node = _Kamus(key, value)
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

    atur = masukkan
    masuk = masukkan

    def luaskan(self, *value, **kwargs):
        try:
            if value:
                value = value[0]
            if value and kwargs:
                self.update(value)
                self.update(kwargs)
                return self
            self.update(value or kwargs)
            return self
        except Exception as e:
            raise IDSAttributeError(e)

    def hapus(self, key):
        if object.__getattribute__(self, "_frozenset"):
            raise IDSTypeError(
                "Tidak bisa di hapus karena telah di tetap/konstan"
            )
        
        if not isinstance(key, (str, int, float, bool)):
            raise IDSKeyError(
            f"Key tipe {type(key).__name__} tidak valid untuk Kamus"
        )
            
        previous = _EMPTY
        node = object.__getattribute__(self, "_head")
        while node is not _EMPTY:
            if object.__getattribute__(node, "key") == key:
                if previous is _EMPTY:
                    object.__setattr__(
                        self,
                        "_head",
                        object.__getattribute__(node, "next"),
                    )
                else:
                    object.__setattr__(
                        previous,
                        "next",
                        object.__getattribute__(node, "next"),
                    )
                if node is object.__getattribute__(self, "_tail"):
                    object.__setattr__(self, "_tail", previous)
                length = object.__getattribute__(self, "_length")
                object.__setattr__(self, "_length", length - 1)
                if object.__getattribute__(self, "_length") == 0:
                    object.__setattr__(self, "_head", _EMPTY)
                    object.__setattr__(self, "_tail", _EMPTY)
                return self
            previous = node
            node = object.__getattribute__(node, "next")
        raise IDSKeyError(key)

    def atur_tetap(self):
        object.__setattr__(self, "_frozenset", True)
        return self

    def salin(self):
        copied = Kamus()
        node = object.__getattribute__(self, "_head")
        while node is not _EMPTY:
            k = object.__getattribute__(node, "key")
            v = object.__getattribute__(node, "value")
            copied.masukkan(k, v)
            node = object.__getattribute__(node, "next")
        return copied

    def urut(self, reverse=False):
        if object.__getattribute__(self, "_frozenset"):
            raise IDSTypeError(
                "Tidak bisa di urutkan karena telah di tetap/konstan"
            )
        head = object.__getattribute__(self, "_head")
        if head is _EMPTY:
            return self
        head = Kamus._merge_sort(head, reverse)
        object.__setattr__(self, "_head", head)
        tail = head
        while object.__getattribute__(tail, "next") is not _EMPTY:
            tail = object.__getattribute__(tail, "next")
        object.__setattr__(self, "_tail", tail)
        return self

    def kunci(self):
        result = Daftar()
        node = object.__getattribute__(self, "_head")
        while node is not _EMPTY:
            result.masukkan(object.__getattribute__(node, "key"))
            node = object.__getattribute__(node, "next")
        return result

    def nilai(self):
        result = Daftar()
        node = object.__getattribute__(self, "_head")
        while node is not _EMPTY:
            result.masukkan(object.__getattribute__(node, "value"))
            node = object.__getattribute__(node, "next")
        return result

    def item(self):
        result = Daftar()
        node = object.__getattribute__(self, "_head")
        while node is not _EMPTY:
            k = object.__getattribute__(node, "key")
            v = object.__getattribute__(node, "value")
            result.masukkan((k, v))
            node = object.__getattribute__(node, "next")
        return result

    # ---------- dunder ----------

    def __dict__(self):
        result = {}
        node = object.__getattribute__(self, "_head")
        while node is not _EMPTY:
            k = object.__getattribute__(node, "key")
            v = object.__getattribute__(node, "value")
            result[k] = v
            node = object.__getattribute__(node, "next")
        return result

    def __getitem__(self, key):
        return self._get(key)

    def __setitem__(self, key, value):
        self.masukkan(key, value)

    def __delitem__(self, key):
        self.hapus(key)

    def __contains__(self, key):
        return self._node_for(key) is not _EMPTY

    def __len__(self):
        return object.__getattribute__(self, "_length")

    def __iter__(self):
        node = object.__getattribute__(self, "_head")
        while node is not _EMPTY:
            yield object.__getattribute__(node, "key")
            node = object.__getattribute__(node, "next")

    def _repr_value(self, value):
        if value is self:
            return "Kamus<{...}>"
        return repr(value)

    def __repr__(self):
        items = []
        node = object.__getattribute__(self, "_head")
        while node is not _EMPTY:
            k = object.__getattribute__(node, "key")
            v = object.__getattribute__(node, "value")
            items.append(f"{k!r}: {self._repr_value(v)}")
            node = object.__getattribute__(node, "next")
        inner = ", ".join(items)
        if object.__getattribute__(self, "_frozenset"):
            return f"Kamus<Konstan<{{{inner}}}>>"
        return f"Kamus<{{{inner}}}>"

    def __str__(self):
        return self.__repr__()


@IDSFunction(name="Kamus", declare="public", arguments={"nilai": Any}, annotation=Any)
def _kamus(nilai) -> Kamus:
    return Kamus(nilai)


@IDSFunction(name="adalah_kamus", declare="public", arguments={"nilai": Any}, annotation=bool)
def _adalah_kamus(nilai) -> bool:
    return isinstance(nilai, (dict, Kamus))


@IDSModule(name="_Kamus", path=Path(__file__).with_suffix(".idsm"))
def module(cls):
    cls.add(_kamus, _adalah_kamus)
    if __name__ == "__main__":
        cls.write()
