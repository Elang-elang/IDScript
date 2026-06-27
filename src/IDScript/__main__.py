from __future__ import annotations

from contextlib import redirect_stdout
import io
import os
from pathlib import Path
import sys
from typing import Literal

import click

try:
    from . import __version__
    from .exceptions import IDSError
    from .compile import Compile
    from .compile.Compiler import BytecodeCompiler, ModuleCode, VM
except ImportError:  # pragma: no cover - fallback for direct source execution
    from IDScript import __version__
    from IDScript.exceptions import IDSError
    from compile import Compile
    from compile.Compiler import BytecodeCompiler, ModuleCode, VM


Mode = Literal["module", "bytecode", "both"]


class IDScriptCommand(click.Command):
    """Click command with colorful IDScript-oriented help output."""

    def format_usage(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        pieces = [click.style(piece, fg="yellow") for piece in self.collect_usage_pieces(ctx)]
        command = click.style(ctx.command_path, fg="cyan", bold=True)
        formatter.write_usage(command, " ".join(pieces))

    def format_help_text(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        if not self.help:
            return
        with formatter.section(click.style("Deskripsi", fg="cyan", bold=True)):
            formatter.write_text(self.help)

    def format_options(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        rows = []
        for param in self.get_params(ctx):
            record = param.get_help_record(ctx)
            if record is None:
                continue
            options, help_text = record
            colored_options = ", ".join(
                click.style(part, fg="green", bold=part.startswith("--"))
                for part in options.split(", ")
            )
            rows.append((colored_options, help_text))

        if rows:
            with formatter.section(click.style("Opsi", fg="cyan", bold=True)):
                formatter.write_dl(rows)


def _with_default_suffix(path: Path, suffix: str) -> Path:
    if path.suffix:
        return path
    return path.with_suffix(suffix)


def _both_outputs(output: Path) -> tuple[Path, Path]:
    base = output.with_suffix("") if output.suffix in {".idsm", ".idsc"} else output
    return base.with_suffix(".idsm"), base.with_suffix(".idsc")


def _compile_source(file: Path) -> ModuleCode:
    return BytecodeCompiler().compile_file(file)


def _run_interpreter(file: Path, main_name: str) -> None:
    runtime = Compile(file.read_text(encoding="utf-8"), file, False)
    if main_name == "utama":
        runtime.main()
        return
    runtime.run(main_name)


def _run_vm_bytecode(file: Path, main_name: str) -> None:
    VM(ModuleCode.from_bytes(file.read_bytes())).run(main_name)


def _progress_enabled() -> bool:
    if os.environ.get("IDS_NO_PROGRESS") or os.environ.get("NO_COLOR"):
        return False
    return bool(getattr(sys.stderr, "isatty", lambda: False)())


def _run_with_progress[T](label: str, callback) -> T:
    if not _progress_enabled():
        return callback()

    styled_label = click.style(label, fg="cyan", bold=True)
    with click.progressbar(length=1, label=styled_label, file=sys.stderr, color=True) as bar:
        result = callback()
        bar.update(1)
        return result


def _run_file_with_progress(label: str, callback) -> None:
    if not _progress_enabled():
        callback()
        return

    output = io.StringIO()
    _run_with_progress(label, lambda: _capture_stdout(callback, output))
    sys.stderr.write("\n\n")
    sys.stderr.flush()
    sys.stdout.write(output.getvalue())
    sys.stdout.flush()


def _capture_stdout(callback, output: io.StringIO) -> None:
    with redirect_stdout(output):
        callback()


def _success(message: str) -> None:
    click.secho(message, fg="green", bold=True)


def _fail_with_usage_error(error: click.UsageError) -> None:
    prefix = click.style("kesalahan penggunaan:", fg="red", bold=True)
    click.echo(f"{prefix} {error.message}", err=True)
    raise click.exceptions.Exit(2)


def _fail_with_idscript_error(error: IDSError) -> None:
    click.echo(str(error), err=True)
    raise click.exceptions.Exit(1)


@click.command(
    name="idscript",
    cls=IDScriptCommand,
    context_settings={"help_option_names": ["-h", "--help"]},
    help=(
        "Run IDScript source with the normal interpreter, or compile it to "
        "official VM module/bytecode artifacts."
    ),
)
@click.argument(
    "file",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.argument(
    "output_file",
    required=False,
    type=click.Path(dir_okay=False, path_type=Path),
)
@click.option(
    "-m",
    "--module",
    "mode",
    flag_value="module",
    help="Compile source to .idsm module output.",
)
@click.option(
    "-c",
    "--bytecode",
    "mode",
    flag_value="bytecode",
    help="Compile source to .idsc bytecode output.",
)
@click.option(
    "--both",
    "mode",
    flag_value="both",
    help="Compile source to both .idsm and .idsc outputs.",
)
@click.option(
    "--main",
    "main_name",
    default="utama",
    show_default=True,
    help="Entrypoint function when running source or bytecode.",
)
@click.version_option(__version__, "-V", "--version", prog_name="idscript")
def main(file: Path, output_file: Path | None, mode: Mode | None, main_name: str) -> None:
    """Public CLI for the ``idscript`` console command."""
    file = file.resolve()

    try:
        if mode is None:
            if output_file is not None:
                raise click.UsageError("OUTPUT_FILE hanya dipakai bersama -m, -c, atau --both.")
            if file.suffix in {".idsm", ".idsc", ".idbc"}:
                _run_file_with_progress(
                    f"Menjalankan bytecode {file.name}",
                    lambda: _run_vm_bytecode(file, main_name),
                )
            else:
                _run_file_with_progress(
                    f"Menjalankan {file.name}",
                    lambda: _run_interpreter(file, main_name),
                )
            return

        if file.suffix != ".ids":
            raise click.UsageError("Mode compile (-m, -c, --both) membutuhkan file source .ids.")
        if output_file is None:
            raise click.UsageError("OUTPUT_FILE wajib diisi saat memakai -m, -c, atau --both.")

        output_file = output_file.resolve()
        module = _run_with_progress(
            f"Mengkompilasi {file.name}",
            lambda: _compile_source(file),
        )

        if mode == "module":
            output = _with_default_suffix(output_file, ".idsm")
            output.write_bytes(module.to_module_bytes())
            _success(f"IDScript module ditulis: {output}")
            return

        if mode == "bytecode":
            output = _with_default_suffix(output_file, ".idsc")
            output.write_bytes(module.to_compiled_bytes())
            _success(f"IDScript bytecode ditulis: {output}")
            return

        module_output, bytecode_output = _both_outputs(output_file)
        module_output.write_bytes(module.to_module_bytes())
        bytecode_output.write_bytes(module.to_compiled_bytes())
        _success(f"IDScript module ditulis: {module_output}")
        _success(f"IDScript bytecode ditulis: {bytecode_output}")
    except click.UsageError as error:
        _fail_with_usage_error(error)
    except IDSError as error:
        _fail_with_idscript_error(error)


if __name__ == "__main__":
    main()
