from __future__ import annotations

from pathlib import Path
from typing import Literal

import click

try:
    from .compile import Compile
    from .compile.Compiler import BytecodeCompiler, ModuleCode, VM
except ImportError:  # pragma: no cover - fallback for direct source execution
    from compile import Compile
    from compile.Compiler import BytecodeCompiler, ModuleCode, VM


Mode = Literal["module", "bytecode", "both"]


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


@click.command(
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
def main(file: Path, output_file: Path | None, mode: Mode | None, main_name: str) -> None:
    """Public CLI for the ``idscript`` console command."""
    file = file.resolve()

    if mode is None:
        if output_file is not None:
            raise click.UsageError("OUTPUT_FILE hanya dipakai bersama -m, -c, atau --both.")
        if file.suffix in {".idsm", ".idsc", ".idbc"}:
            _run_vm_bytecode(file, main_name)
        else:
            _run_interpreter(file, main_name)
        return

    if file.suffix != ".ids":
        raise click.UsageError("Mode compile (-m, -c, --both) membutuhkan file source .ids.")
    if output_file is None:
        raise click.UsageError("OUTPUT_FILE wajib diisi saat memakai -m, -c, atau --both.")

    output_file = output_file.resolve()
    module = _compile_source(file)

    if mode == "module":
        output = _with_default_suffix(output_file, ".idsm")
        output.write_bytes(module.to_module_bytes())
        click.echo(f"IDScript module ditulis: {output}")
        return

    if mode == "bytecode":
        output = _with_default_suffix(output_file, ".idsc")
        output.write_bytes(module.to_compiled_bytes())
        click.echo(f"IDScript bytecode ditulis: {output}")
        return

    module_output, bytecode_output = _both_outputs(output_file)
    module_output.write_bytes(module.to_module_bytes())
    bytecode_output.write_bytes(module.to_compiled_bytes())
    click.echo(f"IDScript module ditulis: {module_output}")
    click.echo(f"IDScript bytecode ditulis: {bytecode_output}")


if __name__ == "__main__":
    main()
