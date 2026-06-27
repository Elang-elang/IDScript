"""IDScript exception hierarchy and source diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
import os
import re
from typing import Any

from lark import UnexpectedCharacters, UnexpectedEOF, UnexpectedInput, UnexpectedToken


@dataclass(frozen=True)
class SourceSpan:
    file: str
    line: int
    column: int
    end_line: int | None = None
    end_column: int | None = None

    def label(self) -> str:
        return f"{self.file}:{self.line}:{self.column}"


_ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "gray": "\033[90m",
}


def _use_color() -> bool:
    return (
        "NO_COLOR" not in os.environ
        and "IDS_NO_COLOR" not in os.environ
        and os.environ.get("IDS_COLOR", "1").lower() not in {"0", "false", "no"}
    )


def _paint(text: str, *styles: str) -> str:
    if not _use_color():
        return text
    prefix = "".join(_ANSI[style] for style in styles)
    return f"{prefix}{text}{_ANSI['reset']}"


class IDSError(Exception):
    """Base exception for all public IDScript errors."""

    kind = "kesalahan"

    def __init__(
        self,
        message: Any,
        *,
        span: SourceSpan | None = None,
        context: str | None = None,
        help_text: str | None = None,
        cause: BaseException | None = None,
        payload: Any = None,
    ):
        self.message = str(message)
        self.payload = message if payload is None else payload
        self.span = span
        self.context = context
        self.help_text = help_text
        self.cause = cause
        super().__init__(self.payload)

    def __str__(self) -> str:
        return self.format_message()

    def format_message(self) -> str:
        if self.span is not None:
            location = _paint(self.span.label(), "bold", "cyan")
            kind = _paint(self.kind, "bold", "red")
            message = f"{location}: {kind}: {self.message}"
        else:
            kind = _paint(self.kind, "bold", "red")
            message = f"{kind}: {self.message}"
        if self.context:
            message = f"{message}\n{self.context}"
        if self.help_text:
            help_label = _paint("bantuan:", "bold", "cyan")
            message = f"{message}\n{help_label} {self.help_text}"
        return message


class IDSSyntaxError(IDSError, SyntaxError):
    """Syntax does not match the IDScript grammar."""

    kind = "kesalahan sintaks"

    @classmethod
    def from_lark(cls, error: UnexpectedInput, file: str, source: str) -> IDSSyntaxError:
        span = SourceSpan(file=file, line=error.line, column=error.column)
        context = _source_context(source, span) if source else None
        expected = getattr(error, "expected", None) or getattr(error, "allowed", None)
        expected_text = _expected_list(expected)

        if isinstance(error, UnexpectedToken):
            found = str(error.token)
            message = f"ditemukan token {found!r} yang tidak sesuai tata bahasa"
        elif isinstance(error, UnexpectedCharacters):
            found = source[error.pos_in_stream:error.pos_in_stream + 1] if source else ""
            message = f"ditemukan karakter {found!r} yang tidak sesuai tata bahasa"
        elif isinstance(error, UnexpectedEOF):
            message = "source berakhir sebelum tata bahasa lengkap"
        else:
            message = "tata bahasa tidak cocok"

        help_text = None
        if expected_text:
            help_text = f"di posisi ini diharapkan salah satu dari: {expected_text}"
        return cls(message, span=span, context=context, help_text=help_text, cause=error)


class IDSNameError(IDSError, NameError):
    """Identifier lookup failed."""

    kind = "identifier tidak terdefinisi"


class IDSRuntimeError(IDSError, RuntimeError):
    """General runtime error for interpreter and VM execution."""

    kind = "kesalahan runtime"

    
    @classmethod
    def from_exception(
        cls,
        error: BaseException,
        *,
        file: str | None = None,
        span: SourceSpan | None = None,
        message: str | None = None,
    ) -> IDSRuntimeError:
        span = span or getattr(error, "__ids_source__", None)
        text = message or f"{type(error).__name__}: {str(error)}"
        if file and span is None:
            text = f"Something was wrong on file\n    {file!r}\n\n{text}"
        return cls(text, span=span, cause=error)


def _has_position(value: Any) -> bool:
    return bool(getattr(value, "line", None) and getattr(value, "column", None))


def span_from_meta(meta: Any, file: str = "<unknown>") -> SourceSpan | None:
    if not _has_position(meta):
        return None
    return SourceSpan(
        file=file,
        line=meta.line,
        column=meta.column,
        end_line=getattr(meta, "end_line", None),
        end_column=getattr(meta, "end_column", None),
    )


def span_from_token(token: Any, file: str = "<unknown>") -> SourceSpan | None:
    if not _has_position(token):
        return None
    return SourceSpan(
        file=file,
        line=token.line,
        column=token.column,
        end_line=getattr(token, "end_line", None),
        end_column=getattr(token, "end_column", None),
    )


def set_source(node: Any, span: SourceSpan | None) -> Any:
    if node is None or span is None:
        return node
    try:
        if getattr(node, "__ids_source__", None) is None:
            setattr(node, "__ids_source__", span)
    except Exception:
        pass
    return node


def get_source(node: Any) -> SourceSpan | None:
    return getattr(node, "__ids_source__", None)


def annotate_exception(error: Exception, span: SourceSpan | None) -> Exception:
    if span is None or getattr(error, "__ids_source__", None) is not None:
        return error

    setattr(error, "__ids_source__", span)
    if isinstance(error, IDSError):
        error.span = span
        return error

    location = f"at {span.label()}"
    message = str(error)
    if location not in message:
        error.args = (f"{message}\n  {location}" if message else location,)
    if hasattr(error, "add_note"):
        error.add_note(location)
    return error


_EXPECTED_NAMES = {
    "LBRACE": "'{'",
    "RBRACE": "'}'",
    "LPAR": "'('",
    "RPAR": "')'",
    "LSQB": "'['",
    "RSQB": "']'",
    "COLON": "':'",
    "COMMA": "','",
    "SEMICOLON": "';'",
    "DOT": "'.'",
    "EQUAL": "'='",
    "PLUS": "'+'",
    "MINUS": "'-'",
    "STAR": "'*'",
    "SLASH": "'/'",
    "AMPERSAND": "'&'",
    "MORETHAN": "'>'",
    "LESSTHAN": "'<'",
    "NAME": "nama identifier",
    "TYPE": "tipe",
    "NUMBER": "angka",
    "STRING": "teks/string",
    "DAN": "'dan'",
    "ATAU": "'atau'",
    "DIDALAM": "'didalam'",
    "TIDAK": "'tidak'",
    "ADALAH": "'adalah'",
    "BUKANLAH": "'bukanlah'",
    "__ANON_3": "'=='",
    "__ANON_4": "'!='",
    "__ANON_5": "'>='",
    "__ANON_6": "'<='",
    "__ANON_7": "'**'",
    "__ANON_2": "'?'",
}

_EXPECTED_PRIORITY = {
    "SEMICOLON": 0,
    "RPAR": 1,
    "RBRACE": 2,
    "RSQB": 3,
    "COMMA": 4,
    "COLON": 5,
    "NAME": 6,
}

_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_NUMBER_RE = re.compile(r"[-+]?(?:\d+\.\d+|\d+)(?:[eE][-+]?\d+)?\b")

_DECLARATION_KEYWORDS = {
    "fungsi",
    "metode",
    "struktur",
    "implementasi",
    "sifat",
    "enum",
    "tipe",
    "antarmuka",
    "turunan",
}

_CONTROL_KEYWORDS = {
    "jika",
    "namun",
    "tidak",
    "untuk",
    "dari",
    "dalam",
    "selama",
    "coba",
    "tangkap",
    "diakhiri",
    "pilah",
    "kasus",
    "bawaan",
}

_FLOW_KEYWORDS = {
    "kembalikan",
    "kesalahan",
    "berhentikan",
    "lanjutkan",
}

_MODIFIER_KEYWORDS = {
    "publik",
    "privat",
    "statik",
    "final",
    "var",
    "konst",
    "KONSTANTA",
    "konstan",
}

_WORD_OPERATORS = {
    "bukan",
    "atau",
    "dan",
    "didalam",
    "adalah",
    "bukanlah",
    "sebagai",
    "salin",
    "impor",
}

_CONSTANTS = {"benar", "salah", "kosong"}
_BUILTIN_TYPES = {
    "Teks",
    "Angka",
    "Float",
    "Boolean",
    "Kosong",
    "Apapun",
    "OBJEK",
    "daftar",
    "kamus",
    "hasil",
}


def _expected_name(name: str) -> str:
    return _EXPECTED_NAMES.get(name, name.lower().replace("_", " "))


def _expected_list(expected: Any) -> str:
    names = [str(item) for item in expected or []]
    names.sort(key=lambda item: (_EXPECTED_PRIORITY.get(item, 100), _expected_name(item)))
    values = [_expected_name(item) for item in names]
    if not values:
        return ""
    if len(values) > 8:
        values = [*values[:8], "..."]
    return ", ".join(values)


def _highlight_identifier(value: str) -> str:
    if value in _DECLARATION_KEYWORDS:
        return _paint(value, "bold", "magenta")
    if value in _CONTROL_KEYWORDS:
        return _paint(value, "bold", "blue")
    if value in _FLOW_KEYWORDS:
        return _paint(value, "bold", "red")
    if value in _MODIFIER_KEYWORDS:
        return _paint(value, "yellow")
    if value in _WORD_OPERATORS:
        return _paint(value, "magenta")
    if value in _CONSTANTS:
        return _paint(value, "bold", "magenta")
    if value in _BUILTIN_TYPES:
        return _paint(value, "bold", "cyan")
    return value


def _highlight_source_line(line: str) -> str:
    if not _use_color():
        return line

    result: list[str] = []
    index = 0
    while index < len(line):
        if line.startswith("//", index):
            result.append(_paint(line[index:], "dim", "gray"))
            break
        if line.startswith("/*", index):
            result.append(_paint(line[index:], "dim", "gray"))
            break

        char = line[index]
        if char == '"':
            start = index
            index += 1
            escaped = False
            while index < len(line):
                current = line[index]
                if current == '"' and not escaped:
                    index += 1
                    break
                escaped = current == "\\" and not escaped
                if current != "\\":
                    escaped = False
                index += 1
            result.append(_paint(line[start:index], "green"))
            continue

        number = _NUMBER_RE.match(line, index)
        if number:
            result.append(_paint(number.group(0), "yellow"))
            index = number.end()
            continue

        identifier = _IDENT_RE.match(line, index)
        if identifier:
            result.append(_highlight_identifier(identifier.group(0)))
            index = identifier.end()
            continue

        if line.startswith(("==", "!=", ">=", "<=", "**"), index):
            result.append(_paint(line[index:index + 2], "bold", "magenta"))
            index += 2
            continue

        if char in "&*+-/=<>!?":
            result.append(_paint(char, "bold", "magenta"))
        elif char in "{}[](),;:.":
            result.append(_paint(char, "blue"))
        else:
            result.append(char)
        index += 1

    return "".join(result)


def _source_context(source: str, span: SourceSpan) -> str:
    lines = source.splitlines()
    if span.line < 1 or span.line > len(lines):
        return ""

    radius = 2
    start_line = max(span.line - radius, 1)
    end_line = min(span.line + radius, len(lines))
    line_number_width = len(str(end_line))
    gutter = " " * line_number_width
    caret_offset = max(span.column - 1, 0)
    bar = _paint("|", "blue")
    caret = _paint("^", "bold", "red")

    context = [f" {gutter} {bar}"]
    for line_number in range(start_line, end_line + 1):
        raw_line = lines[line_number - 1]
        display_number = str(line_number).rjust(line_number_width)
        if line_number == span.line:
            display_number = _paint(display_number, "bold", "red")
        else:
            display_number = _paint(display_number, "blue")
        context.append(f" {display_number} {bar} {_highlight_source_line(raw_line)}")
        if line_number == span.line:
            context.append(f" {gutter} {bar} {' ' * caret_offset}{caret}")
    return "\n".join(context)


# Compatibility with the earlier temporary name.
IDSyntaxError = IDSSyntaxError