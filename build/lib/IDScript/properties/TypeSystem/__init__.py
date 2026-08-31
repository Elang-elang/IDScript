from .types import (
    Teks,          AngkaBulat,         Float,
    Boolean,       Angka,           Primitif,
    TypeFunction,  TypeField,  TypeStructure,
)

from .system import CheckType

"""
Sistem tipe milik IDScript

> Tipe Alias [ Alias : type ]:
- Teks       : str
- AngkaBulat : int
- Float      : float
- Boolean    :  0   |   1
- Angka      : int  | float
- Primitif   : Teks | Angka | Float | Boolean

> Tipe Asli dari pembungkust
- TypeFunction : merupakan tipe yang terinspirasi dari typing.Callable
                 dan dapat dipanggil seperti generik tipe pada python:
                 
                 ```python
                 >>> TypeFunction[[arg1, arg2], return]
                 ```
                 disini (pada TypeFunction) tidak bisa menanonim panjang argumen
                 dan harus serba eksplisit

> Pengecekan tipe
- CheckType : merupakan pengecekan tipe yang dikombinasikan dengan typeguard.check_type
            | dan dapat mengembalikan 'raise TypeError' / '-> bool'
            | dengan menambahkan keyword argument 'soft=True' atau 'soft=False'
            | dan bawaan adalahnya adalah soft=False (soft: bool = True)

"""