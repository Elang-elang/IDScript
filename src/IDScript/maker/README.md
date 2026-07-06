# IDScript Maker API (`IDScript.maker`)

Python-to-IDScript binding API. Memungkinkan definisi struktur, fungsi, kelas, trait, dan implementasi IDScript dari Python murni — tanpa file `.ids`.

## Komponen

| Module | Kelas Utama | Fungsi |
|--------|-------------|--------|
| `module.py` | `IDSModule`, `IDSDeclaration` | Wadah binding; kompilasi ke `ModuleCode`/`.idsm` |
| `function.py` | `IDSFunctionBinding`, `IDSMethodBinding` | Binding fungsi & method biasa |
| `structure.py` | `IDSStructBinding` | Binding struktur (`struktur`) dengan properti |
| `klass.py` | `IDSClassBinding` | Gabungan struct + implementasi untuk kelas Python |
| `implement.py` | `IDSImplementBinding`, `IDSImplement` | Binding implementasi method ke struct |
| `trait.py` | `IDSTraitBinding` | Binding trait (`sifat`) |
| `pyvalue.py` | `IDSPyValue`, `wrap_py_value`, `unwrap_py_value` | Bungkus nilai Python agar bisa dipakai di IDScript |
| `registry.py` | `register_native`, `NATIVE_REGISTRY` | Registry global untuk native binding |
| `module_path.py` | `resolve_module` | Resolve path modul dari object `__main__` |
| `types.py` | `ids_type_name`, `type_descriptor` | Konversi tipe Python ↔ IDScript |
| `errors.py` | `IDSMakerError` | Exception khusus maker |

## Alur

1. Buat binding (fungsi/struktur/trait/dll)
2. Masukkan ke `IDSModule`
3. Kompilasi via `.compile()` → `ModuleCode`
4. Simpan sebagai `.idsm` atau muat ke interpreter

```
from IDScript.maker import IDSModule, IDSFunctionBinding

mod = IDSModule("contoh")
mod.bind(IDSFunctionBinding("sapa", lambda nama: f"Halo {nama}", declare="public"))
mod.compile()
mod.save("contoh.idsm")
```
