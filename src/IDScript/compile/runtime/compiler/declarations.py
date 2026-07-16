from typing import Any, Callable, Type as T
from ...ids_ast import (
    Structure, BlockStruct, StructField, Implementation, ImplBlock, Method,
    Enum, TupleVariant, StructVariant, Discriminant, Trait, AbstractMethod,
    Function, Arguments, Arg,
)
from ...diagnostics import IDSAttributeError, IDSNameError, IDSTypeError
from ..scope import Scope
from ..structure import Structure as Struct
from ..variable import Variable as Var
from ..function import Function as RuntimeFunction
from ..factory import make_generic_factory


def Structure(self, node: Structure):
    name = node.name.id
    is_priv = node.is_priv
    generic_params = node.params

    if generic_params:
        generic_params_info = [self.v(p) for p in generic_params]
        parent_scope = self.current_scope
        self.current_scope = Scope(parent=parent_scope)
        for gp in generic_params_info:
            self.current_scope.declare(gp['name'], T, T, True, True)

        extend = None
        if node.extend:
            extend = self.v(node.extend)

        self.config.enter_struct(name)
        try:
            attrs = {}
            if node.body:
                attrs.update(self.v(node.body))
            struct = Struct(name, self.config, attrs, extend)
        finally:
            self.config.leave_struct()

        self.current_scope = parent_scope

        struct.__generic__ = generic_params_info
        struct._generic_method_asts = []
        struct._generic_cache = {}

        def build_struct_concrete(compiler):
            extend = None
            if node.extend:
                extend = compiler.v(node.extend)
            attrs = {}
            if node.body:
                attrs.update(compiler.v(node.body))
            return Struct(name, self.config, attrs, extend)

        struct.__generic_factory__ = make_generic_factory(
            self, name, generic_params_info,
            struct._generic_method_asts, struct._generic_cache,
            build_struct_concrete,
            set_expected=True,
        )
        self.current_scope.declare(name, Any, struct, True, is_priv)
        return

    extend = None
    if node.extend:
        extend = self.v(node.extend)

    self.config.enter_struct(name)
    try:
        attrs = {}
        if node.body:
            attrs.update(self.v(node.body))
        struct = Struct(name, self.config, attrs, extend)
    finally:
        self.config.leave_struct()

    self.current_scope.declare(name, Any, struct, True, is_priv)


def BlockStruct(self, node: BlockStruct):
    args = [self.v(arg) for arg in node.bodies]
    kwargs = {}
    for arg in args:
        kwargs[arg['name']] = {
            'type': arg['type'],
            'is_priv': arg['is_priv']
        }
    return kwargs


def StructField(self, node: StructField):
    name = node.name.id
    attr_type = self.v(node.type)
    is_priv = node.is_priv
    return {
        'name': name,
        'type': attr_type,
        'is_priv': is_priv,
    }


def Implementation(self, node: Implementation):
    import builtins
    struct_name = node.name.id
    struct = self.current_scope.get(struct_name)

    if node.params:
        generic_method_asts = getattr(struct, '_generic_method_asts', None)
        if generic_method_asts is not None:
            generic_method_asts.append({
                'params': node.params,
                'body': node.body,
                'trait': node.trait,
            })
        return

    if node.type_args:
        factory = getattr(struct, '__generic_factory__', None)
        if factory is not None:
            type_args = [self.v(ta) for ta in node.type_args]
            struct = factory(*type_args)

    kwargs_methods = self.v(node.body)
    self.config.enter_struct(struct_name)

    if node.trait:
        trait_obj = self.v(node.trait)
        trait_obj(kwargs_methods)

    try:
        for kwargs in kwargs_methods:
            builtins.getattr(struct, 'set_method')(**kwargs)
    finally:
        self.config.leave_struct()


def ImplBlock(self, node: ImplBlock):
    return [self.v(b) for b in node.bodies]


