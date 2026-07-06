"""REPL interaktif IDScript dengan syntax highlighting.

Menyediakan REPL (Read-Eval-Print Loop) untuk bahasa IDScript
dengan dukungan prompt_toolkit (syntax highlighting via Pygments)
dan fallback readline untuk non-TTY.

Pemakaian:
    python -m IDScript.IDSRepl
    # atau dari CLI: idscript (tanpa argumen)
    
Fungsi utama:
    main() -> int  -- Jalankan loop REPL
"""

from IDScript.IDSRepl.ids_repl import main
