from __future__ import annotations

"""AST dataclasses used by the IDScript parser and compiler."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Type as T

class _PROGRAM:
    pass

@dataclass
class Program(_PROGRAM):
    bodies: Optional[List['_STATEMENT']] = None



class _STATEMENT(_PROGRAM):
    pass

class _IDENTIFIER(_STATEMENT):
    pass

@dataclass
class Name(_IDENTIFIER):
    id: str

@dataclass
class Info(_IDENTIFIER):
    name: Name

@dataclass
class Top(_STATEMENT):
    body: _STATEMENT

@dataclass
class Block(_STATEMENT):
    bodies: List[_STATEMENT]

@dataclass
class Statement(_STATEMENT):
    body: Optional[_STATEMENT] = None


class _SIMPLE(_STATEMENT):
    pass

@dataclass
class Kembalikan(_SIMPLE):
    value: 'Expression'

@dataclass
class Kesalahan(_SIMPLE):
    value: 'Expression'

@dataclass
class Berhentikan(_SIMPLE):
    pass

@dataclass
class Lanjutkan(_SIMPLE):
    pass



class _VARIABLE(_STATEMENT):
    pass


@dataclass
class Const(_VARIABLE):
    name: Name
    type: 'Type'
    expr: 'Expression' | Any
    is_priv: bool = True

@dataclass
class Variable(_VARIABLE):
    name: Name
    type: 'Type'
    expr: Optional['Expression'] = None

@dataclass
class Final(_VARIABLE):
    name: Name
    type: 'Type'
    expr: 'Expression'

@dataclass
class Assignment(_VARIABLE):
    target: 'Expression'
    expr: 'Expression'



class _FUNCTION(_STATEMENT):
    pass

@dataclass
class Function(_FUNCTION):
    name: Name
    attrs: 'AttrsFunc'
    body: Block
    is_priv: bool = True

@dataclass
class AttrsFunc(_FUNCTION):
    args: 'Arguments'
    type: 'Type'

@dataclass
class Arguments(_FUNCTION):
    args: Optional[List['Arg']] = None

@dataclass
class Arg(_FUNCTION):
    name: Name
    type: 'Type'
    constant: bool = True



class _STRUCTURE(_STATEMENT):
    pass

@dataclass
class Structure(_STRUCTURE):
    name: Name
    body: Optional[BlockStruct] = None
    is_priv: bool = True
    extend: Optional[Name] = None

@dataclass
class BlockStruct(_STRUCTURE):
    bodies: List['StructField'] = field(default_factory=list)

@dataclass
class StructField(_STRUCTURE):
    name: Name
    type: 'Type'
    is_priv: bool = True



class _IMPLEMENTATION(_STRUCTURE):
    pass

@dataclass
class Implementation(_IMPLEMENTATION):
    name: Name
    body: 'ImplBlock'
    trait: Optional[Name] = None

@dataclass
class ImplBlock(_IMPLEMENTATION):
    bodies: List['Method']

@dataclass
class Method(_IMPLEMENTATION):
    name: Name
    attrs: AttrsFunc
    body: Block
    is_priv: bool = True
    static: bool = False



class _ENUM(_STRUCTURE):
    pass

@dataclass
class Enum(_ENUM):
    name: Name
    fields: List['_ENUM_ATTR']
    is_priv: bool = True



class _ENUM_ATTR(_ENUM):
    pass

@dataclass
class TupleVariant(_ENUM_ATTR):
    name: Name
    args: List[T]
    is_priv: bool = True


@dataclass
class StructVariant(_ENUM_ATTR):
    name: Name
    fields: List[StructField]
    is_priv: bool = True


@dataclass
class Discriminant(_ENUM_ATTR):
    name: Name
    value: '_EXPRESSION'
    is_priv: bool = True


@dataclass
class Trait(_STRUCTURE):
    name: Name
    data: List['_ABSTRACT_METHOD']
    is_priv: bool = True


class _ABSTRACT_METHOD(_STRUCTURE):
    pass

@dataclass
class AbstractMethod(_ABSTRACT_METHOD):
    name: Name
    attrs: AttrsFunc


class _CTRL_FLOW(_STATEMENT):
    pass


@dataclass
class If(_CTRL_FLOW):
    test: '_EXPRESSION'
    body: Block
    orelse: Optional['_STATEMENT'] = None

@dataclass
class For(_CTRL_FLOW):
    target: List[Arg]
    iter: '_EXPRESSION'
    body: Block
    orelse: Optional[Block] = None

@dataclass
class While(_CTRL_FLOW):
    test: '_EXPRESSION'
    body: Block
    orelse: Optional[Block] = None

@dataclass
class ExceptionHandler:
    alias: Name
    body: Block

@dataclass
class Try(_CTRL_FLOW):
    body: Block
    handler: List[ExceptionHandler] = field(default_factory=list)
    orelse: Optional[Block] = None
    finalbody: Optional[Block] = None

@dataclass
class Switch(_CTRL_FLOW):
    subject: '_EXPRESSION'
    cases: List['Case']

@dataclass
class Case(_CTRL_FLOW):
    pattern: Optional['_MATCH_EXPR']
    body: Block

class _MATCH_EXPR:
    pass


@dataclass
class MatchValue(_MATCH_EXPR):
    value: '_EXPRESSION'

@dataclass
class MatchAs(_MATCH_EXPR):
    pattern: _MATCH_EXPR
    name: Name

@dataclass
class MatchCapture(_MATCH_EXPR):
    name: Name

@dataclass
class MatchDots(_MATCH_EXPR):
    name: Name

@dataclass
class MatchOr(_MATCH_EXPR):
    patterns: List[_MATCH_EXPR]

@dataclass
class MatchSequence(_MATCH_EXPR):
    patterns: List[_MATCH_EXPR]

@dataclass
class MatchMapping(_MATCH_EXPR):
    keys: List['_EXPRESSION']
    patterns: List[_MATCH_EXPR]

@dataclass
class MatchStruct(_MATCH_EXPR):
    cls: '_EXPRESSION'
    keys: List['_EXPRESSION']
    patterns: List[_MATCH_EXPR]

@dataclass
class MatchSingleton(_MATCH_EXPR):
    value: bool | None

class _MODULE(_STATEMENT):
    pass


@dataclass
class FromImport(_MODULE):
    _from: str
    _imports: List['ImportAttr']

@dataclass
class ImportAttr(_MODULE):
    name: Name
    is_priv: bool = True
    is_const: bool = False
    static: bool = False
    alias: Optional[Name] = None




class _EXPRESSION(_STATEMENT):
    pass

@dataclass
class Expression(_EXPRESSION):
    value: _EXPRESSION



@dataclass
class UnaryOp(_EXPRESSION):
    op: str
    operand: _EXPRESSION

@dataclass
class BoolOp(_EXPRESSION):
    op: str
    values: List[_EXPRESSION]

@dataclass
class Compare(_EXPRESSION):
    left: _EXPRESSION
    ops: List[str]
    comparators: List[_EXPRESSION]

@dataclass
class BinOp(_EXPRESSION):
    left: _EXPRESSION
    op: str
    right: _EXPRESSION


@dataclass
class Attribute(_EXPRESSION):
    value: _EXPRESSION
    attr: str

@dataclass
class Index(_EXPRESSION):
    value: _EXPRESSION
    key: _EXPRESSION

@dataclass
class Call(_EXPRESSION):
    func: _EXPRESSION
    args: Optional[List[_EXPRESSION]] = None

@dataclass
class StructFielded(_EXPRESSION):
    struct: Structure | Name
    kwargs: Kamus


class _LITERAL(_EXPRESSION):
    pass

class _OBJECT(_LITERAL):
    pass

@dataclass
class Constant(_LITERAL):
    value: Any

@dataclass
class Daftar(_OBJECT):
    elts: List[_EXPRESSION]

@dataclass
class Kamus(_OBJECT):
    keys: List[_EXPRESSION]
    values: List[_EXPRESSION]



class _TYPE(_STATEMENT):
    pass

class _TYPEDEF(_TYPE):
    pass


@dataclass
class Type(_TYPE):
    type: Name | _TYPEDEF | T
    option: bool = False


@dataclass
class TypeDef(_TYPEDEF):
    alias: Name
    args: List[Name]
    value: _TYPEDEF
    is_priv: bool = True
    

@dataclass
class InterFace(_TYPEDEF):
    alias: Name
    args: List[InterFaceBody]
    is_priv: bool = True

@dataclass
class InterFaceBody(_TYPEDEF):
    keys: List[_EXPRESSION]
    values: List[_TYPEDEF]


@dataclass
class KEMBALIKAN(_TYPEDEF):
    oke_type: Type
    error_type: Optional[Type] = None

@dataclass
class FUNGSI(_TYPEDEF):
    annotation: Type
    args: Optional[List[Type]] = None

@dataclass
class DAFTAR(_TYPEDEF):
    body: Type

@dataclass
class KAMUS(_TYPEDEF):
    key: Type
    value: Type

@dataclass
class SERIKAT(_TYPEDEF):
    bodies: List[Type]

@dataclass
class LITERAL(_TYPEDEF):
    bodies: List[_LITERAL]

@dataclass
class Dynamic(_TYPEDEF):
    name: Name
    args: List[Name]
