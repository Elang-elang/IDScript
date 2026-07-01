"""Internal language builtins for IDScript.

Only core types and constants live here. Standard functions/classes are external
builtins under ``IDScript/builtins`` and must be imported explicitly.
"""

import typing as T

ALL = [
    # Types
    ("Teks",      T.Type,        str),
    ("Angka",     T.Type,        int),
    ("Float",     T.Type,      float),
    ("Boolean",   T.Type,       bool),
    ("Kosong",    T.Type, type(None)),
    ("Apapun",    T.Type,      T.Any),
    
    # Keyword boolean
    ("benar",   bool,       True),
    ("salah",   bool,      False),
    ("kosong",  type(None), None),
]
