# IDScript Compile

Direktori ini berisi pipeline compile/runtime untuk IDScript.

## Alur Utama

1. `compile.py` membaca source IDScript dan grammar `../gramm.lark`.
2. `lark` mengubah source menjadi parse tree.
3. `parse.py` mengubah parse tree menjadi node AST dari `node.py`.
4. `compiler.py` menjalankan AST dengan `Scope`, builtin, fungsi, dan runtime `struktur`.
5. File di `Utils/` menyimpan helper runtime seperti scope, type checking, return/throw, dan native `Structure`.

## Struktur File

- `compile.py`: entrypoint dan API sederhana untuk compile/run.
- `compiler.py`: visitor AST dan evaluator runtime.
- `parse.py`: transformer Lark tree ke AST.
- `node.py`: dataclass AST.
- `builtin.py`: fungsi dan tipe bawaan IDScript.
- `Utils/`: helper runtime internal.
- `testing/`: test pytest untuk statement dan runtime.
- `SYNTAX.md`: panduan syntax IDScript untuk pemula.
- `EXPLANATION.md`: catatan desain `struktur` dan `implementasi`.
- `ROADMAP.json`: roadmap teknis dalam format JSON.

## Skema Verifikasi

Jalankan dari direktori ini:

```bash
python -m mypy .
python -m pytest
python compile.py
```

`python compile.py` menjalankan contoh di `../../../Example/main.ids`.
