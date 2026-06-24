# Penjelasan Implementasi `struktur` dan `implementasi`

Dokumen ini menjelaskan arah implementasi fitur `struktur` dan `implementasi` berdasarkan runtime wrapper di `Utils/structure.py`, sekaligus memberi masukan untuk penguraian/parser dan node AST.

## Tujuan Desain

Fitur `struktur` sebaiknya menjadi tipe data buatan pengguna yang sederhana, berbahasa Indonesia, dan tetap mendukung type hint serta type checking. Model yang paling cocok untuk kondisi compiler saat ini adalah model Rust-lite/Go-lite:

```ids
struktur Orang {
    publik nama: teks;
    privat umur: angka;
}

implementasi Orang {
    fungsi sapa(ini): teks {
        kembalikan format("Halo {}", ini.nama);
    }
}
```

Model ini memisahkan deklarasi field dari method body. `struktur` berisi data/field, sedangkan `implementasi` berisi method untuk structure tersebut. Pemisahan ini lebih mudah dikompilasi daripada method bebas ala C yang harus ditebak pemiliknya, dan lebih sederhana daripada class penuh ala Python/JavaScript.

## Peran `Utils/structure.py`

File `Utils/structure.py` sekarang diarahkan menjadi runtime model untuk structure. Ada empat komponen utama:

1. `Config`
   Menyimpan nama structure yang sedang berada dalam konteks internal. Ini dipakai untuk mengizinkan akses field privat dari method milik structure yang sama.

2. `Structure`
   Merepresentasikan definisi/prototype structure. Contohnya `Orang`, bukan instance orang tertentu. Metadata disimpan dalam `__PROTOTYPE__`.

3. `StructureInstance`
   Merepresentasikan object hasil instansiasi structure. Contohnya hasil dari `Orang(nama="Budi", umur=20)`.

4. `Implementation`
   Wrapper untuk menambahkan method atau ekstensi ke prototype structure.

## Bentuk `__PROTOTYPE__`

`Structure` menyimpan metadata dalam `__PROTOTYPE__`:

```python
{
    "name": "Orang",
    "config": config,
    "scope": scope,
    "fields": {
        "nama": {
            "type": str,
            "is_priv": False,
            "constant": False,
            "default": None,
            "wrapp": None,
        }
    },
    "methods": {},
    "extends": {},
}
```

Nilai field instance tidak disimpan di `__PROTOTYPE__`. Nilai instance disimpan di `StructureInstance.__FIELDS__`:

```python
{
    "nama": "Budi",
    "umur": 20,
}
```

Pemisahan ini penting agar beberapa instance dari structure yang sama tidak saling menimpa nilai field.

## Native Attribute Access

`StructureInstance` memakai `__getattr__` dan `__setattr__` agar field IDScript bisa diakses seperti attribute Python runtime:

```python
orang.nama
orang.nama = "Andi"
orang.sapa()
```

Alur `orang.nama`:

1. Python memanggil `StructureInstance.__getattr__("nama")`.
2. Runtime mengecek apakah `nama` ada di `prototype["fields"]`.
3. Runtime mengecek visibility. Field `privat` hanya boleh diakses ketika `Config.name` sama dengan nama structure.
4. Runtime mengembalikan nilai dari `__FIELDS__["nama"]`.

Alur `orang.nama = "Andi"`:

1. Python memanggil `StructureInstance.__setattr__("nama", "Andi")`.
2. Runtime mengecek field ada atau tidak.
3. Runtime mengecek field `constant` atau tidak.
4. Runtime menjalankan `check_types(value, field_type)`.
5. Runtime menyimpan nilai baru ke `__FIELDS__`.

Alur `orang.sapa()`:

1. `__getattr__` melihat `sapa` ada di `prototype["methods"]`.
2. Runtime membuat function bound.
3. Sebelum method dijalankan, `Config.enter("Orang")` dipanggil.
4. Method dipanggil dengan instance sebagai argumen pertama, yaitu `ini`.
5. Setelah method selesai, `Config.leave(previous)` mengembalikan konteks lama.

## Rekomendasi Keyword `ini`

Untuk bahasa Indonesia, gunakan `ini` sebagai padanan `self`/`this`.

