# IDScript Syntax for Acode

<p align="center">
  <img src="big.jpg" alt="IDScript" width="160">
</p>

Plugin Acode untuk syntax highlighting file IDScript (`.ids`) dan tampilan JSON untuk module/bytecode teks (`.idsm`, `.idsc`).

## Fitur

- Highlight contextual: kata seperti `dari`, `impor`, `final`, dan `jika` hanya diwarnai saat cocok dengan pola syntax IDScript, sehingga tetap bisa dipakai sebagai identifier di konteks lain.
- Highlight import eksplisit, misalnya `dari "Konsol.idsm" impor { publik println };`.
- Highlight tipe builtin sebagai soft keyword/type token: `Angka`, `Teks`, `Float`, `Boolean`, `Kosong`, `Apapun`, `daftar`, `kamus`, `hasil`.
- Highlight komentar `// ...` dan `/* ... */`.
- Highlight string, angka, operator, pointer `&nama`, `*ptr`, dan `salin ptr`.
- Theme opsional `ace/theme/idscript_night` bernuansa LazyVim/NvChad. Plugin tidak memaksa tema ini; warna highlight tetap mengikuti tema Acode default jika user tidak memilihnya.
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

Default-nya plugin memakai token standar Ace, jadi warna mengikuti tema Acode pengguna. Tema opsional `idscript_night` disediakan untuk user yang ingin tampilan gelap khusus IDScript.

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
├── theme-idscript-night.js
└── snippets/
    └── idscript.js
```

## Catatan

Tahap awal ini hanya syntax highlighting. Diagnostic real-time dari parser IDScript belum disertakan.
