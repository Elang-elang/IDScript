"""Python-to-IDScript binding API (Maker).

Memungkinkan definisi struktur, fungsi, kelas, trait, dan implementasi
IDScript langsung dari Python — tanpa menulis file .ids.

Pemakaian:
    from IDScript.maker import IDSModule, IDSFunctionBinding
    
    mod = IDSModule("contoh")
    mod.bind(IDSFunctionBinding("sapa", lambda nama: f"Halo {nama}", declare="public"))
    mod.compile()
    mod.save("contoh.idsm")

Komponen utama:
    IDSModule          -- Wadah binding, kompilasi ke ModuleCode
    IDSFunctionBinding -- Binding fungsi biasa
    IDSMethodBinding   -- Binding method struct
    IDSStructBinding   -- Binding struktur dengan properti
    IDSClassBinding    -- Gabungan struct + implementasi
    IDSImplementBinding-- Binding implementasi method ke struct
    IDSTraitBinding    -- Binding trait (sifat)
    IDSPyValue         -- Bungkus nilai Python untuk IDScript
    IDSMakerError      -- Exception khusus maker
"""

from .errors import IDSMakerError
from .function import IDSFunction, IDSFunctionBinding, IDSMethod, IDSMethodBinding
from .implement import IDSImplement, IDSImplementBinding
from .klass import IDSClass, IDSClassBinding
from .module import IDSModule
from .pyvalue import IDSPyValue, unwrap_py_value, wrap_py_value
from .registry import clear_registry, register_native, unregister_native
from .structure import IDSStruct, IDSStructBinding
from .trait import IDSTrait, IDSTraitBinding

__all__ = [
    "IDSFunction",
    "IDSFunctionBinding",
    "IDSMethod",
    "IDSMethodBinding",
    "IDSMakerError",
    "IDSStruct",
    "IDSStructBinding",
    "IDSImplement",
    "IDSImplementBinding",
    "IDSClass",
    "IDSClassBinding",
    "IDSTrait",
    "IDSTraitBinding",
    "IDSModule",
    "IDSPyValue",
    "wrap_py_value",
    "unwrap_py_value",
    "register_native",
    "unregister_native",
    "clear_registry",
]
