"""Lark transformer that converts grammar parse trees into IDScript AST nodes."""

from lark import Transformer, v_args
from ..ids_ast import *
from ..diagnostics import set_source, span_from_meta, span_from_token
from ..runtime.types import EMPTY

_OPTIONAL_SENTINEL = object()

class _ParamList(list):
    pass

class _TypeArgList(list):
    pass

def _is_params(x):
    return isinstance(x, _ParamList)

def _is_type_args(x):
    return isinstance(x, _TypeArgList)

@v_args(inline=True)
class _Parse(Transformer):
    def __init__(self, file: str = "<unknown>", source: str | None = None):
        self.file = file
        self.source = source

    def _call_userfunc(self, tree, new_children=None):
        result = super()._call_userfunc(tree, new_children)
        return set_source(result, span_from_meta(tree.meta, self.file, self.source))

    def _ambig(self, *trees):
        from ..ids_ast import Compare, StructFielded, CallDynamic
        flat = []
        for t in trees:
            if isinstance(t, list):
                flat.extend(t)
            else:
                flat.append(t)
        non_compare = [t for t in flat if not isinstance(t, Compare)]
        if non_compare:
            return non_compare[0]
        return flat[0]

    def _call_userfunc_token(self, token):
        result = super()._call_userfunc_token(token)
        return set_source(result, span_from_token(token, self.file, self.source))

    _PASSTHROUGH_RULES = {
        'const_decl', 'struct_decl', 'private_struct',
        'struct_fields', 'impl_stmt', 'enum_body', 'private_field_attr',
        'field_attr', 'trait_stmt', 'func_decl', 'pattern', 'import_decl',
        'dval',
    }

    def __default__(self, data, children, meta):
        if data in self._PASSTHROUGH_RULES:
            result = children[0] if len(children) == 1 else (list(children) if children else None)
            return set_source(result, span_from_meta(meta, self.file, self.source))
        return super().__default__(data, children, meta)
    
    # The PROGRAM
    def start(self, prog):
        return prog
    
    def prog(self, *stmts):
        return Program(bodies=stmts or None)
    
    
    # STATEMENTS
    def top_stmt(self, body):
        return Top(body=body)
    
    def block(self, *bodies):
        return Block(bodies=bodies or None)
    
    def stmt(self, body):
        return Statement(body=body)
    
    def simple_stmt(self, stmt):
        return stmt
    
    def compound_stmt(self, stmt):
        return stmt

    def outside_stmt(self, stmt):
        return stmt
    
    # Simple STMT
    def return_stmt(self, value):
        return Kembalikan(value=value)

    def throw_stmt(self, value):
        return Kesalahan(value=value)

    def throw_stmt_nosemi(self, value):
        return Kesalahan(value=value)

    def break_stmt(self):
        return Berhentikan()
    
    def continue_stmt(self):
        return Lanjutkan()
    
    # VARIABLES
    def const_private(self, attrs, type, expr):
        return Const(
            name=attrs[0],
            type=type,
            expr=expr,
            is_def=attrs[1],
        )
    
    def const_public(self, attrs, type, expr):
        return Const(
            name=attrs[0],
            type=type,
            expr=expr,
            is_priv=False,
            is_def=attrs[1],
        )
    
    
    def var_decl(self, attrs, type, expr = EMPTY):
        return Variable(
            name=attrs[0],
            type=type,
            expr=expr,
            is_def=attrs[1],
        )
    
    def final_decl(self, attrs, type, expr):
        return Final(
            name=attrs[0],
            type=type,
            expr=expr,
            is_def=attrs[1],
        )
    
    def set_var_pointer(self, name):
        return (name, True)
    
    def default_var_assignment(self, name):
        return (name, False)
    
    def assignment(self, target, expr):
        return Assignment(
            target=target,
            expr=expr
        )
    
    def public_struct(self, field):
        field.is_priv = False
        return field
    
    def struct_attrs(self, *args):
        name = args[0]
        body = next(a for a in args if isinstance(a, BlockStruct))
        params = next((a for a in args if _is_params(a)), [])
        extend = next(
            (a for a in args if isinstance(a, Dynamic)),
            next((a for a in args if isinstance(a, Name) and a.id != name.id), None)
        )
        return Structure(name=name, body=body, extend=extend, params=params)
    def struct_extend(self, *args):
        name = args[0]
        generic_args = next((a for a in args[1:] if isinstance(a, _TypeArgList)), None)
        if generic_args:
            return Dynamic(name=name, args=list(generic_args))
        return name

    def block_struct(self, *attrs):
        return BlockStruct(
            bodies=list(attrs)
        )
    
    def attr_field(self, name, type):
        return StructField(
            name=name,
            type=type,
        )

    def public_field(self, field):
        field.is_priv = False
        return field

    def private_field(self, field):
        field.is_priv = True
        return field
    
    def impl_plain(self, *args):
        body = next(a for a in args if isinstance(a, ImplBlock))
        names = [a for a in args if isinstance(a, Name)]
        params = next((a for a in args if _is_params(a)), [])
        type_args = next((a for a in args if _is_type_args(a)), [])
        return Implementation(
            name=names[0],
            body=body,
            params=params,
            type_args=type_args,
        )
    
    def impl_trait(self, *args):
        body = next(a for a in args if isinstance(a, ImplBlock))
        names = [a for a in args if isinstance(a, Name)]
        params = next((a for a in args if _is_params(a)), [])
        all_type_lists = [a for a in args if _is_type_args(a)]
        trait_type_args = all_type_lists[-1] if len(all_type_lists) > 1 else []
        self_type_args = all_type_lists[0] if all_type_lists else []
        return Implementation(
            name=names[-1],
            body=body,
            trait=names[0] if len(names) > 1 else names[-1],
            params=params,
            type_args=self_type_args,
        )
    
    def block_impl(self, *bodies):
        return ImplBlock(bodies=list(bodies))
    
    def body_impl(self, stmt):
        return stmt
    
    def private_method(self, method):
        method.is_priv = True
        return method
    
    def public_method(self, method):
        method.is_priv = False
        return method
    
    def static_method(self, method):
        method.static = True
        return method
    
    def method_attrs(self, name, attrs, body):
        return Method(
            name=name,
            attrs=attrs,
            body=body,
        )
    
    
    
    def enum_stmt(self, attrs): return Enum(**attrs)
    def private_enum(self, attrs):
        return {
            'is_priv': True,
            **attrs
        }
    
    def public_enum(self, attrs):
        return {
            'is_priv': False,
            **attrs
        }
    
    def enum_attrs(self, *args):
        name = args[0]
        attrs = next(a for a in args if isinstance(a, dict))
        params = next((a for a in args if _is_params(a)), [])
        return {
            'name': name,
            'params': params,
            **attrs
        }
    
    def enum_block(self, *fields):
        return {
            'fields': list(fields)
        }
    
    def public_field_attr(self, field):
        field.is_priv = False
        return field
    
    def unit_variant(self, name): return TupleVariant(name=name, args=[])
    def tuple_variant(self, name, *args):
        return TupleVariant(
            name=name,
            args=list(args),
        )
    
    def structure_variant(self, name, *attrs):
        return StructVariant(
            name=name,
            fields=list(attrs)
        )
    
    def discriminant(self, name, value):
        return Discriminant(name=name, value=value)
    
    def private_trait(self, field):
        field.is_priv = True
        return field
    
    def public_trait(self, field):
        field.is_priv = False
        return field
    
    def trait_attrs(self, name, *args):
        params = next((a for a in args if _is_params(a)), [])
        methods = [a for a in args if not _is_params(a)]
        return Trait(
            name=name,
            data=list(methods),
            params=params
        )
    def abstract_plain_method(self, name, attrs):
        return AbstractMethod(
            name=name,
            attrs=attrs
        )
    def abstract_static_method(self, name, attrs):
        return AbstractMethod(
            name=name,
            attrs=attrs,
            static=True,
        )
    
    def private_func(self, name, attrs, body):
        return Function(
            name=name,
            attrs=attrs,
            body=body
        )
    
    def public_func(self, name, attrs, body):
        return Function(
            name=name,
            attrs=attrs,
            body=body,
            is_priv=False
        )
    
    
    def attrs_func(self, generic, args, type = None):
        if isinstance(generic, Arguments) and type is None:
            generic, args, type = [], generic, args
            
        return AttrsFunc(
            generic=generic,
            args=args,
            type=type
        )
    
    def args(self, *args):
        return Arguments(
            args=args or None
        )
    
    def arg(self, arg):
        return arg

    def mut_arg(self, name, type):
        return Arg(
            name=name,
            type=type,
        )
    
    def mut_arg_deferensial(self, name, type):
        return Arg(
            name=name,
            type=type,
            is_def=True
        )

    def immut_arg(self, field):
        field.constant = True
        return field
    
    
    def ctrl_flow(self, stmt):
        return stmt

    def if_flow(self, if_stmt, *stmts):
        current = if_stmt
        for stmt in stmts:
            current.orelse = stmt
            if isinstance(stmt, If):
                current = stmt
        return if_stmt

    def if_stmt(self, expr, body):
        return If(test=expr, body=body)

    def elif_stmt(self, expr, body):
        return If(test=expr, body=body)

    def else_stmt(self, body):
        return body

    def for_flow(self, for_stmt, else_stmt=None):
        for_stmt.orelse = else_stmt
        return for_stmt

    def for_stmt(self, for_expr, body):
        return For(
            target=for_expr['target'],
            iter=for_expr['iter'],
            body=body,
        )

    def for_expr(self, target, expr):
        return {
            'target': target,
            'iter': expr,
        }

    def for_var_decl(self, *parts):
        contains = parts[-1]
        return [Arg(name=name, type=Type(type=object), constant=False) for name in contains]

    def for_final_decl(self, *parts):
        contains = parts[-1]
        return [Arg(name=name, type=Type(type=object), constant=True) for name in contains]

    def for_containns(self, name, *names):
        return [name, *names]

    def while_flow(self, while_stmt, else_stmt=None):
        while_stmt.orelse = else_stmt
        return while_stmt

    def while_stmt(self, expr, body):
        return While(
            test=expr,
            body=body,
        )

    def try_flow(self, try_stmt, *stmts):
        for stmt in stmts:
            if isinstance(stmt, ExceptionHandler):
                try_stmt.handler.append(stmt)
            elif isinstance(stmt, tuple) and stmt[0] == 'finally':
                try_stmt.finalbody = stmt[1]
            else:
                try_stmt.orelse = stmt
        return try_stmt

    def try_stmt(self, body):
        return Try(body=body)

    def catch_stmt(self, alias, body):
        return ExceptionHandler(alias=alias, body=body)

    def finally_stmt(self, body):
        return ('finally', body)

    def switch_flow(self, stmt):
        return stmt

    def switch_stmt(self, subject, *cases):
        return Switch(subject=subject, cases=list(cases))

    def case_stmt(self, pattern, *stmts):
        return Case(pattern=pattern, body=Block(bodies=list(stmts)))

    def case_pattern(self, pattern):
        return pattern

    def default_case(self):
        return None

    def or_pattern(self, pattern, *patterns):
        if not patterns:
            return pattern
        return MatchOr(patterns=[pattern, *patterns])

    def as_pattern(self, pattern, name=None):
        if not name:
            return pattern
        return MatchAs(pattern=pattern, name=name)

    def closed_pattern(self, pattern):
        return pattern

    def match_value(self, pattern):
        return MatchValue(value=pattern)

    def match_singleton_true(self, *args):
        return MatchSingleton(value=True)

    def match_singleton_false(self, *args):
        return MatchSingleton(value=False)

    def match_singleton_none(self, *args):
        return MatchSingleton(value=None)

    def match_sequence(self, patterns):
        return MatchSequence(patterns=patterns)

    def match_mapping(self, *items):
        keys = []
        patterns = []
        for item in items:
            if isinstance(item, tuple):
                keys.append(item[0])
                patterns.append(item[1])
            elif isinstance(item, MatchDots):
                keys.append(Constant(value='...'))
                patterns.append(item)
        return MatchMapping(keys=keys, patterns=patterns)

    def mapping_item(self, key, value):
        return (key, value)

    def match_struct(self, cls, *items):
        keys = []
        patterns = []
        for item in items:
            if isinstance(item, tuple):
                keys.append(item[0])
                patterns.append(item[1])
            elif isinstance(item, MatchDots):
                keys.append(Constant(value='...'))
                patterns.append(item)

        return MatchStruct(
            cls=cls,
            keys=keys,
            patterns=patterns,
        )
    
    def pattern_keyword(self, name, pattern):
        return (Constant(value=name.id), pattern)

    def match_as_capture(self, name):
        return MatchCapture(name=name)

    def match_dots(self, name):
        return MatchDots(name=name)

    def pattern_list(self, pattern, *patterns):
        return [pattern, *patterns]

    def dotted_name(self, name, *attrs):
        expr = name
        for attr in attrs:
            expr = Attribute(value=expr, attr=attr.id)
        return expr
    
    
    
    def import_stmt(self, _from, *_imports):
        return FromImport(_from=str(_from), _imports=_imports)
    
    def import_attr(self, attrs): return ImportAttr(**attrs)
    def private_import(self, attrs):
        return {
            'is_priv': True,
            **attrs
        }
    
    def public_import(self, attrs):
        return {
            'is_priv': False,
            **attrs
        }
    
    def var_import(self, attrs):
        return {
            'is_const': False,
            **attrs
        }
    
    def const_import(self, attrs):
        return {
            'is_const': True,
            **attrs
        }
    
    def static_import(self, attrs):
        return {
            'static': True,
            **attrs
        }
    
    def import_as(self, name, alias = None):
        return {
            'name': name,
            'alias': alias
        }
    
    def all_import_attrs(self, *_):
        return ImportAttr(
            name=Name(id='*'),
            static=True,
            is_const=False,
            is_priv=False,
            alias=None,
        )
    
    
    
    def expr(self, value):
        return Expression(
            value=value
        )
    
    def expr_(self, value):
        return value
    
    def not_(self, *exprs):
        if exprs[0] == 'bukan':
            return UnaryOp(
                op='not',
                operand=exprs[1]
            )
        return exprs[0]
    
    def __bool_op__(self, name, *exprs):
        if len(exprs) < 2:
            return exprs[0]
        
        return BoolOp(
            op=name,
            values=exprs
        )

    def __comp_op__(self, op, *exprs):
        if len(exprs) < 2:
            return exprs[0]
        
        ops = [op]
        left = exprs[0]
        comparators = [exprs[1]]
        if isinstance(exprs[1], Compare):
            right = exprs[1]
            ops.extend(right.ops)
            comparators = [right.left, *right.comparators]
        
        return Compare(
            left=left,
            ops=ops,
            comparators=comparators
        )

    def __bin_op__(self, op, *exprs):
        if len(exprs) < 2:
            return exprs[0]
        
        return BinOp(
            left=exprs[0],
            op=op,
            right=exprs[1]
        )
    
    def or_(self, *exprs): return self.__bool_op__('or', *exprs)
    def and_(self, *exprs): return self.__bool_op__('and', *exprs)
    
    def in_(self, *exprs): return self.__comp_op__('in', *exprs)
    def notin_(self, *exprs): return self.__comp_op__('not in', *exprs)
    def is_(self, *exprs): return self.__comp_op__('is', *exprs)
    def isnot_(self, *exprs): return self.__comp_op__('is not', *exprs)
    
    def eq_(self, *exprs): return self.__comp_op__('==', *exprs)
    def neq_(self, *exprs): return self.__comp_op__('!=', *exprs)
    def gt_(self, *exprs): return self.__comp_op__('>', *exprs)
    def ge_(self, *exprs): return self.__comp_op__('>=', *exprs)
    def lt_(self, *exprs): return self.__comp_op__('<', *exprs)
    def le_(self, *exprs): return self.__comp_op__('<=', *exprs)
    
    def add_(self, *exprs): return self.__bin_op__('+', *exprs)
    def min_(self, *exprs): return self.__bin_op__('-', *exprs)
    def mul_(self, *exprs): return self.__bin_op__('*', *exprs)
    def div_(self, *exprs): return self.__bin_op__('/', *exprs)
    def pow_(self, *exprs): return self.__bin_op__('**', *exprs)
    
    def term(self, expr):
        return expr

    def name_key(self, name):
        return name
    
    def subscripts(self, subscript):
        return subscript
    
    def attr(self, expr, attr):
        return Attribute(
            value=expr,
            attr=str(attr.id)
        )
    
    def idx(self, expr, key):
        return Index(
            value=expr,
            key=key
        )
    
    def call(self, func, args):
        return Call(
            func=func,
            args=args or None
        )
    
    def call_generic(self, func, generic, args):
        return Call(
            func=func,
            args=args,
            generic=generic
        )
    
    def call_params(self, *args):
        return list(args)
    
    def struct_field(self, *args):
        struct = args[0]
        kwargs = next(a for a in args if isinstance(a, Kamus))
        type_args = []
        if isinstance(struct, CallDynamic):
            type_args = struct.type_args
            struct = struct.name
        return StructFielded(
            struct=struct,
            kwargs=kwargs,
            type_args=type_args
        )
    
    def call_dynamic(self, name, type_args):
        return CallDynamic(name=name, type_args=type_args)
    
    def type_args(self, *args):
        return _TypeArgList(args)
    
    def get_identifier(self, value):
        return value

    def identifier_name(self, name):
        return name

    def info_expr(self, name):
        return Info(name=name)

    def pointer_expr(self, value):
        return value

    def referensial(self, name):
        return Referensial(name=name if isinstance(name, Name) else Name(id=str(name)))

    def deferensial(self, name):
        return Deferensial(name=name if isinstance(name, Name) else Name(id=str(name)))

    def salin_referensial(self, name):
        return SalinReferensial(name=name if isinstance(name, Name) else Name(id=str(name)))
    
    def literal(self, lit):
        return lit
    
    def constants(self, const):
        return Constant(
            value=const
        )
    def object(self, obj):
        return obj
    def TEKS(self, s): return str(s)[1:-1].encode().decode('unicode_escape')
    def ANGKA(self, i): return int(i)
    def FLOAT(self, f): return float(f)
    def BOOLEAN(self, b): return str(b) == 'benar'
    def KOSONG(self, n): return None
    def daftar(self, *args): return Daftar(elts=args)
    def kamus(self, kwargs=None):
        if kwargs is None:
            return Kamus(keys=[], values=[])
        return Kamus(**kwargs)
    def dbodies(self, *dicts):
        keys = []
        values = []
        for d in dicts:
            keys.append(d['key'])
            values.append(d['value'])
        
        return {
            'keys': keys,
            'values': values
        }
    def dbody(self, key, value=None):
        if value is None:
            return {
                'key': Constant(value=key.id),
                'value': key
            }
        return {
            'key': key,
            'value': value
        }
    def dkey(self, *key):
        if len(key) == 1:
            if isinstance(key[0], Name):
                return Constant(value=key[0].id)
            return key[0]
        return key[0]

    def expr_func(self, attrs, body):
        return ExprFunc(
            attrs=attrs,
            body=body
        )
    
    def type_ann(self, *types):
        if len(types) == 2 and types[0] is _OPTIONAL_SENTINEL:
            return Type(
                option=True,
                type=types[1]
            )
        return Type(
            type=types[0]
        )
    def optional(self, *args):
        return _OPTIONAL_SENTINEL
    
    
    def typedef_stmt(self, attrs):
        return TypeDef(**attrs)
    
    def private_typedef(self, attrs):
        return {
            'is_priv': True,
            **attrs
        }
    
    def public_typedef(self, attrs):
        return {
            'is_priv': False,
            **attrs
        }
    
    def typedef_attrs(self, alias, *attrs):
        value = attrs[-1]
        args = attrs[0] if len(attrs) == 2 else []
        
        return {
            'alias': alias,
            'args': args,
            'value': value
        }
    def typedef_params(self, *params):
        return _ParamList(params)
    
    def generic_params(self, *args):
        return _TypeArgList(args)
    
    def generic_param_name(self, name):
        return GenericParam(name=name)
    
    def generic_param_bound(self, name, bound):
        return GenericParam(name=name, bound=bound)
    
    def generic_param_default(self, name, default):
        return GenericParam(name=name, default=default)
    
    def generic_param_full(self, name, bound, default):
        return GenericParam(name=name, bound=bound, default=default)
    
    
    def interface_stmt(self, attrs):
        return InterFace(**attrs)
    
    def private_interface(self, attrs):
        return {
            'is_priv': True,
            **attrs
        }
    
    def public_interface(self, attrs):
        return {
            'is_priv': False,
            **attrs
        }
    
    def interface_attrs(self, alias, args):
        return {
            'alias': alias,
            'args': args,
        }
    
    def interface_object(self, *args):
        keys = []
        values = []
        for k, v in list(args):
            keys.append(k)
            values.append(v)
        
        return InterFaceBody(
            keys=keys,
            values=values
        )
    
    def interface_body_object(self, key, value):
        return (key, value)
    
    
    def type_def(self, type):
        return type
    def type_object(self, type):
        return type
    def type_result(self, ok, err = None):
        if not err:
            err = Type(type=Exception, option=True)
            
        return KEMBALIKAN(oke_type=ok, error_type=err)
    def type_func(self, *types):
        annotation = types[-1]
        args = types[:-1]
        return FUNGSI(
            args=args,
            annotation=annotation
        )
    def type_arr(self, body):
        return DAFTAR(
            body=body
        )
    def type_dict(self, key, value):
        return KAMUS(
            key=key,
            value=value
        )
    def type_union(self, *bodies):
        return SERIKAT(
            bodies=bodies
        )
    def type_union_plus(self, *args):
        bodies = []
        for a in args:
            inner = a.type if isinstance(a, Type) else a
            if isinstance(inner, SERIKAT):
                bodies.extend(inner.bodies)
            else:
                bodies.append(a)
        return SERIKAT(bodies=bodies)
    def type_literal(self, *bodies):
        return LITERAL(
            bodies=bodies
        )
    
    def type_dynamic(self, name, *args):
        return Dynamic(name=name, args=list(args))
    
    def NAME(self, id):
        return Name(id=str(id))

class Parse:
    def __new__(cls, tree, file: str = "<unknown>", source: str | None = None):
        return _Parse(file, source).transform(tree)
    @classmethod
    def __repr__(cls):
        return 'parse.Parse'