Saran penting: `ini` jangan dibuat global sungguhan. `ini` hanya boleh tersedia di scope method saat method dipanggil. Ini menjaga compiler tetap aman dan menghindari akses instance dari luar konteks method.

Contoh:

```ids
implementasi Orang {
    fungsi sapa(ini): teks {
        kembalikan format("Halo {}", ini.nama);
    }
}
```

Compiler cukup mengubah method tersebut menjadi wrapper Python yang menerima instance sebagai argumen pertama.

## Masukan Untuk Grammar

Grammar sebaiknya dibuat eksplisit dan konsisten dengan statement IDScript lain. Saya sarankan field structure diakhiri `;`, bukan dipisahkan koma, karena statement lain juga memakai semicolon.

Sketsa grammar:

```lark
outside_stmt: func_decl | struct_decl | impl_stmt

struct_decl: "struktur" NAME block_struct
block_struct: "{" struct_field* "}"
struct_field: visibility? final_mark? NAME ":" type_ann ";"

visibility: "publik" | "privat"
final_mark: "final"

impl_stmt: "implementasi" NAME block_impl
block_impl: "{" func_decl* "}"
```

Catatan:

1. Gunakan `implementasi`, bukan `implentasi`, agar sesuai bahasa Indonesia.
2. Hindari `assignment` di dalam `block_impl` pada tahap awal. Mulai dari `func_decl` saja agar method model stabil dulu.
3. Jangan implementasikan inheritance/extension dulu. Field dan method dasar harus stabil lebih dulu.
4. Jika ingin extension ala generic/trait, jadikan tahap lanjutan setelah instance dan method call selesai.

## Masukan Untuk Node AST

Node AST sebaiknya memisahkan field, block structure, block implementasi, dan method. Jangan menyimpan data runtime di node AST.

Sketsa node:

```python
from dataclasses import dataclass, field

@dataclass
class Structure(_STRUCTURE):
    name: Name
    body: "BlockStruct"

@dataclass
class BlockStruct(_STRUCTURE):
    fields: list["StructField"] = field(default_factory=list)

@dataclass
class StructField(_STRUCTURE):
    name: Name
    type: "Type"
    is_priv: bool = False
    constant: bool = False
    default: "Expression | None" = None

@dataclass
class Implementation(_STRUCTURE):
    name: Name
    body: "ImplBlock"
    extended: list[Name] = field(default_factory=list)

@dataclass
class ImplBlock(_STRUCTURE):
    methods: list[Function] = field(default_factory=list)
```

Catatan penting:

1. Pakai forward reference string atau `from __future__ import annotations` agar node bisa saling mereferensikan.
2. Jangan pakai default `[]` langsung di dataclass. Gunakan `field(default_factory=list)`.
3. Node `StructField` sebaiknya menggantikan `InitAttr` agar namanya lebih jelas.
4. `constant` bisa dipakai untuk field `final`.
5. `is_priv` cukup boolean untuk tahap awal. Jika nanti butuh visibility lebih kaya, baru ubah menjadi enum/string.

## Masukan Untuk Parser Transformer

Parser (`parse.py`) harus mengubah grammar menjadi node AST murni. Parser tidak boleh membuat object runtime `Structure` langsung.

Sketsa transformer:

```python
def struct_decl(self, name, body):
    return Structure(name=name, body=body)

def block_struct(self, *fields):
    return BlockStruct(fields=list(fields))

def struct_field(self, *parts):
    # Ambil visibility, final, name, type, default bila ada.
    return StructField(
        name=name,
        type=type_ann,
        is_priv=is_priv,
        constant=constant,
        default=default,
    )

def impl_stmt(self, name, body):
    return Implementation(name=name, body=body)

def block_impl(self, *methods):
    return ImplBlock(methods=list(methods))
```

Parser harus menjaga output tetap sederhana:

```text
grammar tree -> AST node -> compiler visitor -> runtime object
```

Jangan melompati tahap AST.

## Masukan Untuk Compiler

Compiler harus menjadi penghubung antara AST dan runtime wrapper `Utils/structure.py`.

Tahap compile `struktur`:

```python
def Structure(self, node):
    fields = self.v(node.body)
    struct = RuntimeStructure(node.name.id, self._config_struct, fields)
    self.current_scope.declare(node.name.id, type, struct, True)
```

