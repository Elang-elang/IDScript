# IDScript Builtins (`IDScript.builtins`)

Modul standar IDScript — library resmi yang dapat diimpor via `dari "..." impor { ... }`.

## Daftar Modul

| Modul | Deskripsi |
|-------|-----------|
| `Konsol` | Input/output terminal (`cetak`, `baca`, dll) |
| `Daftar` | Operasi list/daftar (`urutkan`, `filter`, `petakan`, dll) |
| `Kamus` | Operasi dict/kamus (`kunci`, `nilai`, `gabung`, dll) |
| `Teks` / `Atribut` | Manipulasi string/atribut |
| `Angka` / `Float` | Operasi numerik |
| `Galat` | Tipe error & penanganan |
| `Boolean` | Operasi boolean |
| `Hasil` | Tipe Result (`hasil<Ok, Err>`) |
| `Iterasi` | Iterator & generator |
| `Regex` | Regular expression |
| `HTTP` / `Permintaan` | HTTP client & request |
| `Python` | Interop dengan Python |
| `lingkup` | Scope & konteks eksekusi |
| `Waktu` | Operasi waktu (jika ada) |

## Struktur File

Setiap modul terdiri dari dua file:
- `*.py` — implementasi Python (native binding via Maker API)
- `.ids` / `.idsm` — wrapper/type signature IDScript

```
builtins/
├── Konsol.py       # Implementasi Python
├── Konsol.ids      # Signature IDScript
├── Konsol.idsm     # Compiled module
└── ...
```

## Cara Impor

```idscript
dari "Konsol" impor { cetak, baca }
dari "Daftar" impor { filter, petakan }
```
