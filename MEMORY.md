# MEMORY.md

Dokumen ini merangkum percakapan, keputusan, perubahan, dan memori kerja selama sesi pengembangan IDScript. File ini dibuat sebagai catatan berkelanjutan agar konteks proyek tidak hilang.

## Identitas Proyek

- Nama proyek: IDScript
- Singkatan: IDS
- Makna nama: `I[n]D[onesian] Script`, atau secara ringkas `I[n]D[o] Script`
- Pembuat: Elang MRJ
- Username GitHub: `Elang-elang`
- Email: `elangmuhamad888@gmail.com`
- Repository IDScript: <https://github.com/Elang-elang/IDScript>
- Repository pendahulu Indonesian Script (IS): <https://github.com/Elang-elang/indonesian_script>

## Latar Belakang Yang Disepakati

IDScript adalah bahasa pemrograman berbahasa Indonesia yang meneruskan proyek Indonesian Script (IS). IS adalah prototype awal buatan Elang MRJ yang sempat terbengkalai. IDScript dibuat sebagai kelanjutan yang lebih rapi dan lebih serius, dengan grammar, AST, interpreter normal, compiler VM resmi, format module `.idsm`, format compiled bytecode `.idsc`, builtin IDS, dan CLI publik.

Tujuan IDScript bukan langsung menggantikan bahasa pemrograman besar, tetapi menjadi ruang eksperimen serius untuk bahasa pemrograman yang sintaksnya lebih dekat dengan penutur Indonesia.

## Ringkasan Percakapan

### 1. Rekap Awal Proyek

Percakapan dimulai dengan permintaan untuk mengetahui apa yang sudah dilakukan. Konteks besar yang dirangkum saat itu:

- Runtime normal dan compiler VM resmi sudah berkembang cukup jauh.
- Ada fitur `info`, `Config`, enum, compiled module import, builtin IDS, Regex IDS, trait/sifat, extend/turunan, dan VM language yang sedang dirancang.
- Official VM berada di `src/IDScript/compile/Compiler`.
- Runtime normal berada di `src/IDScript/compile/runtime`.
- Grammar utama berada di `src/IDScript/gramm.lark`.

### 2. Perbaikan Runtime Normal: Trait dan Extend

Kita menemukan beberapa blocker serius pada runtime normal:

- `compile/runtime/compiler.py` punya syntax error pada `if node.trait`.
- `compile/runtime/structure.py` punya syntax error `raise raise AttributeError`.
- Grammar punya `impl_trait`, tetapi belum reachable dari `impl_stmt`.
- `AbstractMethod` belum memakai `@dataclass`.
- Transformer punya method `privat_trait`, tetapi grammar memanggil `private_trait`.
- Trait validation belum benar.
- Extend/turunan belum menyalin field dan method parent dengan aman.

Perbaikan yang dilakukan:

- `gramm.lark`: `impl_stmt` sekarang menerima `impl_plain | impl_trait`.
- `nodes.py`: `AbstractMethod` diberi `@dataclass`.
- `transformer.py`: `impl_plain` ditambahkan dan `private_trait` diperbaiki.
- `runtime/compiler.py`: implementasi trait diperbaiki.
- `runtime/compiler.py`: pembuatan annotations method memakai `zip(...)`.
- `runtime/compiler.py`: deklarasi trait memakai `current_scope.declare(...)`.
- `runtime/structure.py`: extend/turunan menyalin schema dan methods parent.
- `runtime/structure.py`: duplicate field dan duplicate method sekarang raise error.
- `runtime/structure.py`: `Trait.__call__` divalidasi ulang tanpa mutasi dictionary method.

Test yang ditambahkan/diperbaiki:

- Trait implementation valid.
- Trait implementation missing method.
- Trait signature mismatch.
- Extend copies fields.
- Extend copies methods.
- Duplicate field error.
- Duplicate method error.

Status verifikasi runtime normal:

- `36 passed, 1 deselected` jika `test_compile_example_file` diskip.
- Full normal runtime masih gagal jika test example lama dijalankan, karena `Example/main.ids` belum ada.

### 3. Rancangan VM Language

Awalnya ada ide instruction pointer dengan bentuk `L1:0`, `L1:1`, seperti line dan column. Setelah diskusi, arah berubah menjadi model seperti Python VM.

Keputusan VM language:

- Runtime IP tetap angka offset biasa.
- Label seperti `L1`, `L_else`, `L_end` hanya simbol compiler/disassembler.
- Bytecode tetap flat list.
- Function/method punya code object sendiri.
- Control flow memakai jump target, bukan nested block pointer.
- Opcode dibuat lebih eksplisit seperti Python bytecode.

