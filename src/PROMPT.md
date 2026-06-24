# Prompt Refactor Compile IDScript

Refactor folder `IDScript/compile` sebagai paket compiler/runtime IDScript.
Tujuan utama adalah merapikan struktur modul, memperjelas tanggung jawab file,
memperbaiki import, dan menjaga seluruh perilaku bahasa tetap sama.

## Konteks Aktual

Folder ini berisi implementasi compile/runtime IDScript:

- `compile.py`: entrypoint `Compile`, membaca grammar `../gramm.lark`,
  menjalankan parser, membangun AST, lalu mengeksekusi compiler/runtime.
- `parse.py`: transformer `lark.Transformer` yang mengubah parse tree menjadi AST.
- `node.py`: semua node AST dalam bentuk dataclass.
- `compiler.py`: visitor/evaluator utama untuk menjalankan AST.
- `builtin.py`: builtin function dan builtin type IDScript.
- `Utils/Types.py`: sentinel `EMPTY`, helper type checking, default value.
- `Utils/scope.py`: `GlobalScope` dan `Scope`.
- `Utils/Struct.py`: runtime native Python untuk `struktur`.
- `Utils/Simple.py`: exception internal untuk `return`, `throw`, `break`,
  dan `continue`.
- `Utils/utils.py`: helper low-level dan `Config`.
- `testing/`: test pytest untuk compiler, import module, pattern matching,
  control flow, dan runtime struktur.

Parser memakai `lark` dan file grammar berada di `IDScript/gramm.lark`.
Tidak perlu membuat lexer/tokenizer manual kecuali benar-benar dibutuhkan.

## Aturan Wajib

- Jangan mengubah semantik bahasa IDScript.
- Jangan mengubah syntax di `gramm.lark` kecuali ada bug yang terbukti.
- Pertahankan API publik:
  - `from compile import Compile`
  - `from compile import Compiler`
  - `from compile import Parse`
- Pertahankan nama konsep bahasa Indonesia seperti `struktur`, `fungsi`,
  `implementasi`, `utama`, `kembalikan`, dan node terkait.
- Semua import harus diperbarui setelah pemindahan file.
- Hindari refactor besar yang tidak diperlukan.
- Jalankan test setelah perubahan.

## Target Struktur

Usulkan struktur akhir seperti ini atau variasi minimal yang lebih aman:

```text
compile/
├── __init__.py
├── entrypoint.py
├── builtin.py
├── ast/
│   ├── __init__.py
│   ├── base.py
│   ├── statements.py
│   ├── functions.py
│   ├── structures.py
│   ├── control_flow.py
│   ├── modules.py
│   ├── expressions.py
│   ├── patterns.py
│   └── types.py
├── parser/
│   ├── __init__.py
│   └── transformer.py
├── runtime/
│   ├── __init__.py
│   ├── compiler.py
│   ├── scope.py
│   ├── structure.py
│   ├── types.py
│   ├── control.py
│   └── config.py
└── testing/
    ├── __init__.py
    ├── conftest.py
    ├── test_compile.py
    └── test_struct_runtime.py
```

Jika pemecahan penuh terlalu berisiko, lakukan bertahap:

1. Pindahkan utilitas runtime terlebih dahulu.
2. Pindahkan AST node ke package `ast`.
3. Pindahkan transformer parser ke package `parser`.
4. Pindahkan evaluator `Compiler` ke package `runtime`.
5. Pertahankan shim kompatibilitas hanya bila diperlukan oleh test/API publik.

## Detail Refactor

### Entry Point

- `Compile` boleh dipindah dari `compile.py` ke `entrypoint.py`.
- `compile.py` dapat menjadi wrapper tipis jika masih dibutuhkan.
- Path grammar harus tetap mengarah ke `IDScript/gramm.lark`.
- Method yang sudah ada seperti `main()`, `run()`, `test()`, dan `exports()`
  harus tetap bekerja.

### AST

- Pecah `node.py` berdasarkan kategori:
  - program/base node;
  - statement;
  - function/method;
  - structure/implementation;
  - control flow;
  - module import;
  - expression;
  - pattern matching;
  - type annotation.
- Gunakan dataclass seperti implementasi saat ini.
- Pastikan nama class node tidak berubah kecuali seluruh referensi diperbarui.

### Parser

- `Parse` dan transformer `_Parse` harus tetap menghasilkan AST yang sama.
- Sesuaikan import node dari package AST baru.
- Jangan mengubah mapping rule grammar tanpa test.

### Runtime Compiler

- `Compiler` adalah visitor/evaluator AST.
- Pertahankan dispatch berdasarkan nama class node.
- Boleh pecah helper internal seperti pattern matching, function wrapper,
  import module, dan type resolver jika tidak mengubah perilaku.
- Pastikan control flow exception `Return`, `Throw`, `Break`, dan `Continue`
  tetap bekerja.

### Runtime Utils

- Rapikan `Utils` menjadi package runtime lowercase jika aman.
- `Types.py` dapat menjadi `runtime/types.py`.
- `scope.py` dapat menjadi `runtime/scope.py`.
- `Struct.py` dapat menjadi `runtime/structure.py`.
- `Simple.py` dapat menjadi `runtime/control.py`.
- `utils.py` dapat menjadi `runtime/config.py` atau helper runtime.
- Update semua import dan test.

### Builtin

- `builtin.py` boleh tetap di root package atau dipindah ke runtime.
- Daftar `ALL` harus tetap berisi builtin function dan type yang sama.

## Kualitas Kode

- Tambahkan module docstring pada modul baru.
- Tambahkan type hints pada fungsi publik dan method penting.
- Gunakan nama yang jelas.
- Ikuti PEP 8 sebisa mungkin.
- Jangan menambahkan komentar yang menjelaskan hal trivial.
- Hindari circular import.
- Hapus import tidak terpakai.

## Verifikasi

Jalankan dari direktori `compile`:

```bash
python -m pytest
```

Pastikan test berikut tetap lewat:

- compile example file;
- function declaration dan argument;
- comment handling;
- if/elif/else;
- for/while;
- try/catch/else/finally;
- switch/case dan pattern matching;
- module import public/private;
- runtime `Structure`.

## Output Yang Diharapkan

Berikan:

- ringkasan struktur baru;
- daftar file yang dipindah/diubah;
- penjelasan import utama yang diperbarui;
- hasil test;
- catatan risiko jika ada bagian yang sengaja belum direfactor.
