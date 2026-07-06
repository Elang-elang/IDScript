from pathlib import Path
import sys

from IDScript.IDSRepl.colour import BOLD, GREEN, YELLOW, RESET


try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.styles import Style
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.lexers import PygmentsLexer
    _HAS_PT = True
except ImportError:
    try:
        import pip
        pip.main(["install", "prompt_toolkit", "--quiet"])
        from prompt_toolkit import PromptSession
        from prompt_toolkit.history import FileHistory
        from prompt_toolkit.styles import Style
        from prompt_toolkit.key_binding import KeyBindings
        from prompt_toolkit.lexers import PygmentsLexer
        _HAS_PT = True
    except Exception:
        _HAS_PT = False


_pt_style = Style.from_dict({
    "prompt": "ansigreen bold",
    "continuation": "ansiyellow bold",
    "pygments.keyword": "#5b9bd5",
    "pygments.keyword.namespace": "#5b9bd5",
    "pygments.keyword.constant": "#5b9bd5",
    "pygments.name.builtin": "#00e676",
    "pygments.name.function": "#ffffff bold",
    "pygments.name.class": "#ffffff bold",
    "pygments.name.variable": "#ffffff bold",
    "pygments.name.other": "#ff0000",
    "pygments.literal.number": "#ffd700",
    "pygments.literal.number.integer": "#ffd700",
    "pygments.literal.number.float": "#ffd700",
    "pygments.literal.string": "#00cc66",
    "pygments.literal.string.double": "#00cc66",
    "pygments.comment": "#ff4444",
    "pygments.comment.single": "#ff4444",
    "pygments.comment.multiline": "#ff4444",
    "pygments.operator": "#5b9bd5",
    "pygments.punctuation": "#ffffff",
    "pygments.text": "#e0e0e0",
})


def _imbang(kode: str) -> bool:
    n = 0
    for ch in kode:
        if ch in ("{", "[", "(", "<"):
            n += 1
        elif ch in ("}", "]", ")", ">"):
            n -= 1
    return n == 0


def _build_kb():
    kb = KeyBindings()
    @kb.add("enter")
    def _enter(event):
        buf = event.current_buffer
        txt = buf.text
        if not txt.strip():
            buf.validate_and_handle()
        elif _imbang(txt):
            buf.validate_and_handle()
        else:
            buf.insert_text("\n")
    return kb


def make_session(lexer):
    if not _HAS_PT or not sys.stdin.isatty():
        return None
    hist = FileHistory(str(Path.home() / '.idscript_history'))
    kb = _build_kb()
    return PromptSession(
        lexer=PygmentsLexer(lexer),
        history=hist,
        style=_pt_style,
        key_bindings=kb,
        multiline=True,
        wrap_lines=False,
    )


def readline_input() -> str:
    _HAS_RL = False
    try:
        import readline
        _HAS_RL = True
    except ImportError:
        pass

    if _HAS_RL:
        try:
            histfile = Path.home() / '.idscript_history'
            readline.read_history_file(str(histfile))
        except (FileNotFoundError, OSError):
            pass
        readline.set_history_length(1000)

    kode = ""
    prompt = f"{BOLD}{GREEN}>>>{RESET} "
    while True:
        try:
            baris = input(prompt)
        except KeyboardInterrupt:
            raise
        except EOFError:
            raise

        if not baris and not kode:
            return ""
        if not kode:
            kode = baris
        else:
            kode = f"{kode}\n{baris}"

        if _imbang(kode):
            if _HAS_RL:
                try:
                    readline.write_history_file(str(histfile))
                except OSError:
                    pass
            return kode
        prompt = f"{BOLD}{YELLOW}...{RESET} "