Opcode yang diganti menjadi eksplisit:

- `CONST` -> `LOAD_CONST`
- `DEFAULT` -> `LOAD_DEFAULT`
- `LOAD` -> `LOAD_NAME`
- `STORE` -> `STORE_NAME`
- `STORE_LOCAL` -> `STORE_FAST`
- `POP` -> `POP_TOP`
- `BINARY` -> `BINARY_OP`
- `UNARY` -> `UNARY_OP`
- `COMPARE` -> `COMPARE_OP`
- `JUMP` -> `JUMP_ABSOLUTE`
- `JUMP_IF_FALSE` -> `POP_JUMP_IF_FALSE`
- `CALL` -> `CALL_FUNCTION`
- `RETURN` -> `RETURN_VALUE`
- `MAKE_LIST` -> `BUILD_LIST`
- `MAKE_MAP` -> `BUILD_MAP`
- `GET_INDEX` -> `BINARY_SUBSCR`
- `SET_INDEX` -> `STORE_SUBSCR`
- `FOR_NEXT` -> `FOR_ITER`
- `IMPORT` -> `IMPORT_NAME`
- `THROW` -> `RAISE_ERROR`
- `GET_ATTR` -> `LOAD_ATTR`
- `SET_ATTR` -> `STORE_ATTR`
- `MAKE_STRUCT` -> `BUILD_STRUCT_TYPE`
- `MAKE_STRUCT_INSTANCE` -> `BUILD_STRUCT_INSTANCE`
- `ADD_METHOD` -> `STORE_METHOD`
- `MAKE_ENUM` -> `BUILD_ENUM_TYPE`
- `MAKE_TYPE_ALIAS` -> `BUILD_TYPE_ALIAS`
- `MAKE_INTERFACE` -> `BUILD_INTERFACE`
- `INFO` -> `LOAD_INFO`

Opcode baru yang ditambahkan:

- `TO_BOOL`
- `POP_JUMP_IF_TRUE`

Keputusan untuk `if not` / `bukan`:

- `jika (bukan kondisi)` dikompilasi menjadi evaluasi kondisi, `TO_BOOL`, lalu `POP_JUMP_IF_TRUE`.
- `jika (kondisi)` dikompilasi menjadi evaluasi kondisi, `TO_BOOL`, lalu `POP_JUMP_IF_FALSE`.

Backward compatibility:

- Opcode lama tetap diterima lewat `opcode_aliases` di `TOKEN.json`.
- VM runtime juga punya `OPCODE_ALIASES` untuk menjalankan `.idsm` string-opcode lama.

Status verifikasi VM:

- VM + CLI tests: `21 passed`.

### 4. CLI Publish Dengan Click

Kita membuat CLI publik berbasis `click` dengan format:

```bash
idscript <file> {-m|--module,-c|--bytecode,--both} <outputFile>
```

Perilaku CLI yang disepakati:

- `idscript file.ids` menjalankan interpreter normal.
- Tanpa flag compile, CLI tidak membuat `.idsm` atau `.idsc`.
- `idscript file.ids -m output` menulis `.idsm`.
- `idscript file.ids -c output` menulis `.idsc` saja, tanpa side effect `.idsm`.
- `idscript file.ids --both output` menulis `.idsm` dan `.idsc`.
- `idscript file.idsc` menjalankan bytecode via VM.
- `--main` memilih entrypoint selain `utama`.

File yang diubah:

- `src/IDScript/__main__.py`: diganti menjadi CLI Click.
- `setup.py`: dependency `click>=8.0` ditambahkan.
- `src/IDScript/compile/testing/test_cli.py`: test CLI ditambahkan.

Verifikasi CLI:

- `python -m IDScript --help`: OK.
- `python -m pytest testing/test_cli.py Compiler/testing/test_compiler.py -q`: `21 passed`.

### 5. Inventarisasi Project

Kita mengecek isi root `/sdcard/DCIM/workspace/IDScript/IDScript`.

Hasil inventarisasi:

- Total file: 172.
- File source/docs/tests relevan: 82.
- Cache/generated metadata: 90.

Kategori file sangat penting:

- `setup.py`
- `src/IDScript/__main__.py`
- `src/IDScript/__init__.py`
- `src/IDScript/gramm.lark`
- `src/IDScript/compile/entrypoint.py`
- `src/IDScript/compile/builtin.py`
- `src/IDScript/compile/ids_ast/nodes.py`
- `src/IDScript/compile/parser/transformer.py`
- `src/IDScript/compile/runtime/*`
- `src/IDScript/compile/Compiler/*`
- `src/IDScript/compile/Compiler/TOKEN.json`
- `src/IDScript/compile/Compiler/backend/vm_compiler.py`
- `src/IDScript/compile/Compiler/runtime/vm.py`

