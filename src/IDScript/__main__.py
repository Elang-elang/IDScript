import click
import typing
import time
import threading
from pathlib import Path
from .interpreter import Compile


class Running:
    def __init__(self, file: Path) -> None:
        self.file = file
        self.is_loading = lambda: True

    def __loading_event__(self) -> None:
        loading_token = [
            "|",
            "/",
            "—",
            "\\",
            "|",
            "/",
            "—",
            "\\",
        ]
        
        print("\nloading: ", end="", flush=True)
        while self.is_loading():
            for token in loading_token:
                if self.is_loading():
                    print(token, end="", flush=True)
                
                    time.sleep(0.1)
                    print("\b", end="", flush=True)

        
    def __main_event__(self) -> Compile:
        compiler = Compile(
            file_path = str(self.file),
            code      = self.file.read_text(encoding="utf-8"),
            module    = False
        )
        
        return compiler

    
    def run(self) -> None:
        loading = threading.Thread(target=self.__loading_event__)
        print(f'\033[36m{"="*20 + " \033[33mProgram " + "\033[36m" + "="*20}\033[0m', flush=True)
        
        loading.start()
        try:
            compiler = self.__main_event__()

            self.is_loading = lambda: False
            print("\b"*(len("loading: ") + 1), end="", flush=True)

            compiler.run()
            compiler.run_func('utama')
            
        except NameError as e:
            print(e)
            if "Nama yang tak terdefinisi 'utama'" in str(e):
                print(f'\033[31mFungsi utama tidak terdifinisi\003[0m')

        except:
            raise
            
        finally:
            if self.is_loading():
                self.is_loading = lambda: False
                print("\b", end="", flush=True)
            print("\n")
            print(f'\033[36m{"="*(40+len(" Program "))}\033[0m', flush=True)
>>>>>>> 3bedd79 (Update from Alternative and the new update)


@click.command(
    name="idscript",
<<<<<<< HEAD
    cls=IDScriptCommand,
    context_settings={"help_option_names": ["-h", "--help"]},
    help=(
        "Run IDScript source with the normal interpreter, or compile it to "
        "official VM module/bytecode artifacts."
    ),
=======
    help="IDScript Cli merupakan command untuk IDScript"
>>>>>>> 3bedd79 (Update from Alternative and the new update)
)
@click.argument(
    "file",
    required=False,
    default=None,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
<<<<<<< HEAD
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
def main(file: Path | None, output_file: Path | None, mode: Mode | None, main_name: str) -> None:
    """Public CLI for the ``idscript`` console command."""
    if file is None:
        from IDScript.IDSRepl import main as repl_main
        sys.exit(repl_main())

    file = file.resolve()

    try:
        if mode is None:
            if output_file is not None:
                raise click.UsageError("OUTPUT_FILE hanya dipakai bersama -m, -c, atau --both.")
            if file.suffix in {".idsm", ".idsc"}:
                _run_file_with_progress(
                    f"Menjalankan bytecode {file.name}",
                    lambda: _run_vm_bytecode(file, main_name),
                )
            elif file.suffix == ".idbc":
                raise click.UsageError("Format .idbc sudah tidak didukung. compile ulang source .ids.")
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
=======
def main(file: Path | None) -> None:
    if file is None:
        raise FileNotFoundError(f'File tidak ditemukan')

    event = Running(file)
    event.run()
>>>>>>> 3bedd79 (Update from Alternative and the new update)
