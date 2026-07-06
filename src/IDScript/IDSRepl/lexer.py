from pygments.lexer import RegexLexer, default
from pygments.token import (
    Keyword, Name, Number, String, Comment, Operator, Punctuation, Text, Whitespace,
)

class IDScriptLexer(RegexLexer):
    name = "IDScript"
    aliases = ["idscript", "ids"]
    filenames = ["*.ids", "*.idsc", "*.idsm"]

    tokens = {
        "root": [
            (r"\s+", Whitespace),
            (r"//[^\n]*", Comment.Single),
            (r"/\*", Comment.Multiline, "comment"),
            (r'"(?:[^"\\]|\\.)*"', String.Double),
            (r"\b(konst|KONSTANTA|var|final)\b", Keyword, "var-name"),
            (r"\b(publik|privat|statik)\b", Keyword),
            (r"\b(fungsi|metode)\b", Keyword, "func-name"),
            (r"\b(struktur)\b", Keyword, "struct-name"),
            (r"\b(enum)\b", Keyword, "struct-name"),
            (r"\b(implementasi)\b", Keyword, "impl-subject"),
            (r"\b(sifat)\b", Keyword, "iface-name"),
            (r"\b(antarmuka)\b", Keyword, "iface-name"),
            (r"\b(tipe)\b", Keyword, "type-name"),
            (r"\b(turunan|dari)\b", Keyword.Namespace),
            (r"\b(jika|namun|untuk|dalam|selama|coba|tangkap|diakhiri|pilah|kasus|bawaan)\b", Keyword),
            (r"\b(kembalikan|kesalahan|berhentikan|lanjutkan)\b", Keyword),
            (r"\b(bukan|atau|dan|didalam|adalah|bukanlah|sebagai|salin|impor)\b", Keyword),
            (r"\b(benar|salah|kosong)\b", Keyword.Constant),
            (r"\b(Angka|Float|Teks|Boolean|Kosong|Apapun|daftar|kamus|hasil)\b", Name.Builtin),
            (r"\b(Daftar|Kamus|Fungsi)\b", Name.Builtin),
            (r"\b\d+\.\d+\b", Number.Float),
            (r"\b\d+\b", Number.Integer),
            (r"!=|==|<=|>=|&&|\|\||[-+*/%=!&|^~?:]", Operator),
            (r"\.", Name.Other),
            (r"[(){}\[\]<>,:;@]", Punctuation),
            (r"[a-zA-Z_]\w*", Text),
        ],
        "comment": [
            (r"\*/", Comment.Multiline, "#pop"),
            (r"[^*]+", Comment.Multiline),
            (r"\*", Comment.Multiline),
        ],
        "var-name": [
            (r"\s+", Whitespace),
            (r"[a-zA-Z_]\w*", Name.Variable, "#pop"),
            default("#pop"),
        ],
        "func-name": [
            (r"\s+", Whitespace),
            (r"[a-zA-Z_]\w*", Name.Function, "#pop"),
            default("#pop"),
        ],
        "struct-name": [
            (r"\s+", Whitespace),
            (r"[a-zA-Z_]\w*", Name.Class, "#pop"),
            default("#pop"),
        ],
        "impl-subject": [
            (r"\s+", Whitespace),
            (r"[a-zA-Z_]\w*", Name.Class, "#pop"),
            default("#pop"),
        ],
        "iface-name": [
            (r"\s+", Whitespace),
            (r"[a-zA-Z_]\w*", Name.Class, "#pop"),
            default("#pop"),
        ],
        "type-name": [
            (r"\s+", Whitespace),
            (r"[a-zA-Z_]\w*", Name.Class, "#pop"),
            default("#pop"),
        ],
    }
