from pathlib import Path
import sys

from IDScript.IDSRepl.colour import BOLD, GREEN, YELLOW, RESET


try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.auto_suggest import AutoSuggest, Suggestion
    from prompt_toolkit.completion import Completer, Completion
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.styles import Style
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.lexers import PygmentsLexer
    _HAS_PT = True
except ImportError:
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
    "pygments.text.whitespace": "#e0e0e0",
})


def _imbang(kode: str) -> bool:
    n = 0
    for ch in kode:
        if ch in ("{", "[", "("):
            n += 1
        elif ch in ("}", "]", ")"):
            n -= 1
    return n == 0


class IDSAutoSuggest(AutoSuggest):
    def __init__(self, completer):
        self._completer = completer

    def get_suggestion(self, buffer, document):
        text = document.text
        ghost = self._completer.ghost_suggestion(text)
        if ghost is not None:
            return Suggestion(ghost)
        return None


class IDSCompleter(Completer):
    def __init__(self, completer):
        self._completer = completer

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        dot = text.rfind('.')
        if dot >= 0 and dot > 0:
            before_dot = text[:dot]
            after_dot = text[dot + 1:]
            results = self._completer.complete_attribute(before_dot, after_dot)
            for name in results:
                yield Completion(name, start_position=-len(after_dot))
            return
        word = self._completer.last_word(text)
        if not word:
            return
        for name in self._completer.complete_prefix(word):
            yield Completion(name, start_position=-len(word))


def _build_kb_with_completer():
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

    @kb.add("tab")
    def _tab(event):
        buf = event.current_buffer
        if buf.suggestion:
            buf.insert_text(buf.suggestion.text)
            buf.suggestion = None
        else:
            buf.complete_next()

    return kb


def make_session(lexer, completer=None):
    if not _HAS_PT or not sys.stdin.isatty():
        return None
    hist = FileHistory(str(Path.home() / '.idscript_history'))
    kb = _build_kb_with_completer()
    kwargs = dict(
        lexer=PygmentsLexer(lexer),
        history=hist,
        style=_pt_style,
        key_bindings=kb,
        multiline=True,
        wrap_lines=False,
    )
    if completer is not None:
        kwargs["auto_suggest"] = IDSAutoSuggest(completer)
        kwargs["completer"] = IDSCompleter(completer)
        kwargs["complete_while_typing"] = False
    return PromptSession(**kwargs)


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
