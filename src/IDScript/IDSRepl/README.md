# IDScript REPL (`IDScript.IDSRepl`)

REPL interaktif untuk bahasa IDScript dengan syntax highlighting via `prompt_toolkit` + Pygments.

## Struktur

| File | Tugas |
|------|-------|
| `ids_repl.py` | Loop utama REPL (`main()`), deteksi expression vs statement (`run_one()`), dispatcher |
| `lexer.py` | `IDScriptLexer` — Pygments `RegexLexer` untuk tokenize IDScript |
| `readline.py` | Input session (`prompt_toolkit` jika TTY, fallback `readline`), style warna, key bindings |
| `execute.py` | Eksekusi kode: `_eval()` untuk expression (bungkus `kembalikan`), `_exec()` untuk full code |
| `colour.py` | ANSI color constants dari `exceptions._ANSI`, `fmt_val()` untuk format nilai hasil |
| `__main__.py` | Entry `python -m IDScript.IDSRepl` |

## Alur

1. User mengetik kode
2. Jika ekspresi (`5 + 3;`, `"halo";`) → `_eval()` → bungkus dlm `fungsi __ids_input__N(): Apapun { kembalikan ... }`
3. Jika statement penuh (`fungsi foo() {}`, `struct Bar {}`) → `_exec()` → kompilasi langsung

## Dependensi

- `prompt_toolkit>=3.0` — input + syntax highlighting
- `Pygments>=2.0` — lexer tokenizer
