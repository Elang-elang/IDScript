# IDScript Syntax for Acode

<p align="center">
  <img src="big.jpg" alt="IDScript" width="160">
</p>

Plugin Acode untuk syntax highlighting file IDScript (`.ids`) dan tampilan JSON untuk module/bytecode teks (`.idsm`, `.idsc`).

## Fitur

- Highlight keyword IDScript: `fungsi`, `struktur`, `implementasi`, `jika`, `coba`, `tangkap`, dan lainnya.
- Highlight tipe builtin: `Angka`, `Teks`, `Float`, `Boolean`, `Kosong`, `Apapun`, `OBJEK`.
- Highlight komentar `// ...` dan `/* ... */`.
- Highlight string, angka, operator, pointer `&nama`, `*ptr`, dan `salin ptr`.
- Auto indent sederhana setelah `{`, `(`, dan `[`.
- Comment toggle memakai `//`.
- Snippet dasar untuk `fungsi`, `utama`, `jika`, `coba`, `struktur`, dan `implementasi`.
- File `.idsm` dan `.idsc` tetap memakai suffix asli, tetapi dibuka dengan mode syntax JSON.

## Scope

Plugin ini mendaftarkan mode untuk:

- `.ids`: syntax IDScript.
- `.idsm`: syntax JSON untuk module hasil compile.
- `.idsc`: syntax JSON untuk bytecode/compiled output berbasis teks.

## Warna

Plugin memakai token standar Ace, jadi warna mengikuti tema Acode pengguna. Tidak ada warna hardcoded.

## Icon

Plugin ini menyertakan dua icon agar paket Acode self-contained:

- `big.jpg`: gambar display/README.
- `small.jpg`: icon plugin dan metadata file IDScript.

## Struktur

```text
plugins/acode-idscript/
├── big.jpg
├── main.js
├── mode-idscript.js
├── package.json
├── plugin.json
├── README.md
├── small.jpg
└── snippets/
    └── idscript.js
```

## Catatan

Tahap awal ini hanya syntax highlighting. Diagnostic real-time dari parser IDScript belum disertakan.
