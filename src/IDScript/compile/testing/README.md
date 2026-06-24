# Testing

Folder ini berisi test pytest untuk pipeline compile dan runtime IDScript.

## File Test

- `test_compile.py`: menguji parser/compiler dasar, fungsi, komentar `...`, dan contoh `Example/main.ids`.
- `test_struct_runtime.py`: menguji runtime native Python untuk `Utils/Struct.py`.

## Menjalankan Test

Dari direktori `compile`:

```bash
python -m pytest
```

Untuk menjalankan satu file saja:

```bash
python -m pytest testing/test_compile.py
python -m pytest testing/test_struct_runtime.py
```
