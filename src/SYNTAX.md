# Syntax IDScript Untuk Pemula

Dokumen ini menjelaskan bentuk syntax yang sedang didukung compiler saat ini.

## Komentar

IDScript mendukung komentar satu baris dengan `...`.

```ids
... ini komentar
println("Halo"); ... komentar setelah statement
```

Komentar lama gaya C/C++ juga masih diterima oleh grammar:

```ids
// komentar
/* komentar */
```

## Konstanta

```ids
KONSTANTA nama: teks = "Budi";
KONSTANTA umur: angka = 20;
```

## Variabel

```ids
var hasil: angka = 10;
var kosong: ?angka;
```

## Final Lokal

```ids
final total: angka = 20;
```

## Fungsi

```ids
fungsi tambah(final a: angka, final b: angka): angka {
    kembalikan a + b;
}
```

Catatan:

- Argumen IDScript bersifat positional.
- Keyword argument biasa tidak digunakan untuk fungsi.
- `final` pada argumen membuat argumen tidak bisa di-assign ulang.

## Return Dan Throw

```ids
kembalikan 0;
kembalikan(0);
kesalahan "pesan";
```

## Tipe Bawaan

- `teks`: string Python.
- `angka`: integer Python.
- `float`: float Python.
- `boolean`: boolean Python.
- `kosong`: nilai kosong atau `None`.

## Optional Type

```ids
fungsi utama(): ?angka {
    kembalikan(0);
}
```

`?angka` berarti nilai boleh `angka` atau `kosong`.

## Struktur

Syntax `struktur` masih dalam tahap pengembangan.

```ids
struktur Orang {
    publik nama: teks,
    privat umur: angka,
}
```

Aturan desain saat ini:

- Field default adalah privat jika tidak memakai `publik`.
- Field publik boleh diakses dari luar.
- Field privat hanya boleh diakses saat runtime berada di konteks structure yang sama.

## Implementasi

Syntax `implementasi` juga masih dalam tahap pengembangan.

```ids
implementasi Orang {
    publik metode sapa(ini: Orang): teks {
        kembalikan ini.nama;
    }
}
```

Catatan:

- `ini` ditulis eksplisit agar mudah dibaca dan didebug.
- Runtime akan mengikat instance ke parameter `ini` saat method dipanggil.
- Method disimpan pada prototype/fields runtime structure, bukan sebagai fungsi global.

## Runtime Structure Python Native

Runtime `Utils/Struct.py` membuat class Python native melalui `type()`.

Contoh konsep Python runtime:

```python
Orang = Structure("Orang", config, {"nama": {"type": str}})
budi = Orang(nama="Budi")

assert type(budi).__name__ == "Orang"
assert budi.nama == "Budi"
```
