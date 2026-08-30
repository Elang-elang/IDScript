from dataclasses import dataclass, field
from typing import (
    List, Dict,
    Any, Literal as Lit,
    Type, Union
)

class Module:
    pass

@dataclass
class Program(Module):
    stmts: List['Statement'] = field(default_factory=list)

class TopStatement(Module):
    pass


class Statement(Module):
    pass

@dataclass
class ModuleLanguage(Module):
    name_language: str
    module_path: str

@dataclass
class BlockStatement(Statement):
    stmts: List['Statement'] = field(default_factory=list)

class SimpleStatement(Statement):
    pass


@dataclass
class PublicStatement(TopStatement):
    name: 'Name'

@dataclass
class ConstantaDeclare(TopStatement):
    name: 'Name'
    type: 'TypeAnnotation'
    expr: 'Expression'
    private: bool = True

@dataclass
class TypeDeclare(TopStatement):
    name: 'Name'
    expr: 'Expression'
    private: bool = True

@dataclass
class FunctionDeclare(TopStatement):
    name: 'Name'
    params: 'Parameter'
    type: 'TypeAnnotation'
    body: List[Statement] = field(default_factory=list)
    private: bool = True
    static:  bool = False

@dataclass
class StructureDeclare(TopStatement):
    name: 'Name'
    fields: List['Field']
    extended: Union['Name', None] = None
    private: bool = True

@dataclass
class Implementation(TopStatement):
    name: 'Name'
    funcs: List[FunctionDeclare]

@dataclass
class FromImport(TopStatement):
    path: 'String'
    mark: 'String'
    fields: List['Name']
    aliases: List[Union['Name', None]] = field(default_factory=list)

@dataclass
class Import(TopStatement):
    paths: List['String']
    marks: List[Union['String', None]]
    aliases: List[Union['Name', None]] = field(default_factory=list)


@dataclass
class VariableDeclare(SimpleStatement):
    name: 'Name'
    type: 'TypeAnnotation'
    expr: 'Expression'

@dataclass
class Assigment(SimpleStatement):
    script: Union['SubScript', 'Name']
    value: 'Expression'

@dataclass
class ReadIn(SimpleStatement):
    name: 'Name'

@dataclass
class WriteOut(SimpleStatement):
    value: 'Expression'

@dataclass
class ReturnStatement(SimpleStatement):
    value: 'Expression'

@dataclass
class ContinueStatement(SimpleStatement):
    pass

@dataclass
class BreakStatement(SimpleStatement):
    pass


class Expression(SimpleStatement):
    pass


@dataclass
class UnaryOp(Expression):
    op: str
    operand: Expression

@dataclass
class BoolOp(Expression):
    op: str
    values: List[Expression]

@dataclass
class Compare(Expression):
    left: Expression
    ops: List[str]
    comparators: List[Expression]

@dataclass
class BinOp(Expression):
    left: Expression
    op: str
    right: Expression


@dataclass
class FunctionExpression(Expression):
    params: 'Parameter'
    type: 'TypeAnnotation'
    body: List[Statement] = field(default_factory=list)


class SubScript(Expression):
    pass

@dataclass
class Attribute(SubScript):
    value: Expression
    attr: str

@dataclass
class Index(SubScript):
    value: Expression
    key: Exception

@dataclass
class CallFunction(SubScript):
    func: Expression
    args: List[Expression] = field(default_factory=list)

@dataclass
class CallStructure(SubScript):
    struct: Expression
    kwargs: Dict[str, Expression] = field(default_factory=dict)


class Literal(Expression):
    pass

@dataclass
class String(Literal):
    strings: str

@dataclass
class Integer(Literal):
    numbers: int

@dataclass
class Float(Literal):
    numbers: int | float

@dataclass
class Boolean(Literal):
    cond: Lit[0, 1]


@dataclass
class TypeAnnotation(SimpleStatement):
    name: 'Name'

@dataclass
class TypeFunction(SimpleStatement):
    params: List[Any | Type | TypeAnnotation]
    type: Any | Type | TypeAnnotation


@dataclass
class Name(SimpleStatement):
    id: str

@dataclass
class Parameter(SimpleStatement):
    params: List['Field'] = field(default_factory=list)

@dataclass
class Field(SimpleStatement):
    name: Name
    type: TypeAnnotation
    private: bool | None = None
    constant: bool | None = None