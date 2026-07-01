from __future__ import annotations

import pytest

from IDScript.compile.Compiler import BytecodeCompiler, VM
from IDScript.compile.diagnostics import (
    IDSAttributeError,
    IDSIndexError,
    IDSKeyError,
    IDSMemoryError,
    IDSLoopError,
    IDSModuleError,
    IDSRuntimeError,
    IDSTypeError,
    IDSValueError,
)


def test_runtime_exception_factory_returns_named_errors():
    cases = [
        (TypeError("bad type"), IDSTypeError),
        (ValueError("bad value"), IDSValueError),
        (AttributeError("missing"), IDSAttributeError),
        (IndexError("missing index"), IDSIndexError),
        (KeyError("missing key"), IDSKeyError),
        (ModuleNotFoundError("missing module"), IDSModuleError),
        (MemoryError("full"), IDSMemoryError),
    ]

    for error, expected in cases:
        assert isinstance(IDSRuntimeError.from_exception(error), expected)


def test_vm_compiler_uses_loop_error_for_break_outside_loop():
    with pytest.raises(IDSLoopError, match="berhentikan"):
        BytecodeCompiler().compile_source(
            "fungsi utama(): Angka { berhentikan; kembalikan 0; }",
            "loop_error.ids",
        )


def test_vm_runtime_uses_attribute_error_for_missing_struct_field():
    module = BytecodeCompiler().compile_source(
        """
        struktur Orang { publik nama: Teks }

        fungsi utama(): Angka {
            var orang: Orang = Orang { nama: "Budi" };
            kembalikan orang.umur;
        }
        """,
        "attribute_error.ids",
    )

    with pytest.raises(IDSAttributeError, match="umur"):
        VM(module).run()
