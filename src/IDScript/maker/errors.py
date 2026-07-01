from __future__ import annotations

from typing import Any, Iterable

from ..exceptions import IDSError


class IDSMakerError(IDSError):
    """Configuration error raised by the Python-to-IDScript maker API."""

    kind = "maker error"


def reject_positional(wrapper: str, args: tuple[Any, ...]) -> None:
    if args:
        raise IDSMakerError(
            f"{wrapper} does not accept positional arguments; use keyword options instead. "
            f"Received {len(args)} positional argument(s)."
        )


def validate_options(
    wrapper: str,
    options: dict[str, Any],
    valid: Iterable[str],
    required: Iterable[str] = (),
) -> None:
    valid_set = set(valid)
    required_set = set(required)
    unknown = sorted(set(options) - valid_set)
    if unknown:
        valid_text = ", ".join(sorted(valid_set)) or "<none>"
        unknown_text = ", ".join(repr(name) for name in unknown)
        raise IDSMakerError(
            f"{wrapper} option(s) {unknown_text} are not supported. "
            f"Valid options are: {valid_text}."
        )
    missing = sorted(name for name in required_set if name not in options or options[name] is None)
    if missing:
        missing_text = ", ".join(repr(name) for name in missing)
        raise IDSMakerError(f"{wrapper} requires option(s): {missing_text}.")


def ensure_type(wrapper: str, option: str, value: Any, expected: type | tuple[type, ...]) -> None:
    if not isinstance(value, expected):
        expected_text = _type_text(expected)
        raise IDSMakerError(
            f"{wrapper} option {option!r} must be {expected_text}; "
            f"got {type(value).__name__}."
        )


def validate_declare(value: str) -> None:
    if value not in {"private", "public"}:
        raise IDSMakerError(
            f"Option 'declare' must be either 'private' or 'public'; got {value!r}."
        )


def _type_text(expected: type | tuple[type, ...]) -> str:
    if isinstance(expected, tuple):
        return " or ".join(item.__name__ for item in expected)
    return expected.__name__