Kategori pendukung:

- `README.md`
- `ABOUT.md`
- `src/SYNTAX.md`
- `src/EXPLANATION.md`
- `src/TODO.md`
- `src/ROADMAP.json`
- `src/IDScript/builtins/*`
- `src/IDScript/compile/testing/*`
- `src/IDScript/compile/Compiler/testing/*`
- `src/IDScript/compile/Compiler/examples/*`

Kategori tambahan/generated:

- `__pycache__/`
- `.pytest_cache/`
- `.mypy_cache/`
- `idscript.egg-info/`
- session json lokal.
- log lokal seperti `error.txt`.

Temuan penting:

- Folder `Example/` di root ada tetapi kosong.
- `test_compile_example_file` masih mencari `Example/main.ids`.
- Karena itu full normal runtime test gagal kecuali test tersebut diskip.

### 6. Aturan Import Builtin dan Lokal

User menambahkan logika import di interpreter normal:

- Jika path import diawali `.`, maka import relatif dari file pemanggil.
- Jika path import tidak diawali `.`, maka import diarahkan ke folder `IDScript/builtins`.

Kita menyamakan logic ini pada VM compiler:

- `dari "./module.ids" impor { ... };` -> relatif ke file pemanggil.
- `dari "iterasi.ids" impor { ... };` -> folder builtin.
- `dari "atribut.ids" impor { ... };` -> folder builtin.

File yang diubah:

- `src/IDScript/compile/Compiler/backend/vm_compiler.py`
- Test lokal di `test_compile.py` dan `test_compiler.py` diperbarui memakai `./...`.
- Test builtin VM diperbarui agar memakai import builtin non-relatif.

Status verifikasi:

- VM + CLI: `21 passed`.
- Normal runtime tanpa missing example: `36 passed, 1 deselected`.

### 7. Revisi README dan setup.py

Kita merevisi `README.md` secara besar-besaran.

Isi baru README mencakup:

- Identitas proyek dan pembuat.
- Latar belakang IDScript sebagai penerus Indonesian Script.
- Status proyek.
- Kebutuhan dependency.
- Instalasi lokal dan dev.
- CLI `idscript`.
- Format file `.ids`, `.idsm`, `.idsc`, `.idbc`.
- Aturan import lokal vs builtin.
- Sintaks IDScript secara detail dan berpoin.
- Contoh untuk statement dan expression utama.
- Type annotation.
- Contoh program lengkap.
- Struktur project.
- Verifikasi test.
- Catatan lisensi masih `TODO`.

Kita juga merevisi `setup.py`:

- `description` diganti menjadi deskripsi singkat yang faktual.
- `author="Elang MRJ"`.
- `author_email="elangmuhamad888@gmail.com"`.
- `url="https://github.com/Elang-elang/IDScript"`.
- `project_urls` ditambahkan untuk IDScript dan Indonesian Script.
- `package_data` ditambah untuk builtin IDS:
  - `IDScript.builtins`: `*.ids`, `*.idsc`, `Regex/*.ids`

Verifikasi setelah revisi:

- `python -m IDScript --help`: OK.
- `python -m pytest testing/test_cli.py Compiler/testing/test_compiler.py -q`: `21 passed`.
- `python -m pytest testing/test_compile.py testing/test_struct_runtime.py -q -k 'not test_compile_example_file'`: `36 passed, 1 deselected`.
- `python setup.py --name` gagal karena environment tidak punya `setuptools`, bukan karena metadata.

## Memori Teknis Saat Ini

### Runtime Normal

- Entrypoint normal: `src/IDScript/compile/entrypoint.py`.
- Evaluator utama: `src/IDScript/compile/runtime/compiler.py`.
- Scope: `src/IDScript/compile/runtime/scope.py`.
- Config runtime: `src/IDScript/compile/runtime/config.py`.
- Struktur/trait/extend: `src/IDScript/compile/runtime/structure.py`.
- Enum normal: `src/IDScript/compile/runtime/enum.py`.
- Builtin normal: `src/IDScript/compile/builtin.py`.

### Compiler VM Resmi

- Package resmi: `src/IDScript/compile/Compiler`.
- API publik: `src/IDScript/compile/Compiler/api.py`.
- Compiler AST ke bytecode: `src/IDScript/compile/Compiler/backend/vm_compiler.py`.
- Runtime VM: `src/IDScript/compile/Compiler/runtime/vm.py`.
- Bytecode/module format: `src/IDScript/compile/Compiler/bytecode.py`.
- Opcode registry: `src/IDScript/compile/Compiler/TOKEN.json` dan `TOKEN.py`.

