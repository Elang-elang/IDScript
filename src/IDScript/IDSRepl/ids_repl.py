from IDScript.IDSRepl.execute import _eval, _exec
from IDScript.IDSRepl.colour import BOLD, CYAN, YELLOW, RED, RESET, fmt_val
from IDScript.IDSRepl.lexer import IDScriptLexer
from IDScript.IDSRepl.readline import make_session, readline_input
import sys


_STMT_KEYWORDS = frozenset({
    "var", "konst", "final", "fungsi", "metode",
    "struct", "struktur", "impl", "implementasi",
    "jika", "coba", "kembalikan", "untuk",
    "enum", "antarmuka", "trait", "sifat", "typedef", "tipe",
    "dari", "impor", "selama", "pilah", "kesalahan",
    "berhentikan", "lanjutkan",
})

_EXPR_START = frozenset({
    "(", "[", "{", "!", "-", "+", "~",
    "angka", "teks", "bool", "benar", "salah", "kosong",
})


def _is_expr_like(s: str) -> bool:
    first = s.lstrip().split(None, 1)[0] if s.strip() else ""
    if not first:
        return False
    if first in _EXPR_START:
        return True
    if first.startswith('"'):
        return True
    if first[0].isdigit() or first[0] in ".@":
        return True
    if first[0].isalpha() and first not in _STMT_KEYWORDS:
        rest = s.lstrip()[len(first):].lstrip()
        if rest.startswith('='):
            return False
        return True
    return False


def run_one(bersih: str):
    if _is_expr_like(bersih):
        hasil = _eval(bersih)
        return hasil
    _exec(bersih)
    return None


def main() -> int:
    session = make_session(IDScriptLexer)

    print(f"{BOLD}{CYAN}IDScript REPL — .keluar untuk keluar{RESET}")

    while True:
        try:
            if session is not None:
                kode = session.prompt(message=[("class:prompt", ">>> ")])
            else:
                kode = readline_input()
        except KeyboardInterrupt:
            print(f"{YELLOW}^C{RESET}")
            continue
        except EOFError:
            print()
            break

        bersih = kode.strip()
        if not bersih:
            continue
        if bersih in (".keluar", ".k"):
            break

        try:
            hasil = run_one(bersih)
            if hasil is not None:
                print(fmt_val(hasil))
        except Exception as e:
            print(f"{RED}{e}{RESET}", file=sys.stderr)

    return 0
