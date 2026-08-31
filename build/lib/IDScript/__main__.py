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

@click.command(
    name="idscript",
    help="IDScript Cli merupakan command untuk IDScript"
)
@click.argument(
    "file",
    required=False,
    default=None,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
def main(file: Path | None) -> None:
    if file is None:
        raise FileNotFoundError(f'File tidak ditemukan')

    event = Running(file)
    event.run()