def Method(self, node: Method):
    import builtins
    name = node.name.id
    return_type = self.v(node.attrs.type)
    body = node.body.bodies or []
    struct_name = self.config.struct_name
    static = node.static

    generic_params = []
    if names := node.attrs.generic:
        generic_params = [name.id for name in names]

    lexical_parent = self.current_scope
    args_config = self.v(node.attrs.args)

    fn = RuntimeFunction(
        self, name, return_type, body, args_config,
        generic_params,
        is_method=True,
        struct_name=struct_name,
        lexical_parent=lexical_parent,
        type_node=node.attrs.type,
    )

    self.config.enter_struct('<object>')
    args = self.v(node.attrs.args)
    self.config.leave_struct()
    annotations = {}
    for arg, ann in zip(args['wrapp'], args['annotations']):
        annotations[arg.__name__] = ann

    annotations['return'] = return_type

    builtins.setattr(fn, '__annotations__', annotations)

    return {
        'name': name,
        'value': fn,
        'type': Callable[[...], Any],
        'is_priv': node.is_priv,
        'static': static,
    }


def Enum(self, node: Enum):
    from ..enum import Enum as EnumType
    name = node.name.id
    generic_params = node.params

    if generic_params:
        generic_params_info = [self.v(p) for p in generic_params]
        parent_scope = self.current_scope
        self.current_scope = Scope(parent=parent_scope)
        for gp in generic_params_info:
            self.current_scope.declare(gp['name'], T, T, True, True)

        self.config.enter_struct(name)
        try:
            raw_fields = [self.v(f) for f in node.fields]
            fields = {}
            for field in raw_fields:
                key = field['name']
                field.pop('name')
                fields[key] = field
            enum = EnumType(name, self.config, fields)
        finally:
            self.config.leave_struct()

        self.current_scope = parent_scope

        enum.__generic__ = generic_params_info
        enum._generic_method_asts = []
        enum._generic_cache = {}

        def build_enum_concrete(compiler):
            from ..enum import Enum as EnumType
            raw_fields = [compiler.v(f) for f in node.fields]
            fields = {}
            for field in raw_fields:
                key = field['name']
                field.pop('name')
                fields[key] = field
            return EnumType(name, self.config, fields)

        enum.__generic_factory__ = make_generic_factory(
            self, name, generic_params_info,
            enum._generic_method_asts, enum._generic_cache,
            build_enum_concrete,
        )
        self.current_scope.declare(name, Any, enum, True, node.is_priv)
        return

    self.config.enter_struct(name)
    try:
        raw_fields = [self.v(f) for f in node.fields]
        fields = {}
        for field in raw_fields:
            key = field['name']
            field.pop('name')
            fields[key] = field
        enum = EnumType(name, self.config, fields)
    finally:
        self.config.leave_struct()
    self.current_scope.declare(name, Any, enum, True, node.is_priv)


def TupleVariant(self, node: TupleVariant):
    if not node.args:
        return {
            'name': node.name.id,
            'kind': 'unit',
            'is_priv': node.is_priv
        }
    return {
        'name': node.name.id,
        'kind': 'tuple',
        'args': [self.v(arg) for arg in node.args],
        'is_priv': node.is_priv
    }


def StructVariant(self, node: StructVariant):
    raw_fields = [self.v(field) for field in node.fields]
    fields = {}
    for field in raw_fields:
        fields[field['name']] = field['type']
    return {
        'name': node.name.id,
        'kind': 'struct',
        'fields': fields,
        'is_priv': node.is_priv
    }


def Discriminant(self, node: Discriminant):
    return {
        'name': node.name.id,
        'kind': 'discriminant',
        'value': self.v(node.value),
        'is_priv': node.is_priv
    }


