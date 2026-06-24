# TODO Patch Berikutnya

Daftar ini berisi pekerjaan lanjutan yang disarankan setelah patch saat ini.

## Prioritas Tinggi

1. Tambahkan test aritmetika yang lebih granular.
   Grammar `mul_`, `div_`, dan `pow_` sudah memakai operator yang benar dan example sudah menguji hasil runtime. Patch berikutnya sebaiknya menambah unit test terpisah untuk precedence dan associativity, misalnya `1 + 2 * 3`, `(1 + 2) * 3`, dan `2 ** 3`.

2. Perbaiki statement `return_stmt` dan `throw_stmt` agar tidak ambigu.
   Saat ini grammar sudah mendukung `kembalikan(0);`, tetapi perlu test tambahan untuk `kembalikan 0;`, `kesalahan("x");`, dan nested expression.

3. Tambahkan error message yang lebih ramah di `compile.py`.
   Error dari Lark dan runtime compiler sebaiknya dibungkus dengan informasi filename, line, column, dan snippet kode IDScript.

4. Tambahkan test untuk builtin IO.
   Minimal test `println`, `print`, `format`, `eprint`, dan `masukan` dengan mock stdin/stdout/stderr.

5. Validasi return type fungsi.
   Saat ini fungsi dapat mengembalikan nilai tanpa pengecekan eksplisit terhadap annotation return. Tambahkan check agar `fungsi utama(): angka { kembalikan("x"); }` gagal dengan error jelas.

## Prioritas Menengah

6. Rapikan API parsing, compiling, dan running.
   `Compile.__init__` sekarang melakukan parse/compile dan `main()`/`run()` menjalankan fungsi. Patch berikutnya sebaiknya merapikan nama method, memperbaiki typo `sefty_run`, dan menambahkan test untuk `run("nama_fungsi")`.

7. Tambahkan mode tanpa auto-run.
   Berguna untuk test atau tooling yang hanya ingin parse/compile tanpa menjalankan efek samping seperti `println`.

8. Perkuat type annotation internal.
   Banyak method visitor masih tanpa type hints lengkap. Tambahkan bertahap setelah perilaku runtime stabil.

9. Hindari `from node import *`.
   Ganti dengan import eksplisit agar dependency antar node lebih jelas dan static analysis lebih kuat.

10. Tambahkan test assignment dan constant.
    Uji `var`, `final`, `KONSTANTA`, assignment normal, dan assignment ke constant/final yang harus gagal.

## Prioritas Rendah

11. Format kode dengan formatter konsisten.
    Pertimbangkan konfigurasi `black`/`ruff`/`isort` jika proyek mulai membesar.

12. Tambahkan dokumentasi mini bahasa IDScript.
    Minimal dokumentasikan syntax fungsi, variable, tipe builtin, list, dict, return, throw, dan function call.

13. Tambahkan CLI argument ke `compile.py`.
    Contoh: `python compile.py ../../../Example/main.ids`, bukan hardcoded ke `Example/main.ids`.

14. Tambahkan test untuk string escape.
    Karena `TEKS` sudah mendukung escaped chars, perlu test untuk `"baris\\nbaru"`, quote escaped, dan backslash.

15. Evaluasi warning dependency `lark` pada Python 3.13.
    Warning `sre_parse` dan `sre_constants` berasal dari dependency. Tidak memblokir, tetapi bisa dipantau saat upgrade Lark.
