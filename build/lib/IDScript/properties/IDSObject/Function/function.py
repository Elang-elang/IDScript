from ...__helper    import ( setter,       deleter,
                             GetAttr,      SetAttr,
                             ReturnSignal              )
from ..._Reprer     import   Reprer
from ...TypeSystem  import   CheckType,    TypeFunction
from ...config      import   Configure
from .parameter      import   Parameter
from ..types        import   TypeField

from typing  import Any
from types   import FunctionType as _ft


@Reprer(writer='Fungsi')
class Function(TypeFunction.__origin__):
    def __init__(
        self,
        name:             str,
        fields:           list[TypeField] | list[Any],
        wrapper:          _ft,
        return_type:      Any,
        /, *,
        config:           Configure | None,
        
    ) -> None:
        handler_name = ''
        if config is None:
            cond = CheckType(fields, list[Any])
            if fields and not cond:
                raise AttributeError(f'Ada Kesalahan dari argumen dan pembungkus. Apakah Fungsi normal atau native python (bagian python)?')
            
            handler_name = '__native_py__'

        
        elif CheckType(config, Configure):
            cond = CheckType(fields, list[TypeField])
            if fields and not cond:
                raise AttributeError(f'Ada Kesalahan dari argumen dan pembungkus. Apakah Fungsi normal atau native python (bagian Fungsi)?')
            
            handler_name = '__native_ids__'

        
        else:
            raise TypeError(f'Seharusnya config harus bertipe berupa Configure')

        handler_func = GetAttr(self, handler_name)
        func_wrapper = handler_func(
            fields,
            wrapper,
            return_type,
            config=config
        )

        parameter = None
        params_type = []
        if CheckType(fields, list[TypeField]):
            parameter = Parameter() \
                        if not fields \
                        else Parameter(*fields)
            
            params_type.extend(parameter.params_type)
        
        else:
            parameter = fields
            params_type.extend(fields)

        # name & params
        SetAttr(self, 'name',                          name)
        SetAttr(self, 'parameter',                parameter)
        SetAttr(self, 'params_type',            params_type)
        
        # return_type
        SetAttr(self, 'return_type',            return_type)

        # private & save of params
        SetAttr(self, '_callable',             func_wrapper)
        
        SetAttr(self, '_raw_callable',              wrapper)
        SetAttr(self, '_fields',                     fields)
        SetAttr(self, '_config',                     config)


    def __getattr__(self, name: str) -> Any:
        if name in ( 'name',        'parameter',
                     'params_type', 'return_type' ):
            return GetAttr(self, name)
        raise AttributeError(f'Tidak ada atribut {name}')

    
    __setattr__ = setter
    __delattr__ = delattr
    
    
    def __native_ids__(
        self,
        fields:           list[TypeField],
        wrapper:          _ft,
        return_type:      Any,
        /, *,
        config:           Configure,
        
    ) -> Any:
        # constanta of parameter
        parameter = Parameter(*fields)
        
        # new function of wrapper
        def func_wrapper(*values) -> Any:
            # setting of scope
            config.enter_scope()
            config.enter_func()

            # getting arguments
            arguments = parameter() if not values else parameter(*values)
            for arg in arguments:
                # declare argument
                config.scope_name.current.def_name(**arg.to_dict())

            try:
                # running of wrapper if doen't has retrun signal, return signal with default value 0 (int)
                wrapper()
                raise ReturnSignal(0)

            # getting signal & checker
            except ReturnSignal as ret:
                CheckType(ret.value, return_type, soft=False)
                return ret.value
            
            except Exception as e:
                raise e
            
            finally:
                # setting leave to previos scope
                config.leave_scope()
                config.leave_func()
            
        return func_wrapper

        
    def __native_py__(
        self,
        fields:        list[Any],
        wrapper:       _ft,
        return_type:   Any,
        /, *,
        config: None,
        
    ) -> Any:
        # new function of wrapper
        def func_wrapper(*values) -> Any:
            # simple checker of arguments
            if len(values) != len(fields):
                raise AttributeError(f'Argumen yang dibutuhkan {len(self._fields)} yang diberi {len(values)}')

            if len(values) != 0 and len(fields) != 0:
                for i, value in enumerate(values):
                    CheckType(value, fields[i], soft=False)

            # check return native & return with signal return
            return_value: Any = None
            try:
                # call of wrapper
                if len(fields) == 0:
                    return_value = wrapper()
                    
                else:
                    return_value = wrapper(*values)

                # check return if no return or None, default return is 0 (int)
                if return_value is None:
                    raise ReturnSignal(0)
                
                raise ReturnSignal(return_value)

            # getting signal & checker
            except ReturnSignal as ret:
                CheckType(ret.value, return_type, soft=False)
                return ret.value
            
            except Exception:
                raise
        
        return func_wrapper


    def copy(self, /) -> Any:
        # getting raw properties to copying
        name        = GetAttr(self, 'name')
        
        fields      = GetAttr(self, '_fields')
        wrapper     = GetAttr(self, '_raw_callable')
        return_type = GetAttr(self, 'return_type')
        config      = GetAttr(self, '_config')

        f_copy = Function(
            name,
            fields,
            wrapper,
            return_type,
            config=config,
        )
        return f_copy
    

    
    def __call__(self, *values: tuple[Any]) -> Any:
        callable = GetAttr(self, '_callable')
        return callable(*values)

    
    def __class_getitem__(cls, *args: Any) -> TypeFunction:
        return TypeFunction[*args]

    
    def __repr__(self):
        return f'{self.name}({', '.join([repr(p) for p in self.parameter])}): {self.return_type}'