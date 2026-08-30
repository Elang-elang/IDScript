from typeguard import check_type
from typing import Any

def CheckType[T](
    cls:      T,
    instance: tuple[type[T | Any], ...] | type[T | Any],
    /, *,
    soft:     bool = True,
) -> bool:
    """
    Sistem tipe milik IDScript
    
    > Pengecekan tipe
    - CheckType : merupakan pengecekan tipe yang dikombinasikan dengan typeguard.check_type
                | dan dapat mengembalikan 'raise TypeError' / '-> bool'
                | dengan menambahkan keyword argument 'soft=True' atau 'soft=False'
                | dan bawaan adalahnya adalah soft=False (soft: bool = True)

    """
    res = False

    # check iteration of instance if type is tuple
    if isinstance(instance, tuple):
        raw_res = [ CheckType(cls, stance)
                    for stance in instance ]
        res = any(raw_res)
    
    # normal checker
    else:
        try:
            res = isinstance(cls, instance)
        except TypeError:
            pass


        if not res:
            try:
                # print(f'{type(cls) = }, {type(instance) = }')
                check_type(cls, instance)
                res = True
            except Exception as e:
                pass

    # checker and raise if not soft (harder)
    if not soft and not res:
        raise TypeError(f'Kesalahan tipe terhadap {cls!r} ({type(cls)}) dan {instance}')
    
    return res