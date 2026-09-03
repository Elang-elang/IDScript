from .._Reprer   import Reprer
from dataclasses import dataclass
from typing      import TypeAliasType, Any, Literal, Union, TypedDict, NotRequired

from types       import FunctionType

"""
Sistem tipe milik IDScript

> Tipe Alias [ Alias : type ]:
- Teks       : str
- AngkaBulat : int
- Float      : float
- Boolean    :  0   |   1
- Angka      : int  | float
- Primitif   : Teks | Angka | Float | Boole
"""

# default type
type Teks       = str
type AngkaBulat = int
type Float      = float

# union type / alias type
type Boolean    = Literal[0, 1]
type Angka      = Union[int, float]

# any alias for default type
type Primitif   = Union[
    Teks, AngkaBulat, Float,
    Boolean, Angka,
]

def get_primitive_type():
    return {
        'Teks': Teks,
        'AngkaBulat': AngkaBulat,
        'Float': Float,
        'Boolean': Boolean,
        'Angka': Angka
    }

@Reprer(writer='TipeFungsi', keyword_only=True,)
@dataclass
class TypeFunction:
    """
    Sistem tipe milik IDScript
    
    > Tipe Asli dari pembungkust
    - TypeFunction : merupakan tipe yang terinspirasi dari typing.Callable
                     dan dapat dipanggil seperti generik tipe pada python:
                 
                     ```python
                     >>> TypeFunction[[arg1, arg2], return]
                     ```
                     disini (pada TypeFunction) tidak bisa menanonim panjang argumen
                     dan harus serba eksplisit
    """
    params_type: list[Any]
    return_type: Any

    def __check_return(self, cls: Any, /) -> bool:
        return cls.return_type is self.return_type

    def __check_params(self, cls: Any, /) -> bool:
        return all([
            param_type is self.params_type[i]
            for i, param_type in enumerate(cls.params_type)
        ])

    def __class_getitem__(cls, *args):
        if isinstance(args[0], tuple):
            return cls.__class_getitem__(*args[0])
        
        if len(args) != 2:
            raise TypeError('TypeFunction must be used as Callable[[arg, ...], result]')

        params_type: list[Any] = []
        if isinstance(args[0], list):
            params_type.extend(args[0])
            
        else:
            params_type.append(args[0])

        return_type: Any = args[1]
        return cls(
            params_type=params_type,
            return_type=return_type
        )

    def __instancecheck__(self, instance: Any, /) -> bool:
        return self.check_type(instance)

    def __repr__(self):
        write_params = ', '.join(
            str(param_type)
            for param_type in self.params_type
        )
        
        return f'TypeFunction[[{write_params}], {str(self.return_type)}]'

    def check_type(self, cls: Any) -> bool:
        if type(cls).__name__ not in ('Function', 'Method'):
            return False
        
        return all([
            self.__check_return(cls),
            self.__check_params(cls)
        ])


class TypeField(TypedDict):
    name:     str
    type:     Any
    constant: NotRequired[bool]
    private:  NotRequired[bool]


