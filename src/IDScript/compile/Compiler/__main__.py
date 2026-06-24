"""CLI for the official IDScript compiler pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


def _run_bytecode_file(file: Path, main: str) -> None:
    from .bytecode import ModuleCode
    from .runtime import VM

    VM(ModuleCode.from_bytes(file.read_bytes())).run(main)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Official readable IDScript compiler")
    parser.add_argument("file", help=".ids source, .idsm module, atau .idsc bytecode")
    parser.add_argument("--direct", "-D", action="store_true", help="jalankan source langsung di VM tanpa menulis .idsm/.idsc")
    parser.add_argument("--module", "-m", help="tulis IDScript Module ke file .idsm")
    parser.add_argument("--bytecode", "-b", help="tulis IDScript Compiled ke file .idsc")
    parser.add_argument("--no-exec", "-E", action="store_true", help="compile .ids menjadi .idsm dan .idsc tanpa menjalankan")
    parser.add_argument("--run", "-r", default="utama", help="nama fungsi entrypoint")
    args = parser.parse_args(argv)

    file = Path(args.file).resolve()
    if file.suffix in {".idsm", ".idsc", ".idbc"}:
        _run_bytecode_file(file, args.run)
        return 0
    if args.direct:
        from .api import run_source_direct

        run_source_direct(file, args.run)
        return 0
    if args.module:
        from .api import compile_module_file

        compile_module_file(file, Path(args.module).resolve())
        return 0
    if args.bytecode:
        from .api import compile_bytecode_file

        compile_bytecode_file(file, Path(args.bytecode).resolve())
        return 0
    from .api import compile_pipeline

    compile_pipeline(file, args.run, run=not args.no_exec)
    return 0


if __name__ == "__main__":
    sys.exit(main())
