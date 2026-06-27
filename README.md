<div align="center">

<img src="icons/big.jpg" alt="IDScript" width="160">

# IDScript

**Bahasa pemrograman berbahasa Indonesia dengan interpreter, compiler VM, dan bytecode resmi.**

`IDScript` / `IDS` = `I[n]D[onesian] Script` atau ringkasnya `I[n]D[o] Script`.

[Mulai Cepat](#mulai-cepat) • [CLI](#cli-idscript) • [Format File](#format-file) • [Sintaks](#panduan-sintaks) • [VM](#compiler-vm) • [Lisensi](#lisensi)

</div>

---

## Tentang

| Info | Nilai |
|---|---|
| Pembuat | Elang MRJ |
| GitHub | [`Elang-elang`](https://github.com/Elang-elang) |
| Email | `elangmuhamad888@gmail.com` |
| Repository | <https://github.com/Elang-elang/IDScript> |
| Pendahulu | [Indonesian Script / IS](https://github.com/Elang-elang/indonesian_script) |
| Status | Prototype / pre-alpha |
| Python | `>=3.13` |

<details open>
<summary><strong>Latar Belakang Singkat</strong></summary>

IDScript lahir sebagai kelanjutan dari Indonesian Script atau IS, sebuah proyek bahasa pemrograman berbahasa Indonesia yang sebelumnya dibuat sebagai prototype dan kemudian terbengkalai. IS membuktikan bahwa sintaks pemrograman dapat dibuat lebih dekat dengan istilah Indonesia, tetapi proyek tersebut belum memiliki struktur compiler, runtime, dan format bytecode yang cukup rapi untuk dilanjutkan sebagai bahasa yang lebih stabil.

IDScript meneruskan gagasan itu dengan fondasi baru: grammar Lark, AST, interpreter normal, compiler VM resmi, format module `.idsm`, format compiled bytecode `.idsc`, builtin runtime, dan CLI publik bernama `idscript`.

</details>

---

## Mulai Cepat

<details open>
<summary><strong>Instalasi Lokal</strong></summary>

```bash
python -m pip install -e .
```

Dengan dependency pengembangan:

```bash
python -m pip install -e .[dev]
```

</details>

<details open>
<summary><strong>Program Pertama</strong></summary>

```ids
fungsi utama(): Angka {
    println("Halo dari IDScript");
    kembalikan 0;
}
```

Jalankan:

```bash
idscript main.ids
```

</details>

---

## CLI `idscript`

Format utama:

```bash
idscript <file> {-m|--module,-c|--bytecode,--both} <outputFile>
```

<details open>
<summary><strong>Mode Interpreter</strong></summary>

Tanpa flag compile, `idscript` menjalankan interpreter normal dan tidak membuat `.idsm` atau `.idsc`.

```bash
idscript program.ids
```

Entrypoint default adalah `utama`. Entrypoint lain dapat dipilih dengan `--main`.

```bash
idscript program.ids --main jalankan
```

</details>

<details>
<summary><strong>Mode Module `.idsm`</strong></summary>

```bash
idscript program.ids -m build/program
idscript program.ids --module build/program.idsm
```

Jika `outputFile` tidak punya suffix, CLI otomatis memakai `.idsm`.

</details>

<details>
<summary><strong>Mode Bytecode `.idsc`</strong></summary>

```bash
idscript program.ids -c build/program
idscript program.ids --bytecode build/program.idsc
```

Mode ini menulis `.idsc` saja dan tidak membuat `.idsm` sebagai side effect.

</details>

<details>
<summary><strong>Mode Both</strong></summary>

```bash
idscript program.ids --both build/program
```

Output:

```text
build/program.idsm
build/program.idsc
```

</details>

<details>
<summary><strong>Menjalankan Bytecode</strong></summary>

File `.idsm`, `.idsc`, dan `.idbc` dapat diberikan langsung ke CLI.

```bash
idscript build/program.idsc
```

</details>

---

## Format File

| Format | Fungsi |
|---|---|
| `.ids` | Source IDScript yang ditulis manusia. |
| `.idsm` | IDScript Module, format module VM yang masih deskriptif/readable. |
| `.idsc` | IDScript Compiled, bytecode final yang opcode-nya dikodekan. |
| `.idbc` | Bytecode legacy dari VMCompiler lama, hanya kompatibilitas baca. |

<details>
<summary><strong>Alur Compile</strong></summary>

```text
program.ids -> program.idsm -> program.idsc -> VM
```

Contoh:

```bash
idscript app.ids --module app.idsm
idscript app.ids --bytecode app.idsc
idscript app.idsc
```

</details>

---

## Aturan Import

| Bentuk Import | Resolusi Path |
|---|---|
| `dari "./mod.ids" impor ...` | Relatif ke file pemanggil. |
| `dari "../mod.ids" impor ...` | Relatif ke file pemanggil. |
| `dari "iterasi.ids" impor ...` | Folder builtin `IDScript/builtins`. |
| `dari "atribut.ids" impor ...` | Folder builtin `IDScript/builtins`. |

```ids
dari "./math.ids" impor { var tambah, konstan VERSI };
dari "./math.ids" impor { var tambah sebagai plus };
dari "iterasi.ids" impor { var panjang, var Daftar };
```

---

## Panduan Sintaks

Bagian ini dibuat sebagai referensi cepat. Buka bagian yang dibutuhkan saja.

<details open>
<summary><strong>Tipe Bawaan</strong></summary>

| Tipe IDScript | Makna Runtime |
|---|---|
| `Teks` | String |
| `Angka` | Integer |
| `Float` | Float |
| `Boolean` | Boolean |
| `Kosong` | `kosong` / `None` |
| `Apapun` | Nilai bebas |
| `OBJEK` | Alias object Python untuk kebutuhan builtin |

```ids
var nama: Teks = "Budi";
var umur: Angka = 20;
var rasio: Float = 1.5;
var aktif: Boolean = benar;
var nihil: Kosong = kosong;
var bebas: Apapun = [1, "dua", benar];
```

</details>

<details>
<summary><strong>Komentar</strong></summary>

```ids
// komentar satu baris

/*
   komentar banyak baris
*/
```

</details>

<details>
<summary><strong>Konstanta `KONSTANTA`</strong></summary>

```ids
KONSTANTA NILAI: Angka = 10;
publik KONSTANTA VERSI: Teks = "0.1.0";
privat KONSTANTA RAHASIA: Teks = "internal";
```

Catatan:

- `KONSTANTA` hanya ada di top-level.
- `publik` berarti dapat diekspor dari module.
- Default visibility adalah privat.

</details>

<details>
<summary><strong>Variabel `var` dan Final `final`</strong></summary>

```ids
var nilai: Angka = 1;
nilai = nilai + 1;

final total: Angka = 100;
```

Optional type:

```ids
var mungkin: ?Angka = kosong;
```

</details>

<details>
<summary><strong>Return, Throw, Break, Continue</strong></summary>

```ids
fungsi ambil(): Angka {
    kembalikan 7;
}

fungsi gagal(): Teks {
    kesalahan "terjadi kesalahan";
}

fungsi hitung(): Angka {
    var total: Angka = 0;
    untuk (var angka dari dalam [1, 2, 3, 4]) {
        jika (angka == 2) { lanjutkan; }
        jika (angka == 4) { berhentikan; }
        total = total + angka;
    }
    kembalikan total;
}
```

</details>

<details open>
<summary><strong>Fungsi</strong></summary>

```ids
fungsi tambah(a: Angka, b: Angka): Angka {
    kembalikan a + b;
}

fungsi kali(final a: Angka, final b: Angka): Angka {
    kembalikan a * b;
}

publik fungsi utama(): Angka {
    kembalikan tambah(2, 3);
}
```

Catatan:

- Entrypoint default adalah `fungsi utama()`.
- Interpreter normal memperketat `utama` agar tidak menerima argumen dan mengembalikan `Angka` atau `?Angka`.

</details>

<details>
<summary><strong>If / Elif / Else</strong></summary>

```ids
fungsi status(nilai: Angka): Teks {
    jika (nilai > 80) {
        kembalikan "baik";
    } namun jika (nilai > 60) {
        kembalikan "cukup";
    } jika tidak {
        kembalikan "kurang";
    }
}
```

Negasi memakai `bukan`.

```ids
fungsi cek(flag: Boolean): Angka {
    jika (bukan flag) {
        kembalikan 0;
    }
    kembalikan 1;
}
```

Di VM, `jika (bukan x)` dikompilasi ke `TO_BOOL` lalu `POP_JUMP_IF_TRUE`.

</details>

<details>
<summary><strong>Loop `selama` dan `untuk`</strong></summary>

```ids
fungsi sampai_lima(): Angka {
    var angka: Angka = 0;
    selama (angka < 5) {
        angka = angka + 1;
    }
    kembalikan angka;
}
```

```ids
fungsi jumlah(): Angka {
    var total: Angka = 0;
    untuk (var angka dari dalam [1, 2, 3]) {
        total = total + angka;
    }
    kembalikan total;
}
```

Destructuring target:

```ids
fungsi jumlah_pasangan(): Angka {
    var total: Angka = 0;
    untuk (var (a, b) dari dalam [[1, 2], [3, 4]]) {
        total = total + a + b;
    }
    kembalikan total;
}
```

</details>

<details open>
<summary><strong>Try / Catch / Else / Finally</strong></summary>

```ids
fungsi aman(): Angka {
    var nilai: Angka = 0;

    coba {
        kesalahan 5;
    } tangkap (e) {
        nilai = 5;
    } jika tidak {
        nilai = 99;
    } diakhiri {
        nilai = nilai + 1;
    }

    kembalikan nilai;
}
```

Semantik mengikuti model Python:

- Blok `coba` dijalankan lebih dulu.
- Blok `tangkap` berjalan jika ada error.
- Blok `jika tidak` berjalan hanya jika tidak ada error.
- Blok `diakhiri` selalu berjalan, termasuk sebelum `kembalikan` keluar dari blok `coba`.

Catatan VM:

- VM resmi sudah mendukung `coba/tangkap/jika tidak/diakhiri` melalui opcode `SETUP_TRY`.
- Handler pertama menangani error yang dilempar oleh `kesalahan` atau exception runtime.

</details>

<details>
<summary><strong>Switch / Match `pilah`</strong></summary>

```ids
fungsi pilih(x: Angka): Teks {
    pilah (x) {
        kasus 1:
            kembalikan "satu";
        kasus 2:
            kembalikan "dua";
        kasus bawaan:
            kembalikan "lain";
    }
}
```

Pattern sequence:

```ids
fungsi total_data(): Angka {
    var total: Angka = 0;
    pilah ([1, 2, 3]) {
        kasus [kepala, ...ekor]:
            total = kepala + ekor[0] + ekor[1];
    }
    kembalikan total;
}
```

</details>

<details>
<summary><strong>Type Alias `tipe`</strong></summary>

```ids
tipe ID = Angka
tipe Nama = Teks

fungsi ambil_id(): ID {
    kembalikan 7;
}
```

Dynamic alias:

```ids
tipe Kotak[T] = daftar[T]
var angka: Kotak[Angka] = [1, 2, 3];
```

</details>

<details>
<summary><strong>Antarmuka `antarmuka`</strong></summary>

```ids
antarmuka User {
    nama: Teks,
    umur: Angka,
}

fungsi ambil_umur(user: User): Angka {
    kembalikan user["umur"];
}
```

</details>

<details open>
<summary><strong>Struktur, Turunan, Implementasi, dan Sifat</strong></summary>

Struktur:

```ids
struktur Orang {
    publik nama: Teks,
    privat umur: Angka,
}
```

Turunan:

```ids
struktur Makhluk {
    publik nama: Teks,
}

struktur Orang {
    publik umur: Angka,
} turunan dari Makhluk
```

Implementasi metode:

```ids
implementasi Orang {
    publik metode sapa(ini: Orang): Teks {
        kembalikan "Halo " + ini.nama;
    }
}
```

Sifat / trait:

```ids
sifat BisaSapa {
    metode sapa(ini: Orang): Teks;
}

implementasi BisaSapa untuk Orang {
    publik metode sapa(ini: Orang): Teks {
        kembalikan ini.nama;
    }
}
```

Aturan penting:

- Field default privat.
- Duplicate field saat turunan menghasilkan error.
- Duplicate method saat turunan menghasilkan error.
- Tidak ada override implicit.
- Trait memvalidasi nama argumen, tipe argumen, dan return type.

</details>

<details open>
<summary><strong>Enum</strong></summary>

Unit variant:

```ids
enum Gender {
    publik Pria,
    publik Wanita,
}
```

Tuple variant:

```ids
enum Data {
    publik Nomor(Angka),
    publik Pasangan(Teks, Angka),
}
```

Struct variant:

```ids
enum Event {
    publik Login { nama: Teks, umur: Angka },
}
```

Discriminant variant:

```ids
enum Kode {
    publik Oke = 200,
    publik Gagal = 500,
}
```

Metode enum:

```ids
implementasi Kode {
    publik metode nilai(ini: Apapun): Angka {
        kembalikan ini.value;
    }
}
```

</details>

<details>
<summary><strong>Expression</strong></summary>

Literal:

```ids
var teks: Teks = "halo";
var angka: Angka = 10;
var pecahan: Float = 3.14;
var flag: Boolean = benar;
var kosong_nilai: Kosong = kosong;
```

List dan kamus:

```ids
var angka: daftar[Angka] = [1, 2, 3];
var user: kamus[Teks, Apapun] = {"nama": "Budi", "umur": 20};
```

Call, attribute, dan index:

```ids
println("Halo");
var nama: Teks = user.nama;
var pertama: Angka = [1, 2, 3][0];
```

Operator:

```ids
var hasil: Angka = 1 + 2 * 3;
var pangkat: Angka = 2 ** 3;
```

Boolean dan comparison:

```ids
jika (benar dan bukan salah) {
    println("oke");
}

jika (2 didalam [1, 2, 3]) {
    println("ada");
}
```

`identifikasi` dan `info`:

```ids
var angka: Angka = 7;
var salin: Angka = identifikasi angka;

jika (info angka == "Angka") {
    println("ini angka");
}
```

Kategori `info` mencakup `Angka`, `Float`, `Boolean`, `Teks`, `Kosong`, `Daftar`, `Kamus`, `Struktur`, `Enum`, `VarianEnum`, `Tipe`, `Antarmuka`, `Fungsi`, dan `Objek`.

</details>

<details>
<summary><strong>Type Annotation Lanjutan</strong></summary>

```ids
var mungkin: ?Angka = kosong;
var angka: daftar[Angka] = [1, 2, 3];
var data: kamus[Teks, Angka] = {"a": 1};
var operasi: fungsi[[Angka, Angka], Angka];
var hasil_operasi: hasil[Angka, Teks];
var nilai: [Angka, Teks] = 1;
var mode: ["dev", "prod"] = "dev";
```

</details>

---

## Contoh Program Lengkap

<details open>
<summary><strong>Buka contoh</strong></summary>

```ids
tipe Nama = Teks

struktur Orang {
    publik nama: Nama,
    publik umur: Angka,
}

sifat BisaSapa {
    metode sapa(ini: Orang): Teks;
}

implementasi BisaSapa untuk Orang {
    publik metode sapa(ini: Orang): Teks {
        kembalikan "Halo " + ini.nama;
    }
}

fungsi utama(): Angka {
    final budi: Orang = Orang { nama: "Budi", umur: 20 };
    println(budi.sapa());

    jika (info budi == "Struktur") {
        println("Budi adalah struktur Orang");
    }

    kembalikan budi.umur;
}
```

</details>

---

## Compiler VM

<details open>
<summary><strong>Opcode bergaya Python</strong></summary>

VM resmi memakai opcode eksplisit agar mudah dibaca dan didebug.

| Lama | Baru |
|---|---|
| `CONST` | `LOAD_CONST` |
| `LOAD` | `LOAD_NAME` |
| `STORE` | `STORE_NAME` |
| `STORE_LOCAL` | `STORE_FAST` |
| `POP` | `POP_TOP` |
| `BINARY` | `BINARY_OP` |
| `COMPARE` | `COMPARE_OP` |
| `JUMP` | `JUMP_ABSOLUTE` |
| `JUMP_IF_FALSE` | `POP_JUMP_IF_FALSE` |
| `CALL` | `CALL_FUNCTION` |
| `RETURN` | `RETURN_VALUE` |

Opcode lama tetap didukung sebagai alias untuk kompatibilitas.

</details>

<details>
<summary><strong>Contoh bytecode konseptual if/else</strong></summary>

```text
LOAD_NAME pi
TO_BOOL
POP_JUMP_IF_FALSE L_else

LOAD_NAME pi
STORE_NAME Pi
JUMP_ABSOLUTE L_end

L_else:
LOAD_CONST 0
STORE_NAME Pi

L_end:
LOAD_CONST None
RETURN_VALUE
```

Catatan: label seperti `L_else` hanya simbol disassembler/compiler. Runtime tetap memakai offset angka.

</details>

---

## Struktur Project

| Path | Fungsi |
|---|---|
| `src/IDScript/__main__.py` | CLI publik `idscript`. |
| `src/IDScript/gramm.lark` | Grammar utama IDScript. |
| `src/IDScript/compile/entrypoint.py` | Entrypoint interpreter normal. |
| `src/IDScript/compile/ids_ast` | Definisi AST. |
| `src/IDScript/compile/parser` | Transformer parse tree ke AST. |
| `src/IDScript/compile/runtime` | Interpreter normal dan runtime model. |
| `src/IDScript/compile/Compiler` | Compiler VM resmi, bytecode, dan VM runtime. |
| `src/IDScript/builtins` | Builtin yang ditulis dalam IDScript. |

---

## Verifikasi

Jalankan dari folder `src/IDScript/compile`:

```bash
python -m pytest testing/test_cli.py Compiler/testing/test_compiler.py -q
python -m pytest testing/test_compile.py testing/test_struct_runtime.py -q -k 'not test_compile_example_file'
```

Catatan:

- Test VM dan CLI berjalan dengan command di atas.
- Test normal runtime penuh masih membutuhkan `Example/main.ids` pada root project.
- Folder `Example/` sebaiknya diisi kembali sebelum rilis publik final.

---

## Lisensi

IDScript menggunakan **MIT License**.

<details open>
<summary><strong>Ringkasan Lisensi</strong></summary>

- Kamu boleh memakai, menyalin, memodifikasi, menggabungkan, mempublish, mendistribusikan, sublicense, dan menjual IDScript.
- Kamu boleh memakai IDScript untuk proyek pribadi, pendidikan, riset, maupun komersial.
- Copyright notice dan permission notice MIT harus tetap disertakan pada salinan atau bagian substantial dari software.
- IDScript diberikan apa adanya, tanpa garansi apa pun.
- Pembuat dan pemegang hak cipta tidak bertanggung jawab atas klaim, kerusakan, atau masalah lain dari penggunaan IDScript.

Lihat file [`LICENSE.md`](LICENSE.md) untuk teks lengkap.

</details>