class TypeStructure(type):
    def __new__(
        cls,
        name:                  str,
        bases:     tuple[Any, ...],
        namespace:  dict[str, Any],
    ) -> type:
        return super().__new__(cls, name, bases, namespace)

    def __getattribute__(cls, name: str) -> Any:
        try:
            return super().__getattribute__(name)
        except AttributeError:
            prototype = cls.__dict__.get('PROTOTYPE')
            if prototype is not None:
                try:
                    return prototype.get_name(name)
                except (NameError, PermissionError):
                    pass
            raise

    def __setattr__(cls, name: str, value: Any, /) -> None:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            try:
                prototype.set_name(name, value)
                return
            except (NameError, AttributeError):
                pass
        super().__setattr__(name, value)

    def __delattr__(cls, name: str) -> None:
        raise PermissionError(f'Tidak dapat menghapus atribut {name}')


    def __getitem__(cls, name: str, /) -> Any:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            prototype.config.enter_struct(prototype.name_struct)
            try:
                return cls.__getattribute__('ambil_item')(name)
            except NameError:
                raise NotImplementedError(f'Tidak ada penanganan "ambil_item" pada {prototype.name_struct}')
            finally:
                prototype.config.leave_struct()
            
        raise NotImplementedError(f'Tidak ada penanganan "ambil_item"')

    def __setitem__(cls, name: str, value: Any, /) -> None:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            prototype.config.enter_struct(prototype.name_struct)
            try:
                cls.__getattribute__('atur_item')(name, value)
                return
            except NameError:
                raise NotImplementedError(f'Tidak ada penanganan "atur_item" pada {prototype.name_struct}')
            finally:
                prototype.config.leave_struct()
            
        raise NotImplementedError(f'Tidak ada penanganan "atur_item"')

    
    def __delitem__(cls, name: str, /) -> None:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            prototype.config.enter_struct(prototype.name_struct)
            try:
                cls.__getattribute__('hapus_item')(name)
                return
            except NameError:
                raise NotImplementedError(f'Tidak ada penanganan "hapus_item" pada {prototype.name_struct}')
            finally:
                prototype.config.leave_struct()
            
        raise NotImplementedError(f'Tidak ada penanganan "hapus_item"')


    def __contains__(cls, value: Any, /) -> bool:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            prototype.config.enter_struct(prototype.name_struct)
            try:
                return bool(cls.__getattribute__('termasuk')(value))
            except NameError:
                raise NotImplementedError(f'Tidak ada penanganan "termasuk" pada {prototype.name_struct}')
            finally:
                prototype.config.leave_struct()
        raise NotImplementedError(f'Tidak ada penanganan "termasuk"')

    def __bool__(cls) -> bool:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            prototype.config.enter_struct(prototype.name_struct)
            try:
                return bool(cls.__getattribute__('kondisi'))
            except NameError:
                raise NotImplementedError(f'Tidak ada penanganan "kondisi" pada {prototype.name_struct}')
            finally:
                prototype.config.leave_struct()
        raise NotImplementedError(f'Tidak ada penanganan "kondisi"')

    def __eq__(cls, value: Any, /) -> bool:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            prototype.config.enter_struct(prototype.name_struct)
            try:
                return bool(cls.__getattribute__('sama')(value))
            except NameError:
                raise NotImplementedError(f'Tidak ada penanganan "sama" pada {prototype.name_struct}')
            finally:
                prototype.config.leave_struct()
            
        raise NotImplementedError(f'Tidak ada penanganan "sama"')

    def __ne__(cls, value: Any, /) -> bool:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            prototype.config.enter_struct(prototype.name_struct)
            try:
                return bool(cls.__getattribute__('tidak_sama')(value))
            except NameError:
                raise NotImplementedError(f'Tidak ada penanganan "tidak_sama" pada {prototype.name_struct}')
            finally:
                prototype.config.leave_struct()
            
        raise NotImplementedError(f'Tidak ada penanganan "tidak_sama"')

    def __gt__(cls, value: Any, /) -> bool:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            prototype.config.enter_struct(prototype.name_struct)
            try:
                return bool(cls.__getattribute__('lebih_besar')(value))
            except NameError:
                raise NotImplementedError(f'Tidak ada penanganan "lebih_besar" pada {prototype.name_struct}')
            finally:
                prototype.config.leave_struct()
            
        raise NotImplementedError(f'Tidak ada penanganan "lebih_besar"')

    def __ge__(cls, value: Any, /) -> bool:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            prototype.config.enter_struct(prototype.name_struct)
            try:
                return bool(cls.__getattribute__('besar_sama')(value))
            except NameError:
                raise NotImplementedError(f'Tidak ada penanganan "besar_sama" pada {prototype.name_struct}')
            finally:
                prototype.config.leave_struct()
            
        raise NotImplementedError(f'Tidak ada penanganan "besar_sama"')

    def __lt__(cls, value: Any, /) -> bool:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            prototype.config.enter_struct(prototype.name_struct)
            try:
                return bool(cls.__getattribute__('lebih_kecil')(value))
            except NameError:
                raise NotImplementedError(f'Tidak ada penanganan "lebih_kecil" pada {prototype.name_struct}')
            finally:
                prototype.config.leave_struct()
            
        raise NotImplementedError(f'Tidak ada penanganan "lebih_kecil"')

    def __le__(cls, value: Any, /) -> bool:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            prototype.config.enter_struct(prototype.name_struct)
            try:
                return bool(cls.__getattribute__('kecil_sama')(value))
            except NameError:
                raise NotImplementedError(f'Tidak ada penanganan "kecil_sama" pada {prototype.name_struct}')
            finally:
                prototype.config.leave_struct()
            
        raise NotImplementedError(f'Tidak ada penanganan "kecil_sama"')

    def __add__(cls, value: Any, /) -> Any:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            prototype.config.enter_struct(prototype.name_struct)
            try:
                return cls.__getattribute__('pertambahan')(value)
            except NameError:
                raise NotImplementedError(f'Tidak ada penanganan "pertambahan" pada {prototype.name_struct}')
            finally:
                prototype.config.leave_struct()
            
        raise NotImplementedError(f'Tidak ada penanganan "pertambahan"')

    def __sub__(cls, value: Any, /) -> Any:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            prototype.config.enter_struct(prototype.name_struct)
            try:
                return cls.__getattribute__('pengurangan')(value)
            except NameError:
                raise NotImplementedError(f'Tidak ada penanganan "pengurangan" pada {prototype.name_struct}')
            finally:
                prototype.config.leave_struct()
            
        raise NotImplementedError(f'Tidak ada penanganan "pengurangan"')

    def __mul__(cls, value: Any, /) -> Any:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            prototype.config.enter_struct(prototype.name_struct)
            try:
                return cls.__getattribute__('perkalian')(value)
            except NameError:
                raise NotImplementedError(f'Tidak ada penanganan "perkalian" pada {prototype.name_struct}')
            finally:
                prototype.config.leave_struct()
            
        raise NotImplementedError(f'Tidak ada penanganan "perkalian"')

    def __truediv__(cls, value: Any, /) -> Any:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            prototype.config.enter_struct(prototype.name_struct)
            try:
                return cls.__getattribute__('pembagian')(value)
            except NameError:
                raise NotImplementedError(f'Tidak ada penanganan "pembagian" pada {prototype.name_struct}')
            finally:
                prototype.config.leave_struct()
            
        raise NotImplementedError(f'Tidak ada penanganan "pembagian"')

    def __pow__(cls, value: Any, /) -> Any:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            prototype.config.enter_struct(prototype.name_struct)
            try:
                return cls.__getattribute__('perpangkatan')(value)
            except NameError:
                raise NotImplementedError(f'Tidak ada penanganan "perpangkatan" pada {prototype.name_struct}')
            finally:
                prototype.config.leave_struct()
            
        raise NotImplementedError(f'Tidak ada penanganan "perpangkatan"')

    def __int__(cls) -> int:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            prototype.config.enter_struct(prototype.name_struct)
            try:
                return int(cls.__getattribute__('ke_angka')())
            except NameError:
                raise NotImplementedError(f'Tidak ada penanganan "ke_angka" pada {prototype.name_struct}')
            finally:
                prototype.config.leave_struct()
            
        raise NotImplementedError(f'Tidak ada penanganan "ke_angka"')

    def __str__(cls) -> str:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            prototype.config.enter_struct(prototype.name_struct)
            try:
                return cls.__getattribute__('ke_teks')()
            except NameError:
                try:
                    return cls.__getattribute__('tulisan')()
                except NameError:
                    pass
                
                raise NotImplementedError(f'Tidak ada penanganan "ke_teks" pada {prototype.name_struct}')
            finally:
                prototype.config.leave_struct()
            
        raise NotImplementedError(f'Tidak ada penanganan "ke_teks"')


    def __float__(cls) -> float:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            prototype.config.enter_struct(prototype.name_struct)
            try:
                return float(cls.__getattribute__('ke_float')())
            except NameError:
                raise NotImplementedError(f'Tidak ada penanganan "ke_float" pada {prototype.name_struct}')
            finally:
                prototype.config.leave_struct()
            
        raise NotImplementedError(f'Tidak ada penanganan "ke_float"')

    def __copy__(cls) -> Any:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            prototype.config.enter_struct(prototype.name_struct)
            try:
                return cls.__getattribute__('salin')()
            except NameError:
                raise NotImplementedError(f'Tidak ada penanganan "salin" pada {prototype.name_struct}')
            finally:
                prototype.config.leave_struct()
            
        raise NotImplementedError(f'Tidak ada penanganan "salin"')

    def __deepcopy__(cls) -> Any:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            prototype.config.enter_struct(prototype.name_struct)
            try:
                return cls.__getattribute__('salin_mendalam')()
            except NameError:
                try:
                    return cls.__getattribute__('salin')()
                except NameError:
                    raise NotImplementedError(f'Tidak ada penanganan "salin_mendalam" pada {prototype.name_struct}')
            finally:
                prototype.config.leave_struct()
            
        raise NotImplementedError(f'Tidak ada penanganan "salin_mendalam"')

    
    def __repr__(cls) -> str:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            prototype.config.enter_struct(prototype.name_struct)
            try:
                return cls.__getattribute__('tulisan')()
            except NameError:
                raise NotImplementedError(f'Tidak ada penanganan "tulisan" pada {prototype.name_struct}')
            finally:
                prototype.config.leave_struct()
        
        return 'types.TypeStructure'
    
    def __instancecheck__(cls, instance: Any, /) -> bool:
        prototype = cls.__dict__.get('PROTOTYPE')
        if prototype is not None:
            prototype.config.enter_struct(prototype.name_struct)
            try:
                return bool(cls.__getattribute__('cek_jangkauan')(instance))
            except NameError:
                raise NotImplementedError(f'Tidak ada penanganan "cek_jangkauan" pada {prototype.name_struct}')
            finally:
                prototype.config.leave_struct()
            
        return type(instance) is TypeStructure