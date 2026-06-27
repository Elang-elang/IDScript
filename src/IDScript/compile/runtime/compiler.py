"""AST visitor and runtime evaluator for IDScript."""

from typing import (
    Any, List, Dict, TypedDict, Callable, Type as T,
    Union, Literal, Optional, cast, get_origin
)
import builtins
import operator
from pathlib import Path

from ..ids_ast import *
from ..diagnostics import IDSRuntimeError, annotate_exception, get_source
from .scope import GlobalScope, Scope
from .control import Throw, Return, Break, Continue
from .types import check_types, EMPTY, Result, default_value
from .config import Config
from .structure import Structure as Struct, Trait as trait
from .variable import Variable as Var


class _VMFunctionProxy:
    def __init__(self, vm: Any, module_key: str, name: str, function: Any):
        self._vm = vm
        self._module_key = module_key
        self._name = name
        self._function = function

    def __call__(self, *args: Any) -> Any:
        state = self._vm._load_module(self._module_key)
        return self._vm._call(self._function, list(args), state, {})

    def __repr__(self) -> str:
        return f'<VMFunction: {self._name}>'

class Compiler:
    def __init__(self, file, is_module=False):
        self.v = self.visit
        
        self.global_scope = GlobalScope()
        self.current_scope = self.global_scope
        self.config = Config(file, is_module)
        
        from ..builtin import ALL
        for n, t, v in ALL:
            self.global_scope.declare(n, t, v, True, True)
        
        self.global_scope.declare(
            'BERKAS',
            str,
            self.config.path() if self.config.is_module() else 'utama',
            True,
            True,
        )
        
        from ..builtin import GLOBAL, LOCAL
        
        Global = type(
            'Global',
            (object,),
            {
                '__init__': lambda _: None,
                '__call__': lambda _, *args: GLOBAL(self.global_scope, *args),
                '__repr__': lambda _: '<Function: Global>', 
            }
        )()
        Lokal = type(
            'Lokal',
            (object,),
            {
                '__init__': lambda _: None,
                '__call__': lambda _, *args: LOCAL(self.current_scope, *args),
                '__repr__': lambda _: '<Function: Lokal>', 
            }
        )()
        
        self.global_scope.declare(
            'Global',
            Callable[[...], None],
            Global,
            True,
            True,
        )
        
        self.global_scope.declare(
            'Lokal',
            Callable[[...], None],
            Lokal,
            True,
            True,
        )
    
    def visit(self, __node):
        method = builtins.getattr(
            self,
            type(__node).__name__,
            self._undefined_node,
        )
        try:
            return method(__node)
        except (Return, Throw, Break, Continue):
            raise
        except Exception as error:
            raise annotate_exception(error, get_source(__node)) from error

    def _undefined_node(self, __node):
        raise NotImplementedError(f'The node/token {type(__node).__name__!r} is undefined')
    
    def Program(self, node: Program):
        try:
            if node.bodies:
                for body in node.bodies:
                    self.v(body)
        except ImportError:
            raise
        except IDSRuntimeError:
            raise
        except Exception as e:
            raise IDSRuntimeError.from_exception(e, file=self.config.path()) from e
    
    def Top(self, node: Top):
        return self.v(node.body)
    
    def Block(self, node: Block):
        for body in node.bodies or []:
            self.v(body)
    
    def Statement(self, node: Statement):
        if node.body:
            return self.v(node.body)

    
    def Kembalikan(self, node: Kembalikan):
        if self.config.is_infunc():
            raise Return(self.v(node.value))
        raise AttributeError(
            'Return statement only inside function'
        )

    def Kesalahan(self, node: Kesalahan):
        if self.config.is_infunc():
            raise Throw(self.v(node.value))
        raise AttributeError(
            'Throw statement only inside function'
        )

    def Berhentikan(self, node: Berhentikan):
        if self.config.is_inloop():
            raise Break()
        raise AttributeError(
            'Break statement only inside loop'
        )

    def Lanjutkan(self, node: Lanjutkan):
        if self.config.is_inloop():
            raise Continue()
        raise AttributeError(
            'Continue statement only inside loop'
        )
    
    
    def Const(self, node: Const):
        name = node.name.id
        ann = self.v(node.type)
        expr = self.v(node.expr) if node.expr else None
        is_priv = node.is_priv
        if node.is_def:
            if not isinstance(expr, Var):
                raise TypeError(f'Konstanta deferensial {name!r} membutuhkan referensial')
            self.current_scope.declare(name, ann, expr, True, is_priv, True)
            return

        self.current_scope.declare(name, ann, expr, True, is_priv, False)
    
    def Variable(self, node: Variable):
        name = node.name.id
        ann = self.v(node.type)
        expr = self.v(node.expr) if node.expr is not EMPTY else EMPTY
        
        if expr is EMPTY:
            expr = default_value(ann)
        
        if node.is_def:
            if not isinstance(expr, Var):
                raise TypeError(f'Variabel deferensial {name!r} membutuhkan referensial')
            self.current_scope.declare(name, ann, expr, False, False, True)
            return

        self.current_scope.declare(name, ann, expr)
    
    def Final(self, node: Final):
        name = node.name.id
        ann = self.v(node.type)
        expr = self.v(node.expr)
        
        if node.is_def:
            if not isinstance(expr, Var):
                raise TypeError(f'Final deferensial {name!r} membutuhkan referensial')
            self.current_scope.declare(name, ann, expr, True, True, True)
            return

        self.current_scope.declare(name, ann, expr, True)
    
    def Assignment(self, node: Assignment):
        expr = self.v(node.expr)
        
        target = None
        if isinstance(node.target, Deferensial):
            pointer = self.current_scope.getThis(node.target.name.id)
            pointer.pointer_set(expr)

        elif isinstance(node.target, Attribute):
            target = self.v(node.target.value)
            attr = node.target.attr
            setattr(target, attr, expr)
        
        elif isinstance(node.target, Index):
            target = self.v(node.target.value)
            idx = self.v(node.target.key)
            target[idx] = expr
        
        elif isinstance(node.target, Name):
            target = node.target.id
            self.current_scope.set(target, expr)
        else:
            raise TypeError('Assignment target must be a name or subscripts')
    
    
    def Structure(self, node: Structure):
        name = node.name.id
        is_priv = node.is_priv
        extend = None

        if node.extend:
            extend = self.v(node.extend)
        
        self.config.enter_struct(name)
        try:
            attrs = {}
            if node.body:
                attrs.update(self.v(node.body))

            struct = Struct(
                name,
                self.config,
                attrs,
                extend,
            )
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

    
    def StructField(self, node: 'StructField'):
        name = node.name.id
        attr_type = self.v(node.type)
        is_priv = node.is_priv
        
        return {
            'name': name,
            'type': attr_type,
            'is_priv': is_priv,
        }
    
    
    def Implementation(self, node: Implementation):
        struct_name = node.name.id
        kwargs_methods = self.v(node.body)
        
        struct = self.current_scope.get(struct_name)
        self.config.enter_struct(struct_name)
        
        if node.trait:
            trait = self.v(node.trait)
            trait(kwargs_methods)
        
        try:
            for kwargs in kwargs_methods:
                builtins.getattr(struct, 'add_method')(**kwargs)
        finally:
            self.config.leave_struct()
    
    def ImplBlock(self, node: ImplBlock):
        return [self.v(b) for b in node.bodies]
    
    def Method(self, node: Method):
        name = node.name.id
        args = self.v(node.attrs.args)
        return_type = self.v(node.attrs.type)
        body = node.body.bodies or []
        struct_name = self.config.struct_name
        static = node.static
        
        def wrapper(*arguments):
            arguments = list(arguments)
            parent = self.current_scope
            self.current_scope = Scope(parent=parent)

            self.config.enter_func()
            self.config.enter_struct(struct_name)
            if static and arguments:
                arguments.pop(0)

            try:
                if args and arguments:
                    for i, arg in enumerate(args['wrapp']):
                        if i < len(arguments):
                            arg(arguments[i])
                        else:
                            raise AttributeError(f'{name}() missing required argument {arg.name!r}')
                if arguments and not args:
                    raise AttributeError(f'{name}() takes 0 arguments but {len(arguments)} was given')

                for stmt in body:
                    self.v(stmt)

                result = arguments[0] if arguments else None
                check_types(result, return_type)
                return result
            except Return as res:
                result = None
                if res.args:
                    result = res.args[0]
                
                check_types(result, return_type)
                return result
            except Throw as err:
                error = err.args[0] if err.args else IDSRuntimeError('Something was wrong')
                if not isinstance(error, BaseException):
                    error = IDSRuntimeError(error)
                raise error
            except:
                raise
            finally:
                self.current_scope = parent
                self.config.leave_struct()
                self.config.leave_func()
        
        annotations = {}
        for arg, ann in zip(args['wrapp'], args['annotations']):
            annotations[arg.__name__] = ann
        
        annotations['return'] = return_type
        
        method = type(
            name,
            (object,),
            {
                '__init__': lambda _: None,
                '__call__': lambda _, *args: wrapper(*args),
                '__repr__': lambda _: f'<Method of {struct_name}: {name}>',
                '__setattr__': lambda this, name, value: object.__setattr__(this, name, value),

                '__annotations__': annotations
            }
        )
        
        return {
            'name': name,
            'value': method(),
            'type': Callable[[...], Any],
            'is_priv': node.is_priv,
        }
    
    
    def Enum(self, node: Enum):
        from .enum import Enum
        name = node.name.id
        self.config.enter_struct(name)
        try:
            raw_fields = [self.v(f) for f in node.fields]
            fields = {}
            for field in raw_fields:
                key = field['name']
                field.pop('name')
                fields[key] = field

            enum = Enum(
                name, self.config,
                fields
            )
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
        raw_data = [self.v(data) for data in node.data]
        is_priv = node.is_priv
        
        data = {}
        for raw_d in raw_data:
            name_data = raw_d['name']
            data[name_data] = {
                key: value
                for key, value in raw_d.items()
                if key != 'name'
            }
        
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
        
        annotations = {}
        for arg, ann in zip(args['wrapp'], args['annotations']):
            annotations[arg.__name__] = ann
        
        annotations['return'] = return_type
        
        return {
            'name': node.name.id,
            'annotations': annotations,
            'type': Callable[[...], Any]
        }
    
    def Function(self, node: Function):
        name = node.name.id
        args = self.v(node.attrs.args)
        return_type = self.v(node.attrs.type)
        body = node.body.bodies or []
        is_priv = node.is_priv
        
        # perketatan fungsi utama
        if name == 'utama':
            if any(list(args.values())):
                raise AttributeError("Main Function (fungsi utama) doesn't arguments required!")
            if return_type != int and return_type != Optional[int]:
                raise AttributeError("Main Function (fungsi utama) doesn't return a integer type?")
        
        def wrapper(*arguments):
            parent = self.current_scope
            self.current_scope = Scope(parent=parent)

            self.config.enter_func()

            try:
                if args and arguments:
                    for i, arg in enumerate(args['wrapp']):
                        if i < len(arguments):
                            arg(arguments[i])
                        else:
                            raise AttributeError(f'{name}() missing required argument {arg.name!r}')
                if arguments and not args:
                    raise AttributeError(f'{name}() takes 0 arguments but {len(arguments)} was given')

                for stmt in body:
                    self.v(stmt)
            except Return as res:
                result = None
                if res.args:
                    result = res.args[0]
                
                check_types(result, return_type)
                return result
            except Throw as err:
                error = err.args[0] if err.args else IDSRuntimeError('Something was wrong')
                if not isinstance(error, BaseException):
                    error = IDSRuntimeError(error)
                raise error
            except:
                raise
            finally:
                self.current_scope = parent
                self.config.leave_func()
        
        func = type(
            name,
            (object,),
            {
                '__init__': lambda _: None,
                '__call__': lambda _, *args: wrapper(*args),
                '__repr__': lambda _: f'<Function: {name}>',
                '__setattr__': lambda this, name, value: object.__setattr__(this, name, value),

            }
        )
        self.current_scope.declare(
            name,
            Callable[..., return_type],
            func(),
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
        name = node.name.id
        arg_type = self.v(node.type)

        def wrapper(val):
            if node.is_def:
                if not isinstance(val, Var):
                    raise TypeError(f'Argumen deferensial {name!r} membutuhkan referensial')
                self.current_scope.declare(name, arg_type, val, node.constant, True, True)
                return

            self.current_scope.declare(name, arg_type, val, node.constant)
        
        wrapper.__name__ = name
        
        return {
            'wrapp': wrapper,
            'annotation': arg_type,
        }
    

    def If(self, node: If):
        if self.v(node.test):
            return self.v(node.body)
        if node.orelse:
            return self.v(node.orelse)

    def For(self, node: For):
        iterable = self.v(node.iter)
        is_break = False

        for item in iterable:
            parent = self.current_scope
            self.current_scope = Scope(parent=parent)

            self.config.enter_loop()
            try:
                values = item
                if len(node.target) == 1:
                    values = [item]
                for index, target in enumerate(node.target):
                    value = values[index]
                    self.current_scope.declare(
                        target.name.id,
                        self.v(target.type),
                        value,
                        target.constant,
                    )
                self.v(node.body)
            except Continue:
                continue

            except Break:
                break

            except:
                raise

            finally:
                self.current_scope = parent
                self.config.leave_loop()

        else:
            if node.orelse:
                return self.v(node.orelse)

    def While(self, node: While):
        while self.v(node.test):
            parent = self.current_scope
            self.current_scope = parent

            self.config.enter_loop()
            try:
                self.v(node.body)
            except Continue:
                continue

            except Break:
                break

            except:
                raise

            finally:
                self.current_scope = parent
                self.config.leave_loop()
        else:
            if node.orelse:
                return self.v(node.orelse)

    def Try(self, node: Try):
        handled = False
        try:
            self.v(node.body)
        except Throw as err:
            if not node.handler:
                raise
            error = err.args[0] if err.args else IDSRuntimeError('Something was wrong')
            self._handle_exception(node.handler[0], error)
            handled = True

        except Return:
            raise

        except Exception as err:
            if not node.handler:
                raise

            self._handle_exception(node.handler[0], err)
            handled = True

        else:
            if node.orelse:
                self.v(node.orelse)

        finally:
            if node.finalbody:
                self.v(node.finalbody)

        return handled

    def _handle_exception(self, handler: ExceptionHandler, error: Any):
        parent = self.current_scope
        self.current_scope = Scope(parent=parent)
        try:
            self.current_scope.declare(handler.alias.id, Any, error)
            self.v(handler.body)
        finally:
            self.current_scope = parent

    def Switch(self, node: Switch):
        subject = self.v(node.subject)
        default_case = None
        for case in node.cases:
            if case.pattern is None:
                default_case = case
                continue
            if self._match_pattern(case.pattern, subject):
                return self.v(case.body)
        if default_case:
            return self.v(default_case.body)

    def Case(self, node: Case):
        return self.v(node.body)

    def _bind_name(self, name: Name, value: Any):
        try:
            self.current_scope.set(name.id, value)
        except Exception:
            self.current_scope.declare(name.id, Any, value)

    def _match_pattern(self, pattern: Any, value: Any) -> bool:
        if isinstance(pattern, MatchValue):
            if isinstance(pattern.value, Name):
                try:
                    return self.v(pattern.value) == value
                except Exception:
                    self._bind_name(pattern.value, value)
                    return True
            if isinstance(pattern.value, (str, int, float, bool)) or pattern.value is None:
                return pattern.value == value
            return self.v(pattern.value) == value

        if isinstance(pattern, MatchSingleton):
            return value is pattern.value

        if isinstance(pattern, MatchCapture):
            self._bind_name(pattern.name, value)
            return True

        if isinstance(pattern, MatchAs):
            if self._match_pattern(pattern.pattern, value):
                self._bind_name(pattern.name, value)
                return True
            return False

        if isinstance(pattern, MatchOr):
            return any(self._match_pattern(item, value) for item in pattern.patterns)

        if isinstance(pattern, MatchSequence):
            if not isinstance(value, (list, tuple)):
                return False

            dots_indexes = [
                index
                for index, item in enumerate(pattern.patterns)
                if isinstance(item, MatchDots)
            ]
            if not dots_indexes:
                if len(value) != len(pattern.patterns):
                    return False
                return all(
                    self._match_pattern(item_pattern, value[index])
                    for index, item_pattern in enumerate(pattern.patterns)
                )

            if len(dots_indexes) > 1:
                raise NotImplementedError('Multiple unpack patterns belum didukung')

            dots_index = dots_indexes[0]
            before = pattern.patterns[:dots_index]
            after = pattern.patterns[dots_index + 1:]
            if len(value) < len(before) + len(after):
                return False

            for index, item_pattern in enumerate(before):
                if not self._match_pattern(item_pattern, value[index]):
                    return False

            offset = len(value) - len(after)
            for index, item_pattern in enumerate(after):
                if not self._match_pattern(item_pattern, value[offset + index]):
                    return False

            sequence_dots = cast(MatchDots, pattern.patterns[dots_index])
            self._bind_name(sequence_dots.name, list(value[dots_index:offset]))
            return True

        if isinstance(pattern, MatchMapping):
            if not isinstance(value, dict):
                return False

            remaining = dict(value)
            mapping_dots: MatchDots | None = None
            for key_node, item_pattern in zip(pattern.keys, pattern.patterns):
                if isinstance(item_pattern, MatchDots):
                    mapping_dots = item_pattern
                    continue

                key = self.v(key_node)
                if key not in value or not self._match_pattern(item_pattern, value[key]):
                    return False
                remaining.pop(key, None)
            if mapping_dots:
                self._bind_name(mapping_dots.name, remaining)
            return True

        if isinstance(pattern, MatchStruct):
            cls = self.v(pattern.cls)
            try:
                py_class = object.__getattribute__(cls, '__PY_CLASS__')
            except (AttributeError, TypeError):
                py_class = cls if isinstance(cls, type) else None

            if py_class is None or not isinstance(value, py_class):
                return False

            properties = value.to_dict(include_private=True)
            if not properties:
                return False

            remaining = dict(properties)
            struct_dots: MatchDots | None = None
            for keyword_node, item_pattern in zip(pattern.keys, pattern.patterns):
                if isinstance(item_pattern, MatchDots):
                    struct_dots = item_pattern
                    continue

                key = self.v(keyword_node)
                if key not in properties or not self._match_pattern(item_pattern, properties[key]):
                    return False
                remaining.pop(key, None)
            if struct_dots:
                self._bind_name(struct_dots.name, remaining)
            return True

        if isinstance(pattern, MatchDots):
            raise NotImplementedError("Unpack pattern '...' belum didukung sebagai pattern utama")
        return False
    
    
    
    def FromImport(self, node: FromImport):
        path_module = node._from
        if path_module.startswith('.'):
            path_module = Path(self.config.path()).parent / Path(path_module)
        else:
            path_module = Path(__file__).parent.parent.parent / 'builtins' / Path(path_module)

        funcs_wrapp = [ self.v(wrapp) for wrapp in node._imports ]

        if not path_module.exists():
            raise ModuleNotFoundError(f'No module named {str(path_module)!r}')

        if path_module.suffix in {'.idsm', '.idsc', '.idbc'}:
            exports = self._compiled_module_exports(path_module)
            for func_wrapp in funcs_wrapp:
                func_wrapp(exports)
            return

        code = path_module.read_text()
        try:
            from ..entrypoint import Compile
            compile = Compile(code, str(path_module), True)
            exports = compile.exports()

            for func_wrapp in funcs_wrapp:
                func_wrapp(exports)
        except Throw as e:
            raise IDSRuntimeError(f'Something was wrong in {str(path_module)}: {str(e)}') from e
        except:
            raise

    def _compiled_module_exports(self, path_module: Path):
        from ..Compiler.bytecode import ModuleCode
        from ..Compiler.runtime import VM
        from ..Compiler.runtime.vm import VMFunction

        module = ModuleCode.from_bytes(path_module.read_bytes())
        vm = VM(module)
        exports = {}
        for name, value in vm.exports().items():
            export_value = value
            if isinstance(value, VMFunction):
                export_value = _VMFunctionProxy(vm, module.path, name, value)
            exports[name] = {
                'type': Any,
                'value': export_value,
                'constant': True,
            }
        return exports
    
    def ImportAttr(self, node: ImportAttr):
        name = node.name.id
        is_priv = node.is_priv
        is_const = node.is_const
        static = node.static
        
        def wrapp(exports):
            if name == '*' and static and not is_const and not is_priv and not node.alias:
                for name_this, this in exports.items():
                    self.current_scope.declare(
                        name_this,
                        this['type'],
                        this['value'],
                        this['constant'],
                        False,
                    )
                wrapp.name = '*'
                return True
            
            if name not in exports:
                raise ImportError(f'Name {name} never defined')
            this = exports[name]
            
            alias = None
            if node.alias:
                alias = node.alias.id
            
            if static:
                self.current_scope.declare(
                    alias or name,
                    this['type'],
                    this['value'],
                    this['constant'],
                    is_priv,
                )
            
            else:
                self.current_scope.declare(
                    alias or name,
                    this['type'],
                    this['value'],
                    is_const,
                    is_priv,
                )
            
            wrapp.name = name
            return True
        
        return wrapp
    
    
    def Expression(self, node: Expression):
        return self.v(node.value)
    
    def UnaryOp(self, node: UnaryOp):
        return not self.v(node.operand)
    
    def BoolOp(self, node: BoolOp):
        op = node.op
        values = [self.v(value) for value in node.values]
        match op:
            case 'or':
                return values[0] or values[1]
            case 'and':
                return values[0] and values[1]

    def Compare(self, node: Compare):
        left = self.v(node.left)
        ops = node.ops
        comparators = [self.v(comp) for comp in node.comparators]
        compare_ops = {
            '==': operator.eq,
            '!=': operator.ne,
            '>': operator.gt,
            '>=': operator.ge,
            '<': operator.lt,
            '<=': operator.le,
            'in': lambda a, b: a in b,
            'not in': lambda a, b: a not in b,
            'is': operator.is_,
            'is not': operator.is_not,
        }
        
        res = True
        for i, comp in enumerate(comparators):
            res = res and compare_ops[ops[i]](left, comp)
            left = comp
        
        return res
    
    def BinOp(self, node: BinOp):
        left = self.v(node.left)
        op = node.op
        right = self.v(node.right)
        bin_ops = {
            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            '**': operator.pow,
        }
        
        return bin_ops[op](left, right)
    
    def Attribute(self, node: Attribute):
        val = self.v(node.value)
        attr = node.attr
        
        return builtins.getattr(val, attr)
    
    def Index(self, node: Index):
        val = self.v(node.value)
        key = self.v(node.key)
        
        return val[key]
    
    def Call(self, node: Call):
        func = self.v(node.func)
        if not node.args:
            return func()
        
        args = [self.v(arg) for arg in node.args]
        return func(*args)
    
    def Info(self, node: Info):
        value = self.current_scope.get(node.name.id)
        return self._info_name(value)

    def Referensial(self, node: Referensial):
        return self.current_scope.getThis(node.name.id)

    def Deferensial(self, node: Deferensial):
        return self.current_scope.getThis(node.name.id).pointer_get()

    def SalinReferensial(self, node: SalinReferensial):
        variable = self.current_scope.getThis(node.name.id)
        if variable.is_pointer:
            return variable.value
        return variable.copy_address()

    def _info_name(self, value: Any) -> str:
        from .enum import Enum, EnumValue, StructVariant, TupleVariant

        if value is None:
            return 'Kosong'
        if isinstance(value, bool):
            return 'Boolean'
        if isinstance(value, int):
            return 'Angka'
        if isinstance(value, float):
            return 'Float'
        if isinstance(value, str):
            return 'Teks'
        if isinstance(value, list):
            return 'Daftar'
        if isinstance(value, dict):
            return 'Kamus'
        if isinstance(value, Enum):
            return 'Enum'
        if isinstance(value, (EnumValue, StructVariant, TupleVariant)):
            return 'VarianEnum'
        if isinstance(value, Struct) or (
            hasattr(value, '__PROTOTYPE__') and hasattr(value, '__FIELDS__')
        ):
            return 'Struktur'
        if isinstance(value, type) and hasattr(value, '__annotations__') and hasattr(value, '__total__'):
            return 'Antarmuka'
        if isinstance(value, type) or get_origin(value) is not None:
            return 'Tipe'
        if callable(value) or 'Function' in repr(value) or 'Method' in repr(value):
            return 'Fungsi'
        return 'Objek'
    
    def StructFielded(self, node: StructFielded):
        struct = self.v(node.struct)
        kwargs = self.v(node.kwargs)
        
        if type(struct) is not Struct:
            raise AttributeError(f'{str(struct)} is not a structure')
        
        return struct(**kwargs)
    
    def Constant(self, node: Constant):
        return node.value
    
    def Daftar(self, node: Daftar):
        if not node.elts:
            return []
        return [self.v(v) for v in node.elts]
    
    def Kamus(self, node: Kamus):
        if not node.keys and not node.values: return {}
        keys = [self.v(k) for k in node.keys]
        values = [self.v(v) for v in node.values]
        
        res = {}
        for i, key in enumerate(keys):
            res[key] = values[i]
        
        return res
    
    def Type(self, node: Type):
        t = node.type
        if not isinstance(t, type):
            t = self.v(t)
        if node.option: return Optional[t]
        return t
    
    
    def TypeDef(self, node: TypeDef):
        alias = node.alias.id
        value = self.v(node.value)
        
        if not node.args:
            self.current_scope.declare(alias, T, value, True, node.is_priv)
            return 
        
        def wrapper(*arguments):
            names = [arg.id for arg in node.args]
            
            parent = self.current_scope
            self.current_scope = Scope(parent=parent)
            
            for idx, val in enumerate(arguments):
                self.current_scope.declare(names[idx], T, val, True, True)
            names = names[len(arguments):]
            
            if names:
                for name in names:
                    self.current_scope.declare(name, T, Any, True, True)
            
            try:
                return self.v(node.value)
            except:
                raise 
            finally:
                self.current_scope = parent

        wrapper.__name__ = alias
        self.current_scope.declare(alias, Callable[..., Any], wrapper, True, node.is_priv)
        return

    
    def InterFace(self, node: InterFace):
        alias = node.alias.id
        types_attrs = self.v(node.args)
        
        typeddict = cast(Any, TypedDict)(
            alias,
            types_attrs
        )
        
        type_value = type(typeddict)
        
        self.current_scope.declare(
            alias,
            type_value,
            typeddict,
            True,
            node.is_priv
        )
    
    def InterFaceBody(self, node: InterFaceBody):
        keys_name = [self.v(key) for key in node.keys]
        values_type = [self.v(value) for value in node.values]
        
        result = {}
        for key, val in zip(keys_name, values_type):
            result[key] = val
        return result
    
    
    def KEMBALIKAN(self, node: KEMBALIKAN):
        ok = self.v(node.oke_type)
        err = self.v(node.error_type)
        return Result[ok, err]
    
    def FUNGSI(self, node: FUNGSI):
        annotation = node.annotation
        if not node.args:
            return Callable[[], annotation]
        args = [self.v(arg) for arg in node.args]
        return Callable[args, annotation]
    
    def DAFTAR(self, node: DAFTAR):
        body = self.v(node.body)
        return cast(Any, List)[body]
    
    def KAMUS(self, node: KAMUS):
        key = self.v(node.key)
        val = self.v(node.value)
        return cast(Any, Dict)[key, val]
    
    def SERIKAT(self, node: SERIKAT):
        return Union.__getitem__(tuple(self.v(b) for b in node.bodies))
    
    def LITERAL(self, node: LITERAL):
        return Literal.__getitem__(tuple(self.v(b) for b in node.bodies))
    
    
    def Dynamic(self, node: Dynamic):
        typedef = self.v(node.name)
        if not callable(typedef):
            raise TypeError(f'{node.name.id!r} is not a dynamic typedef')
        args = [self.v(arg) for arg in node.args]
        return typedef(*args)
    
    def Name(self, node: Name):
        return self.current_scope.get(node.id)