### Grammar dan Parser

- Grammar utama: `src/IDScript/gramm.lark`.
- AST dataclasses: `src/IDScript/compile/ids_ast/nodes.py`.
- Transformer: `src/IDScript/compile/parser/transformer.py`.

### CLI

- CLI publik: `src/IDScript/__main__.py`.
- Console script package: `idscript=IDScript.__main__:main`.
- Dependency CLI: `click>=8.0`.

### Builtins IDS

- Folder builtin: `src/IDScript/builtins`.
- Builtin IDS saat ini:
  - `atribut.ids`
  - `iterasi.ids`
  - `regex.idsc`
  - `Regex/*.ids`

Aturan import:

- `./...` berarti relatif ke file pemanggil.
- Tanpa `.` berarti cari di folder `IDScript/builtins`.

## Status Test Terakhir

Command yang berhasil:

```bash
python -m pytest Compiler/testing/test_compiler.py testing/test_cli.py -q
```

Hasil:

```text
21 passed
```

Command yang berhasil dengan skip test example kosong:

```bash
python -m pytest testing/test_compile.py testing/test_struct_runtime.py -q -k 'not test_compile_example_file'
```

Hasil:

```text
36 passed, 1 deselected
```

Command yang belum bisa diverifikasi karena dependency environment:

```bash
python setup.py --name
```

Alasan gagal:

```text
ModuleNotFoundError: No module named 'setuptools'
```

## Keputusan Penting

- Official VM adalah `src/IDScript/compile/Compiler`, bukan legacy `compile.VMCompiler`.
- Runtime normal dan VM resmi sama-sama penting.
- Opcode VM baru memakai gaya eksplisit seperti Python bytecode.
- Opcode lama tetap didukung sebagai alias.
- Import lokal wajib eksplisit memakai awalan `./`.
- Import non-relatif diarahkan ke builtins.
- `README.md` menjadi dokumentasi utama project.
- `setup.py` sekarang memuat metadata pembuat dan repository resmi.
- Builtins IDS harus ikut masuk package data saat publish.

## Hal Yang Masih Perlu Dikerjakan

- Pulihkan `Example/main.ids` atau ubah test lama yang masih mengharapkannya.
- Tentukan lisensi package, karena `setup.py` masih `license="TODO"`.
- Pastikan environment publish memiliki `setuptools`, `build`, dan tool upload yang dibutuhkan.
- Tambahkan `.gitignore` untuk cache/generated files jika belum ada.
- Bersihkan sebelum publish:
  - `__pycache__/`
  - `.pytest_cache/`
  - `.mypy_cache/`
  - `idscript.egg-info/`
  - session/log lokal.
- Pertimbangkan test packaging untuk memastikan `package_data` benar-benar memasukkan `builtins` dan `TOKEN.json`.
- VM masih perlu dukungan lebih lengkap untuk statement kompleks seperti `Try` jika ingin paritas penuh dengan interpreter normal.
- Dokumentasi syntax perlu terus disesuaikan setiap grammar berubah.

## Refleksi Diri Asisten

Selama percakapan ini, arah kerja berubah dari perbaikan internal runtime ke persiapan publish. Saya perlu menjaga dua hal sekaligus: stabilitas teknis dan dokumentasi pengguna. Beberapa keputusan penting muncul dari koreksi user, terutama tentang VM language yang sebaiknya mengikuti model Python VM, dan aturan import yang membedakan path lokal `./...` dari builtin non-relatif.

Hal yang berjalan baik:

- Saya memeriksa codebase sebelum mengubah file.
- Perbaikan runtime dilakukan bertahap dan diverifikasi dengan test.
- Perubahan VM opcode dibuat backward-compatible.
- CLI dibuat sesuai format yang diminta.
- README dan setup.py sudah diarahkan untuk publish.

Hal yang perlu lebih hati-hati:

- Jangan menganggap path import lama tanpa `./` sebagai lokal setelah aturan builtin disepakati.
- Jangan menganggap `Example/main.ids` masih ada; saat ini folder `Example/` kosong.
- Untuk packaging, test `setup.py` belum bisa dijalankan tanpa `setuptools`.
- Saat user meminta rencana, jangan langsung mengubah file; saat build mode aktif, lanjut implementasi.

## Ringkasan Singkat

IDScript sekarang memiliki runtime normal yang lebih stabil untuk trait/extend, VM compiler dengan opcode eksplisit ala Python, CLI Click yang siap publish, aturan import builtin/lokal yang konsisten, README lengkap, dan metadata setup.py yang sesuai identitas Elang MRJ. Test utama yang relevan sudah hijau, kecuali satu test lama yang bergantung pada `Example/main.ids` yang belum ada.
