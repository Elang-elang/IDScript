from typeguard import check_type
from typing import Any, Literal
from .types import *

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

type _EMPTY = None
def ValidateType(
    obj: Any,
    sbj: Any = _EMPTY
) -> Any:
    if sbj is _EMPTY:
        return _resolver_type(obj)

    obj = _resolver_type(obj)
    sbj = _resolver_type(sbj)
    if obj is Any or sbj is Any:
        return Any
    
    elif obj is sbj:
        return obj

    raise TypeError(f'Tipe yang tidak sama antara {obj} dan {sbj}')


def ValidateAttribute(
    obj:  Any,
    attr: str,
    *,
    getter: Any = getattr
) -> Any:
    if obj is Any:
        return Any

    elif getter:
        try:
            if getter(obj, attr):
                return obj
        except AttributeError:
            pass
        except Exception as e:
            print(f'Warning<{type(e)}>: {str(e)}')
            

    raise AttributeError(f'{obj} tidak memiliki atribut {attr!r}')


def _resolver_type(obj: Any) -> Any:
    py_to_ids = {
        str: Teks,
        int: AngkaBulat,
        float: Float,
        bool: Boolean,
        type(None): Literal[0],
        type(lambda: None): TypeFunction,
        type: TypeStructure
    }
    if obj in py_to_ids:
        return py_to_ids[obj]
    
    return obj