"""Lark transformer that converts grammar parse trees into IDScript AST nodes."""

from lark import Transformer, v_args
from ..ids_ast import *
from ..runtime.types import EMPTY

@v_args(inline=True)
class _Parse(Transformer):
    def __init__(self):
        pass
    
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
    
    def break_stmt(self):
        return Berhentikan()
    
    def continue_stmt(self):
        return Lanjutkan()
    
    # VARIABLES
    def const_decl(self, field): return field
    def const_private(self, name, type, expr):
        return Const(
            name=name,
            type=type,
            expr=expr
        )
    
    def const_public(self, name, type, expr):
        return Const(
            name=name,
            type=type,
            expr=expr,
            is_priv=False
        )
    
    
    def var_decl(self, name, type, expr = EMPTY):
        return Variable(
            name=name,
            type=type,
            expr=expr
        )
    
    def final_decl(self, name, type, expr):
        return Final(
            name=name,
            type=type,
            expr=expr
        )
    
    def assignment(self, target, expr):
        return Assignment(
            target=target,
            expr=expr
        )
    
    def struct_decl(self, field): return field
    def private_struct(self, field): return field
    def public_struct(self, field):
        field.is_priv = False
        return field
    
    def struct_attrs(self, name, body, extend=None):
        return Structure(name=name, body=body, extend=extend)
    def struct_extend(self, name): return name
    def block_struct(self, *attrs):
        return BlockStruct(
            bodies=list(attrs)
        )
    
    def struct_fields(self, field): return field
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
    
    def impl_stmt(self, field): return field

    def impl_plain(self, name, body):
        return Implementation(
            name=name,
            body=body
        )
    
    def impl_trait(self, trait, name, body):
        return Implementation(
            name=name,
            body=body,
            trait=trait
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
    
    def enum_attrs(self, name, attrs):
        return {
            'name': name,
            **attrs
        }
    
    def enum_block(self, *fields):
        return {
            'fields': list(fields)
        }
    
    def enum_body(self, field): return field
    def private_field_attr(self, field): return field
    def public_field_attr(self, field):
        field.is_priv = False
        return field
    
    def field_attr(self, field): return field
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
    
    def trait_stmt(self, field): return field
    def private_trait(self, field):
        field.is_priv = True
        return field
    
    def public_trait(self, field):
        field.is_priv = False
        return field
    
    def trait_attrs(self, name, *data):
        return Trait(
            name=name,
            data=list(data)
        )
    def abstract_method(self, name, attrs):
        return AbstractMethod(
            name=name,
            attrs=attrs
        )
    
    def func_decl(self, field): return field
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
    
    
    def attrs_func(self, args, type):
        return AttrsFunc(
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

    def immut_arg(self, name, type):
        return Arg(
            name=name,
            type=type,
            constant=True
        )
    
    
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

    def pattern(self, pattern): return pattern

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
    
    def import_decl(self, attrs): return attrs
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
    def ge_(self, *exprs): return self.__comp_op__('>', *exprs)
    def gt_(self, *exprs): return self.__comp_op__('>=', *exprs)
    def le_(self, *exprs): return self.__comp_op__('<', *exprs)
    def lt_(self, *exprs): return self.__comp_op__('<=', *exprs)
    
    def add_(self, *exprs): return self.__bin_op__('+', *exprs)
    def min_(self, *exprs): return self.__bin_op__('-', *exprs)
    def mul_(self, *exprs): return self.__bin_op__('*', *exprs)
    def div_(self, *exprs): return self.__bin_op__('/', *exprs)
    def pow_(self, *exprs): return self.__bin_op__('**', *exprs)
    
    def term(self, expr):
        return expr
    
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
    
    def call(self, func, *args):
        return Call(
            func=func,
            args=args or None
        )
    
    def struct_field(self, struct, kwargs):
        return StructFielded(
            struct=struct,
            kwargs=kwargs
        )
    
    def get_identifier(self, value):
        return value

    def identifier_name(self, name):
        return name

    def info_expr(self, name):
        return Info(name=name)
    
    def literal(self, lit):
        return lit
    
    def constants(self, const):
        return Constant(
            value=const
        )
    def object(self, obj):
        return obj
    def TEKS(self, s): return str(s)[1:-1]
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
        
    def dval(self, val): return val
    def type_ann(self, *types):
        if len(types) == 2 and types[0] is True:
            return Type(
                option=True,
                type=types[1]
            )
        return Type(
            type=types[0]
        )
    def optional(self, *args):
        return True
    
    
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
    def typedef_params(self, *names):
        return list(names)
    
    
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
    def type_literal(self, *bodies):
        return LITERAL(
            bodies=bodies
        )
    
    def type_dynamic(self, name, *args):
        return Dynamic(name=name, args=list(args))
    
    def NAME(self, id):
        return Name(id=str(id))

class Parse:
    def __new__(cls, tree):
        return _Parse().transform(tree)
    @classmethod
    def __repr__(cls):
        return 'parse.Parse'
