from .fieldspace  import FieldSpace
from .namespace   import NameSpace
from .scope       import (
      TypeScope,  Scope,
      Global,     Local,
)

"""
Scoping & NameSpace dari IDScript
> Scope yang berguna untuk menyimpan variabel
- TypeScope : Merupakan Type dari semua Scope dan memuat properti abstrak dan metode bawaan
- Scope     : Sebuah wrapper untuk mengambil Global dan Local
- Global    : Sebuah Scope yang memuat Global Scope 
- Local     : Sebuah Scope yang memuat Local Scope

> NameSpace & FieldSpace yang menetapkan variabel
- NameSpace  (Penamaan)  : Penyimpanan variabel dengan lengkap dan dapat menjadi tempat konstanta juga
- FieldSpace (Penetapan) : Penyimpanan sementara untuk variabel kosong dan akan di transformasi ke NameSpace
                         | jika sudah termuat isi dari variabel nya

"""