Tahap compile field:

```python
def BlockStruct(self, node):
    return {
        field["name"]: field
        for field in [self.v(item) for item in node.fields]
    }

def StructField(self, node):
    return {
        "name": node.name.id,
        "type": self.v(node.type),
        "is_priv": node.is_priv,
        "constant": node.constant,
        "default": self.v(node.default) if node.default else None,
    }
```

Tahap compile `implementasi`:

```python
def Implementation(self, node):
    struct = self.current_scope.get(node.name.id)
    impl = RuntimeImplementation(node.name.id, self.current_scope, self._config_struct, struct)
    for method in node.body.methods:
        impl.add_method(method.name.id, self._compile_method(method))
```

Method binding harus meng-inject `ini`:

```python
def _compile_method(self, node):
    def method(instance, *args):
        parent = self.current_scope
        self.current_scope = Scope(parent=parent)
        self.current_scope.declare("ini", instance.__class__, instance, True)
        # bind parameter lain dan execute body
    return method
```

Catatan: type untuk `ini` sebaiknya nanti memakai tipe structure, bukan `instance.__class__`, tetapi tahap awal boleh dibuat pragmatis dulu.

## Masukan Untuk Attribute Access

Node `Attribute(value, attr)` sudah ada. Compiler bisa memanfaatkan native `getattr`:

```python
def Attribute(self, node):
    value = self.v(node.value)
    return getattr(value, node.attr)
```

Ini sudah cocok dengan `StructureInstance.__getattr__`.

Untuk assignment ke attribute, node assignment saat ini hanya menerima target `Name`. Perlu diperluas:

```python
def Assignment(self, node):
    if isinstance(node.target, Name):
        self.current_scope.set(node.target.id, self.v(node.expr))
    elif isinstance(node.target, Attribute):
        target = self.v(node.target.value)
        setattr(target, node.target.attr, self.v(node.expr))
```

Ini akan membuat sintaks seperti berikut bisa bekerja:

```ids
orang.nama = "Andi";
```

## Testing Yang Wajib Ditambahkan

Test minimal harus bertahap:

1. Runtime wrapper langsung:
   Membuat `Structure`, membuat instance, membaca field publik, menolak field privat, mengubah field publik, dan memanggil method.

2. Parser structure:
   Parse `struktur Orang { publik nama: teks; }` dan pastikan AST menghasilkan `Structure` dengan `StructField`.

3. Compiler structure:
   Compile deklarasi structure dan pastikan nama structure masuk scope.

4. Constructor:
   `Orang(nama="Budi")` menghasilkan `StructureInstance`.

5. Method binding:
   `orang.sapa()` menjalankan method yang menerima `ini`.

6. Visibility:
   `orang.umur` gagal dari luar jika `umur` privat, tetapi bisa dibaca dari method structure.

7. Assignment attribute:
   `orang.nama = "Andi"` berhasil jika bukan `final`, gagal jika `final`.

Skema verifikasi tetap:

```bash
python -m mypy .
python -m pytest
python compile.py
```

## Risiko Yang Perlu Dihindari

1. Jangan simpan nilai field instance di global scope.
   Ini akan membuat semua instance berbagi value field dan saling menimpa.

2. Jangan jadikan `ini` global permanen.
   `ini` hanya boleh hidup selama method dipanggil.

3. Jangan implementasikan inheritance/extension terlalu awal.
   Selesaikan structure, instance, method, dan visibility dulu.

4. Jangan campur runtime object ke parser.
   Parser harus menghasilkan AST saja.

5. Jangan memakai mutable default di dataclass.
   Selalu pakai `field(default_factory=list)` untuk list/dict.

## Urutan Patch Yang Disarankan

1. Patch stabilitas Python: import, syntax, forward reference, mutable default.
2. Patch grammar structure agar konsisten dan mudah diparse.
3. Patch node AST agar field dan implementation jelas.
4. Patch parser transformer agar semua rule baru menghasilkan node.
5. Patch compiler untuk mendaftarkan `Structure` ke scope.
6. Patch constructor dan instance creation.
7. Patch implementation dan method binding dengan `ini`.
8. Patch visibility dan assignment attribute.
9. Tambah test lengkap dan update dokumentasi.
