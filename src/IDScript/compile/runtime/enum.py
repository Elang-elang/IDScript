"""Native Python runtime wrapper for IDScript `enum` values."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from .config import Config
from .types import check_types


class EnumValue:
    """Concrete value produced by an enum variant.

    Unit and discriminant variants are values immediately. Tuple and struct
    variants produce this value after their payload has been validated.
    """

    def __init__(
        self,
        prototype: dict[str, Any],
        variant: str,
        kind: str,
        payload: tuple[Any, ...] = (),
        fields: Mapping[str, Any] | None = None,
        discriminant: Any = None,
    ):
        object.__setattr__(self, '__PROTOTYPE__', prototype)
        object.__setattr__(self, '_variant', variant)
        object.__setattr__(self, '_kind', kind)
        object.__setattr__(self, '_payload', tuple(payload))
        object.__setattr__(self, '_fields', dict(fields or {}))
        object.__setattr__(self, '_discriminant', discriminant)

    @property
    def enum_name(self) -> str:
        return object.__getattribute__(self, '__PROTOTYPE__')['name']

    @property
    def variant(self) -> str:
        return object.__getattribute__(self, '_variant')

    @property
    def kind(self) -> str:
        return object.__getattribute__(self, '_kind')

    @property
    def payload(self) -> tuple[Any, ...]:
        return object.__getattribute__(self, '_payload')

    @property
    def value(self) -> Any:
        return object.__getattribute__(self, '_discriminant')

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            'enum': self.enum_name,
            'variant': self.variant,
            'kind': self.kind,
        }
        if self.kind == 'tuple':
            result['payload'] = list(self.payload)
        elif self.kind == 'struct':
            result['fields'] = dict(object.__getattribute__(self, '_fields'))
        elif self.kind == 'discriminant':
            result['value'] = self.discriminant
        return result

    def __getattr__(self, name: str) -> Any:
        fields = object.__getattribute__(self, '_fields')
        if name in fields:
            return fields[name]

        prototype = object.__getattribute__(self, '__PROTOTYPE__')
        methods = prototype['methods']
        if name in methods:
            method = methods[name]
            method_schema = prototype['schema'].get(name, {})
            config = prototype['config']
            if method_schema.get('is_priv') and not config.is_struct_name(prototype['name']):
                raise AttributeError(f"Enum {prototype['name']!r} has no attribute {name!r}")

            def bound(*args: Any, **kwargs: Any) -> Any:
                config.enter_struct(prototype['name'])
                try:
                    return method(self, *args, **kwargs)
                finally:
                    config.leave_struct()

            return bound

        raise AttributeError(f"Enum value {self.enum_name}.{self.variant} has no attribute {name!r}")

    def __getitem__(self, key: int | str) -> Any:
        if self.kind == 'tuple':
            return self.payload[int(key)]
        if self.kind == 'struct':
            return object.__getattribute__(self, '_fields')[str(key)]
        raise TypeError(f"Enum value {self.enum_name}.{self.variant} has no payload")

    def __iter__(self):
        if self.kind == 'tuple':
            return iter(self.payload)
        if self.kind == 'struct':
            return iter(object.__getattribute__(self, '_fields').items())
        return iter(())

    def __len__(self) -> int:
        if self.kind == 'tuple':
            return len(self.payload)
        if self.kind == 'struct':
            return len(object.__getattribute__(self, '_fields'))
        return 0

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError(f"Enum value {self.enum_name}.{self.variant} is immutable")

    def __repr__(self) -> str:
        base = f'{self.enum_name}.{self.variant}'
        if self.kind == 'tuple':
            payload = ', '.join(repr(value) for value in self.payload)
            return f'{base}({payload})'
        if self.kind == 'struct':
            fields = object.__getattribute__(self, '_fields')
            body = ', '.join(f'{key}: {value!r}' for key, value in fields.items())
            return f'{base} {{ {body} }}'
        if self.kind == 'discriminant':
            return f'{base} = {self.discriminant!r}'
        return base

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EnumValue):
            return False
        return self.to_dict() == other.to_dict()


class UnitVariant(EnumValue):
    """A unit enum variant, for example `Type.Kosong`."""

    def __init__(self, prototype: dict[str, Any], name: str, discriminant: Any = None):
        kind = 'discriminant' if discriminant is not None else 'unit'
        super().__init__(prototype, name, kind, discriminant=discriminant)

    def __call__(self, *args: Any, **kwargs: Any) -> UnitVariant:
        if args or kwargs:
            raise TypeError(f'{self.enum_name}.{self.variant} does not take payload')
        return self


class TupleVariant:
    """Constructor for tuple variants, for example `Type.Daftar(Vec)`."""

    def __init__(self, prototype: dict[str, Any], name: str, required: list[Any]):
        self._prototype = prototype
        self._name = name
        self._required = list(required)

    def __call__(self, *args: Any) -> EnumValue:
        if len(args) != len(self._required):
            raise TypeError(
                f'{self}() takes {len(self._required)} arguments but {len(args)} was given'
            )
        for index, value in enumerate(args):
            check_types(value, self._required[index])
        return EnumValue(self._prototype, self._name, 'tuple', payload=tuple(args))

    def __repr__(self) -> str:
        return f"{self._prototype['name']}.{self._name}"

    __str__ = __repr__


class StructVariant:
    """Constructor for struct variants, for example `Type.Object { ... }`."""

    def __init__(self, prototype: dict[str, Any], name: str, required: Mapping[str, Any]):
        self._prototype = prototype
        self._name = name
        self._required = dict(required)

    def __call__(self, *args: Any, **kwargs: Any) -> EnumValue:
        if args:
            if len(args) != 1 or not isinstance(args[0], Mapping) or kwargs:
                raise TypeError(f'{self}() expects keyword fields or one mapping payload')
            kwargs = dict(args[0])

        unknown = set(kwargs) - set(self._required)
        missing = set(self._required) - set(kwargs)
        if unknown:
            raise AttributeError(f'{self} has unknown field(s): {", ".join(sorted(unknown))}')
        if missing:
            raise AttributeError(f'{self} missing field(s): {", ".join(sorted(missing))}')

        fields: dict[str, Any] = {}
        for name, expected_type in self._required.items():
            value = kwargs[name]
            check_types(value, expected_type)
            fields[name] = value
        return EnumValue(self._prototype, self._name, 'struct', fields=fields)

    def __repr__(self) -> str:
        return f"{self._prototype['name']}.{self._name}"

    __str__ = __repr__


class Enum:
    """Runtime wrapper for IDScript enums.

    The public surface intentionally mirrors `Structure`: it stores a prototype,
    exposes schema/method helpers, and supports `add_method` for implementations.
    Variant access happens through attributes on the enum object.
    """

    def __init__(
        self,
        name: str,
        config: Config,
        fields: Mapping[str, Any] | None = None,
    ):
        prototype = {
            'name': name,
            'config': config,
            'schema': self._normalize_fields(fields or {}),
            'methods': {},
            'variants': {},
        }
        prototype['variants'] = self._build_variants(prototype)
        object.__setattr__(self, '__PROTOTYPE__', prototype)

    def __call__(self, *args: Any, **kwargs: Any) -> object:
        raise TypeError('Enum type cannot be called directly; call one of its variants')

    def __getattr__(self, name: str) -> Any:
        prototype = object.__getattribute__(self, '__PROTOTYPE__')
        if name in prototype:
            return prototype[name]
        if name in prototype['variants']:
            self._ensure_access(prototype, name)
            return prototype['variants'][name]
        if name in prototype['methods']:
            method = prototype['methods'][name]

            def bound(*args: Any, **kwargs: Any) -> Any:
                config = prototype['config']
                config.enter_struct(prototype['name'])
                try:
                    return method(self, *args, **kwargs)
                finally:
                    config.leave_struct()

            return bound
        raise AttributeError(f"Enum {prototype['name']!r} has no attribute {name!r}")

    def set_method(
        self,
        name: str,
        value: Callable[..., Any] | None = None,
        type: Any = Any,
        is_priv: bool = False,
        **kwargs: Any,
    ) -> None:
        method = value or kwargs.get('method')
        if method is None:
            raise TypeError('set_method() missing method value')
        check_types(method, type)

        prototype = object.__getattribute__(self, '__PROTOTYPE__')
        prototype['schema'][name] = {
            'kind': 'method',
            'is_priv': is_priv,
            'is_method': True,
            'constant': True,
        }
        prototype['methods'][name] = method

    add_method = set_method

    def has_property(self, name: str) -> bool:
        prototype = object.__getattribute__(self, '__PROTOTYPE__')
        return name in prototype['variants']

    def has_method(self, name: str) -> bool:
        prototype = object.__getattribute__(self, '__PROTOTYPE__')
        return name in prototype['methods']

    def has(self, name: str) -> bool:
        return self.has_property(name) or self.has_method(name)

    def to_dict(self) -> dict[str, Any]:
        prototype = object.__getattribute__(self, '__PROTOTYPE__')
        return {
            'name': prototype['name'],
            'schema': dict(prototype['schema']),
            'methods': list(prototype['methods'].keys()),
            'variants': list(prototype['variants'].keys()),
        }

    def _normalize_fields(self, fields: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
        normalized: dict[str, dict[str, Any]] = {}
        for name, field in fields.items():
            if isinstance(field, Mapping):
                kind = self._variant_kind(field)
                normalized[name] = {
                    'kind': kind,
                    'is_priv': bool(field.get('is_priv', False)),
                    'is_method': bool(field.get('is_method', False)),
                    'constant': bool(field.get('constant', True)),
                    'args': list(field.get('args', field.get('required', []))) if kind == 'tuple' else [],
                    'fields': dict(field.get('fields', field.get('required', {}))) if kind == 'struct' else {},
                    'value': field.get('value', field.get('discriminant')),
                }
            elif field == 'unit':
                normalized[name] = self._unit_schema()
            elif isinstance(field, (list, tuple)):
                normalized[name] = {**self._unit_schema(), 'kind': 'tuple', 'args': list(field)}
            else:
                normalized[name] = {**self._unit_schema(), 'kind': 'discriminant', 'value': field}
        return normalized

    def _variant_kind(self, field: Mapping[str, Any]) -> str:
        raw_kind = field.get('kind', field.get('variant', field.get('type')))
        if raw_kind in {'unit', 'tuple', 'struct', 'discriminant'}:
            return str(raw_kind)
        if 'args' in field:
            return 'tuple'
        if 'fields' in field or isinstance(field.get('required'), Mapping):
            return 'struct'
        if 'value' in field or 'discriminant' in field:
            return 'discriminant'
        return 'unit'

    def _unit_schema(self) -> dict[str, Any]:
        return {
            'kind': 'unit',
            'is_priv': False,
            'is_method': False,
            'constant': True,
            'args': [],
            'fields': {},
            'value': None,
        }

    def _build_variants(self, prototype: dict[str, Any]) -> dict[str, Any]:
        variants: dict[str, Any] = {}
        for name, field in prototype['schema'].items():
            if field.get('is_method'):
                continue
            kind = field['kind']
            if kind == 'unit':
                variants[name] = UnitVariant(prototype, name)
            elif kind == 'tuple':
                variants[name] = TupleVariant(prototype, name, field['args'])
            elif kind == 'struct':
                variants[name] = StructVariant(prototype, name, field['fields'])
            elif kind == 'discriminant':
                variants[name] = UnitVariant(prototype, name, field['value'])
            else:
                raise ValueError(f'Unknown enum variant kind {kind!r}')
        return variants

    def _ensure_access(self, prototype: dict[str, Any], name: str) -> None:
        field = prototype['schema'][name]
        config = prototype['config']
        if field.get('is_priv') and \
          not config.is_struct_name(prototype['name']) and \
          config.is_module():
            raise AttributeError(f"Enum {prototype['name']!r} has no attribute {name!r}")

    def __repr__(self) -> str:
        prototype = object.__getattribute__(self, '__PROTOTYPE__')
        return f"<Enum: {prototype['name']}>"
