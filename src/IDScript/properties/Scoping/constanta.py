from typing import Literal

# Constanta
SLOTS_PROPERTY = {
    'name',     'type',   'value',
    'constant',           'private',
}

SLOTS_METHODS = {
    'copy',        'to_dict',
    '__init__',    '__repr__',    '__dict__',
    '__getattr__', '__setattr__', '__delattr__', 
    '__getitem__', '__setitem__', '__delitem__',
    '__deepcopy__',               '__copy__',
}

SLOTS_ATTRS = {*SLOTS_PROPERTY, *SLOTS_METHODS}

SLOTS_ALIAS: dict[str, str] = {
    # properties
    'nama':      'name',
    'tipe':      'type',
    'isi':       'value',
    'isian':     'value',
    'konstant':  'constant',
    'privat':    'private',

    # methods
    'salin':            'copy',
    '__getattribute__': '__getattr__',
}

SLOTS_VALUE = {
    'isi', 'isian', 'value'
}

type SCOPES = Literal[
    'Global', 'global',
    'Local',  'local',
]