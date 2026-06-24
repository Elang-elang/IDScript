"""Native Python runtime wrapper for IDScript `struktur` values."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from .types import check_types
from .config import Config
from copy import deepcopy


class Structure:
    def __init__(
        self,
        name: str,
        config: Config,
        fields: Mapping[str, Any] | None = None,
        extend: Structure | None = None,
    ):
        prototype = {
            'name': name,
            'config': config,
            'schema': self._normalize_fields(fields or {}),
            'methods': {},
            'extend': {
                'schema': {},
                'methods': {},
            }
        }
        if extend:
            self._normalize_extend(prototype, extend.__PROTOTYPE__)

        object.__setattr__(self, '__PROTOTYPE__', prototype)
        object.__setattr__(self, '__PY_CLASS__', self._build_class(prototype))

    def __call__(self, **kwargs: Any) -> object:
        py_class = object.__getattribute__(self, '__PY_CLASS__')
        return py_class(**kwargs)

    def __getattr__(self, name: str) -> Any:
        prototype = object.__getattribute__(self, '__PROTOTYPE__')
        if name in prototype:
            return prototype[name]
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
        raise AttributeError(f"Structure {prototype['name']!r} has no attribute {name!r}")

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
        if name in prototype['methods']:
            raise AttributeError(
                f"Structure {prototype['name']!r} has duplicated method {name!r}"
            )
        if name in prototype['schema'] and not prototype['schema'][name].get('is_method'):
            raise AttributeError(
                f"Structure {prototype['name']!r} has duplicated member {name!r}"
            )
        prototype['schema'][name] = {
            'type': type,
            'is_priv': is_priv,
            'is_method': True,
            'constant': True,
            'default': None,
        }
        prototype['methods'][name] = method

    add_method = set_method

    def has_property(self, name: str) -> bool:
        prototype = object.__getattribute__(self, '__PROTOTYPE__')
        field = prototype['schema'].get(name)
        return bool(field and not field.get('is_method'))

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
        }

    def _normalize_fields(self, fields: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
        normalized: dict[str, dict[str, Any]] = {}
        for name, field in fields.items():
            if isinstance(field, Mapping):
                normalized[name] = {
                    'type': field.get('type', Any),
                    'is_priv': bool(field.get('is_priv', False)),
                    'is_method': bool(field.get('is_method', False)),
                    'constant': bool(field.get('constant', False)),
                    'default': field.get('default'),
                }
            else:
                normalized[name] = {
                    'type': field,
                    'is_priv': False,
                    'is_method': False,
                    'constant': False,
                    'default': None,
                }
        return normalized

    def _normalize_extend(
        self,
        this_prototype: dict[str, Any],
        extend_prototype: dict[str, Any]
    ) -> None:
        struct_name = this_prototype['name']
        this_schema = this_prototype['schema']
        this_methods = this_prototype['methods']
        extend_schema = extend_prototype['schema']
        extend_methods = extend_prototype['methods']

        if not extend_schema and not extend_methods:
            return

        this_properties = {
            name: field
            for name, field in this_schema.items()
            if not field.get('is_method')
        }
        extend_properties = {
            name: field
            for name, field in extend_schema.items()
            if not field.get('is_method')
        }

        duplicated = set(this_properties) & set(extend_properties)
        if duplicated:
            raise AttributeError(
                f'Structure {struct_name!r} has duplicated field(s): '
                f"{', '.join(sorted(duplicated))}"
            )

        duplicated_methods = set(this_methods) & set(extend_methods)
        if duplicated_methods:
            raise AttributeError(
                f'Structure {struct_name!r} has duplicated method(s): '
                f"{', '.join(sorted(duplicated_methods))}"
            )

        parent_schema = deepcopy(extend_schema)
        parent_methods = deepcopy(extend_methods)
        parent_schema.update(this_schema)
        parent_methods.update(this_methods)

        this_prototype['schema'] = parent_schema
        this_prototype['methods'] = parent_methods

    def _build_class(self, prototype: dict[str, Any]) -> type:
        struct_name = prototype['name']

        def ensure_access(instance: object, name: str) -> None:
            field = prototype['schema'][name]
            config = prototype['config']
            if field.get('is_priv') and not config.is_struct_name(struct_name):
                raise AttributeError(f'Structure {struct_name!r} has no attribute {name!r}')

        def init(instance: object, **kwargs: Any) -> None:
            schema = prototype['schema']
            properties = {
                name: field
                for name, field in schema.items()
                if not field.get('is_method')
            }
            unknown = set(kwargs) - set(properties)
            required = {
                name
                for name, field in properties.items()
                if field.get('default') is None and name not in kwargs
            }

            if unknown:
                raise AttributeError(
                    f'Structure {struct_name!r} has no field(s): '
                    f"{', '.join(sorted(unknown))}"
                )
            if required:
                raise AttributeError(
                    f'Structure {struct_name!r} missing field(s): '
                    f"{', '.join(sorted(required))}"
                )

            object.__setattr__(instance, '__PROTOTYPE__', prototype)
            object.__setattr__(
                instance,
                '__FIELDS__',
                {'properties': {}, 'methods': dict(prototype['methods'])},
            )

            fields = object.__getattribute__(instance, '__FIELDS__')
            for name, field in properties.items():
                value = kwargs.get(name, field.get('default'))
                check_types(value, field.get('type', Any))
                fields['properties'][name] = value

        def get_attr(instance: object, name: str) -> Any:
            fields = object.__getattribute__(instance, '__FIELDS__')
            schema = prototype['schema']

            if name in fields['properties']:
                ensure_access(instance, name)
                return fields['properties'][name]

            if name in fields['methods']:
                ensure_access(instance, name)
                method = fields['methods'][name]

                def bound(*args: Any, **kwargs: Any) -> Any:
                    config = prototype['config']
                    config.enter_struct(struct_name)
                    try:
                        return method(instance, *args, **kwargs)
                    finally:
                        config.leave_struct()

                return bound

            if name in schema:
                raise AttributeError(f'Structure {struct_name!r} has no attribute {name!r}')
            raise AttributeError(f'Structure {struct_name!r} has no attribute {name!r}')

        def set_attr(instance: object, name: str, value: Any) -> None:
            if name in {'__PROTOTYPE__', '__FIELDS__'} or name.startswith('_'):
                object.__setattr__(instance, name, value)
                return

            fields = object.__getattribute__(instance, '__FIELDS__')
            schema = prototype['schema']
            if name not in schema or schema[name].get('is_method'):
                raise AttributeError(f'Structure {struct_name!r} has no property {name!r}')

            ensure_access(instance, name)
            field = schema[name]
            if field.get('constant'):
                raise AttributeError(f'Structure field {name!r} is constant')

            check_types(value, field.get('type', Any))
            fields['properties'][name] = value

        def call(instance: object, *args: Any) -> Any:
            fields = object.__getattribute__(instance, '__FIELDS__')
            method = fields['methods'].get('inisiasi')
            if method is None:
                raise AttributeError(f"Structure {struct_name!r} has no method 'inisiasi'")

            config = prototype['config']
            config.enter_struct(struct_name)
            try:
                result = method(instance, *args)
            finally:
                config.leave_struct()
            check_types(result, type(None))
            return result

        def call_special(instance: object, name: str, *args: Any) -> Any:
            fields = object.__getattribute__(instance, '__FIELDS__')
            method = fields['methods'].get(name)
            if method is None:
                return NotImplemented

            config = prototype['config']
            previous = config.enter_struct(struct_name)
            try:
                return method(instance, *args)
            finally:
                config.leave_struct()

        def special_unary(instance: object, name: str) -> Any:
            result = call_special(instance, name)
            if result is NotImplemented:
                raise TypeError(f"Structure {struct_name!r} does not implement {name}")
            return result

        def special_binary(instance: object, name: str, other: Any) -> Any:
            return call_special(instance, name, other)

        def special_setitem(instance: object, key: Any, value: Any) -> None:
            result = call_special(instance, '__setitem__', key, value)
            if result is NotImplemented:
                raise TypeError(f"Structure {struct_name!r} does not implement __setitem__")

        def special_delitem(instance: object, key: Any) -> None:
            result = call_special(instance, '__delitem__', key)
            if result is NotImplemented:
                raise TypeError(f"Structure {struct_name!r} does not implement __delitem__")

        def to_dict(instance: object, include_private: bool = False) -> dict[str, Any]:
            fields = object.__getattribute__(instance, '__FIELDS__')
            result: dict[str, Any] = {}
            for name, value in fields['properties'].items():
                if prototype['schema'][name].get('is_priv') and not include_private:
                    continue
                result[name] = value
            return result

        def repr_instance(instance: object) -> str:
            result = call_special(instance, '__repr__')
            if result is not NotImplemented:
                return str(result)
            return f'{struct_name} {to_dict(instance)}'

        namespace = {
            '__PROTOTYPE__': prototype,
            '__init__': init,
            '__getattr__': get_attr,
            '__setattr__': set_attr,
            '__call__': call,
            '__contains__': lambda instance, item: bool(special_binary(instance, '__contains__', item)),
            '__len__': lambda instance: special_unary(instance, '__len__'),
            '__iter__': lambda instance: special_unary(instance, '__iter__'),
            '__getitem__': lambda instance, key: special_binary(instance, '__getitem__', key),
            '__setitem__': special_setitem,
            '__delitem__': special_delitem,
            '__add__': lambda instance, other: special_binary(instance, '__add__', other),
            '__mul__': lambda instance, other: special_binary(instance, '__mul__', other),
            '__rmul__': lambda instance, other: special_binary(instance, '__rmul__', other),
            '__iadd__': lambda instance, other: special_binary(instance, '__iadd__', other),
            '__imul__': lambda instance, other: special_binary(instance, '__imul__', other),
            '__eq__': lambda instance, other: special_binary(instance, '__eq__', other),
            '__ne__': lambda instance, other: special_binary(instance, '__ne__', other),
            '__lt__': lambda instance, other: special_binary(instance, '__lt__', other),
            '__le__': lambda instance, other: special_binary(instance, '__le__', other),
            '__gt__': lambda instance, other: special_binary(instance, '__gt__', other),
            '__ge__': lambda instance, other: special_binary(instance, '__ge__', other),
            'to_dict': to_dict,
            '__repr__': repr_instance,
            '__match_args__': tuple(
                name
                for name, field in prototype['schema'].items()
                if not field.get('is_method')
            ),
        }
        return type(struct_name, (object,), namespace)

    def __repr__(self) -> str:
        prototype = object.__getattribute__(self, '__PROTOTYPE__')
        return f"<Structure: {prototype['name']}>"


class Trait:
    def __init__(
        self,
        name: str,
        data: dict[str, Any]
    ) -> None:
        self._name = name
        self._data = data

    def __call__(
        self,
        methods: list[dict[str, Any]] | None = None
    ) -> None:
        data_methods = {
            method['name']: method
            for method in methods or []
        }

        missing = set(self._data) - set(data_methods)
        if missing:
            raise AttributeError(
                f'Trait {self._name!r} missing method(s): '
                f"{', '.join(sorted(missing))}"
            )

        for name, object_data in self._data.items():
            subject_data = data_methods[name]
            if object_data['type'] != subject_data['type']:
                raise TypeError(
                    f'{name}() from implement doesnt same with {name}() from trait '
                    f"type: {object_data['type']}"
                )
            
            expected_annotations = object_data['annotations']
            annotations = subject_data['value'].__annotations__
            expected_names = set(expected_annotations)
            actual_names = set(annotations)

            if expected_names != actual_names:
                missing_names = expected_names - actual_names
                extra_names = actual_names - expected_names
                mismatched_names = sorted(missing_names | extra_names)
                raise TypeError(
                    f'{name}() from implement doesnt same with {name}() from trait '
                    f"args: {', '.join(mismatched_names)}"
                )

            for arg_name, expected_type in expected_annotations.items():
                if annotations[arg_name] == expected_type:
                    continue
                raise TypeError(
                    f'{name}() from implement doesnt same with {name}() from trait '
                    f'annotation {arg_name}: {expected_type}'
                )

        return

    def __repr__(self):
        return f'<Trait: {self._name}>'