def Trait(self, node: Trait):
    name = node.name.id
    is_priv = node.is_priv
    generic_params = node.params

    if generic_params:
        generic_params_info = [self.v(p) for p in generic_params]
        parent_scope = self.current_scope
        self.current_scope = Scope(parent=parent_scope)
        for gp in generic_params_info:
            self.current_scope.declare(gp['name'], T, T, True, True)

        raw_data = [self.v(data) for data in node.data]
        self.current_scope = parent_scope

        data = {}
        for raw_d in raw_data:
            name_data = raw_d['name']
            data[name_data] = {
                key: value
                for key, value in raw_d.items()
                if key != 'name'
            }

        from ..structure import Trait as trait
        trait_obj = trait(name, data)
        trait_obj.__generic__ = generic_params_info
        self.current_scope.declare(name, Callable[[...], Any], trait_obj, True, is_priv)
        return

    raw_data = [self.v(data) for data in node.data]
    data = {}
    for raw_d in raw_data:
        name_data = raw_d['name']
        data[name_data] = {
            key: value
            for key, value in raw_d.items()
            if key != 'name'
        }

    from ..structure import Trait as trait
    self.current_scope.declare(
        name,
        Callable[[...], Any],
        trait(name, data),
        True,
        is_priv
    )


def AbstractMethod(self, node: AbstractMethod):
    args = self.v(node.attrs.args)
    return_type = self.v(node.attrs.type)
    static = node.static

    annotations = {}
    for arg, ann in zip(args['wrapp'], args['annotations']):
        annotations[arg.__name__] = ann

    annotations['return'] = return_type

    return {
        'name': node.name.id,
        'annotations': annotations,
        'type': Callable[[...], Any],
        'static': static,
    }


def Function(self, node: Function):
    name = node.name.id
    return_type = self.v(node.attrs.type)
    body = node.body.bodies or []
    is_priv = node.is_priv

    generic_params = []
    if names := node.attrs.generic:
        generic_params = [name.id for name in names]

    if name == 'utama':
        if generic_params:
            raise IDSAttributeError('Fungsi utama tidak boleh memiliki argumen generik')
        if node.attrs.args.args:
            raise IDSAttributeError('Fungsi utama tidak boleh memiliki argumen')
        if return_type != int and return_type != Optional[int]:
            raise IDSTypeError('Fungsi utama harus mengembalikan Angka')

    fn = RuntimeFunction(
        self, name, return_type, body, None,
        generic_params,
        is_method=False,
        lexical_parent=None,
        args_node=node.attrs.args,
        type_node=node.attrs.type,
    )
    self.current_scope.declare(
        name,
        Callable[..., return_type],
        fn,
        True,
        is_priv
    )


def Arguments(self, node: Arguments):
    if not node.args:
        return {
            'wrapp': [],
            'annotations': [],
        }
    res: dict[str, list[Any]] = {'wrapp': [], 'annotations': []}
    for arg in node.args:
        arg = self.v(arg)
        res['wrapp'].append(arg['wrapp'])
        res['annotations'].append(arg['annotation'])
    return res


def Arg(self, node: Arg):
    from typing import TypeAliasType
    name = node.name.id
    arg_type: Any = Any
    try:
        arg_type = self.v(node.type)
    except IDSNameError:
        if not self.config.is_struct_name('<object>'):
            raise
        type_name = getattr(getattr(node.type, 'type', None), 'id', None)
        arg_type = TypeAliasType(type_name, Any)

    def wrapper(val):
        if node.is_def:
            if not isinstance(val, Var):
                raise IDSTypeError(f'Argumen deferensial {name!r} membutuhkan referensial')
            self.current_scope.declare(name, arg_type, val, node.constant, True, True)
            return
        self.current_scope.declare(name, arg_type, val, node.constant)

    wrapper.__name__ = name

    return {
        'wrapp': wrapper,
        'annotation': arg_type,
    }


HANDLERS = [
    Structure, BlockStruct, StructField, Implementation, ImplBlock, Method,
    Enum, TupleVariant, StructVariant, Discriminant, Trait, AbstractMethod,
    Function, Arguments, Arg,
]
