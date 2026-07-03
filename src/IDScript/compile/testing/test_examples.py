"""Test all examples in the examples/ directories."""

from pathlib import Path
import io
import sys

import pytest

from IDScript.compile.entrypoint import Compile
from IDScript.compile.Compiler.backend.vm_compiler import BytecodeCompiler
from IDScript.compile.Compiler.runtime.vm import VM


EXAMPLES_DIR = Path(__file__).resolve().parents[4] / "examples"
NATIVE_DIR = EXAMPLES_DIR / "NativeIDS"
COMPILER_EXAMPLES_DIR = (
    Path(__file__).resolve().parents[1] / "Compiler" / "examples"
)
ROOT_EXAMPLE_DIR = Path(__file__).resolve().parents[4] / "Example"


# ---------------------------------------------------------------------------
# Helper: run a .ids file with the runtime Compile (CLI-style)
# ---------------------------------------------------------------------------

def _run_runtime(path: Path, stdin: str = "") -> tuple[int, str]:
    code = path.read_text()
    old_stdin = sys.stdin
    try:
        sys.stdin = io.StringIO(stdin)
        result = Compile(code, str(path))
        out = result.main()
        return out, ""
    except Exception as e:
        return -1, str(e)
    finally:
        sys.stdin = old_stdin


# ---------------------------------------------------------------------------
# Helper: compile+run with the VM (BytecodeCompiler)
# ---------------------------------------------------------------------------

def _run_vm(path: Path) -> tuple[int, str]:
    code = path.read_text()
    try:
        module = BytecodeCompiler().compile_source(code, str(path))
        result = VM(module).run()
        return result if result is not None else 0, ""
    except Exception as e:
        return -1, str(e)


# ---------------------------------------------------------------------------
# Runtime compiler tests (NativeIDS examples)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "file,expected_exit",
    [
        ("generik.ids", 0),
        ("kontrol.ids", 0),
        ("pointer.ids", 0),
        ("struktur.ids", 0),
        ("trait.ids", 0),
    ],
)
def test_native_examples_runtime(file, expected_exit):
    path = NATIVE_DIR / file
    if not path.exists():
        pytest.skip(f"{path} tidak ditemukan")
    exit_code, error = _run_runtime(path)
    assert exit_code == expected_exit, f"{file} gagal: {error}"


# ---------------------------------------------------------------------------
# VM compiler tests (Compiler examples)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "file,expected_exit",
    [
        ("calculator_integer.ids", 96),
    ],
)
def test_compiler_examples_vm(file, expected_exit):
    path = COMPILER_EXAMPLES_DIR / file
    if not path.exists():
        pytest.skip(f"{path} tidak ditemukan")
    exit_code, error = _run_vm(path)
    assert exit_code == expected_exit, f"{file} gagal: {error}"


# ---------------------------------------------------------------------------
# Root example
# ---------------------------------------------------------------------------

def test_root_example(capsys, monkeypatch):
    path = ROOT_EXAMPLE_DIR / "main.ids"
    if not path.exists():
        pytest.skip(f"{path} tidak ditemukan")
    code = path.read_text()
    monkeypatch.setattr("sys.stdin", io.StringIO("15\n10\n"))
    result = Compile(code, str(path))
    assert result.main() == 1


# ---------------------------------------------------------------------------
# IDSPy Maker test (test the Maker API directly from Python)
# ---------------------------------------------------------------------------

def test_idspy_maker_module():
    """Test that the Maker API can create and use a module."""
    from IDScript.maker import IDSFunction, IDSModule
    from IDScript.compile.Compiler.bytecode import ModuleCode

    @IDSFunction(name="salam", declare="public",
                 arguments={"nama": str}, annotation=str)
    def _salam(nama: str) -> str:
        return f"Halo, {nama}!"

    @IDSFunction(name="tambah", declare="public",
                 arguments={"a": int, "b": int}, annotation=int)
    def _tambah(a: int, b: int) -> int:
        return a + b

    module_code: ModuleCode = None

    @IDSModule(name="TestModule")
    def mod(cls):
        cls.add(_salam, _tambah)
        nonlocal module_code
        module_code = cls.build()

    assert module_code is not None
    assert "salam" in module_code.exports
    assert "tambah" in module_code.exports
    assert len(module_code.functions) == 2
