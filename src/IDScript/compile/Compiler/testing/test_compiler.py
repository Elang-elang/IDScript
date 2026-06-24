from pathlib import Path
import pytest
import subprocess
import sys
import time

from compile.Compiler import BytecodeCompiler, FunctionCode, ModuleCode, TOKEN, VM, compile_bytecode_file, run_source_direct


EXAMPLE_DIR = Path(__file__).resolve().parents[1] / "examples"
IDSCRIPT_DIR = Path(__file__).resolve().parents[3]


def test_token_registry_can_encode_and_decode_opcode():
    encoded = TOKEN.encode_instruction(["LOAD_CONST", 7])

    assert encoded == [1, 7]
    assert TOKEN.decode_instruction(encoded) == ["LOAD_CONST", 7]
    assert TOKEN.encode_instruction(["CONST", 7]) == [1, 7]


def test_compiler_emits_explicit_python_style_opcodes():
    module = BytecodeCompiler().compile_source(
        """
        fungsi utama(): Angka {
            var pi: Angka = 1;
            jika (bukan pi) { kembalikan 0; }
            kembalikan pi;
        }
        """,
        "opcodes.ids",
    )

    code = module.functions["utama"].code

    assert code[:4] == [
        ["LOAD_CONST", 1],
        ["STORE_FAST", "pi"],
        ["LOAD_NAME", "pi"],
        ["TO_BOOL"],
    ]
    assert code[4][0] == "POP_JUMP_IF_TRUE"
    assert ["RETURN_VALUE"] in [[inst[0]] for inst in code]


def test_vm_still_accepts_legacy_opcode_names():
    module = ModuleCode(
        name="legacy",
        path="legacy.ids",
        functions={
            "utama": FunctionCode(
                name="utama",
                args=[],
                code=[
                    ["CONST", 7],
                    ["RETURN"],
                ],
            )
        },
    )

    assert VM(module).run() == 7


def test_official_compiler_runs_source_direct(capsys):
    result = run_source_direct(EXAMPLE_DIR / "main.ids")

    assert result == 25
    assert capsys.readouterr().out == "elang\n25\n"


def test_official_compiler_writes_idsm_and_idsc(tmp_path, capsys):
    source = tmp_path / "main.ids"
    math = tmp_path / "math.ids"
    source.write_text((EXAMPLE_DIR / "main.ids").read_text())
    math.write_text((EXAMPLE_DIR / "math.ids").read_text())
    module_file = tmp_path / "main.idsm"
    bytecode_file = tmp_path / "main.idsc"

    compile_bytecode_file(source, bytecode_file, module_file)

    assert module_file.read_bytes().startswith(b"IDSM1\n")
    assert bytecode_file.read_bytes().startswith(b"IDSC1\n")
    assert VM(ModuleCode.from_bytes(bytecode_file.read_bytes())).run() == 25
    assert capsys.readouterr().out == "elang\n25\n"


def test_official_compiler_cli_default_pipeline(tmp_path):
    source = tmp_path / "main.ids"
    math = tmp_path / "math.ids"
    source.write_text((EXAMPLE_DIR / "main.ids").read_text())
    math.write_text((EXAMPLE_DIR / "math.ids").read_text())

    result = subprocess.run(
        [sys.executable, "-m", "compile.Compiler", str(source)],
        cwd=IDSCRIPT_DIR,
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout == "elang\n25\n"
    assert source.with_suffix(".idsm").read_bytes().startswith(b"IDSM1\n")
    assert source.with_suffix(".idsc").read_bytes().startswith(b"IDSC1\n")


def test_bytecode_compiler_can_compile_ast_from_memory():
    module = BytecodeCompiler().compile_source(
        """
        fungsi utama(): Angka {
            kembalikan 2 + 3;
        }
        """,
        "inline.ids",
    )

    assert VM(module).run() == 5


def test_calculator_examples_compile_to_bytecode_and_run_fast(tmp_path, capsys):
    cases = [
        ("calculator_integer.ids", 96, "96\n"),
        ("calculator_decimal.ids", 15.56636, "15.56636\n"),
        ("calculator_calculus.ids", 47.25, "47.25\n"),
    ]

    for filename, expected, expected_output in cases:
        source = tmp_path / filename
        source.write_text((EXAMPLE_DIR / filename).read_text())
        module_file = source.with_suffix(".idsm")
        bytecode_file = source.with_suffix(".idsc")

        compile_bytecode_file(source, bytecode_file, module_file)
        assert module_file.read_bytes().startswith(b"IDSM1\n")
        assert bytecode_file.read_bytes().startswith(b"IDSC1\n")

        module = ModuleCode.from_bytes(bytecode_file.read_bytes())
        start = time.perf_counter()
        result = VM(module).run()
        elapsed = time.perf_counter() - start

        if isinstance(expected, float):
            assert abs(result - expected) < 0.00001
        else:
            assert result == expected
        assert elapsed < 1.0
        assert capsys.readouterr().out == expected_output


def test_vm_supports_typedef_interface_and_enum(tmp_path):
    source = tmp_path / "new_features.ids"
    source.write_text(
        """
        tipe ID = Angka

        antarmuka User {
            nama: Teks,
            umur: Angka,
        }

        enum Type {
            publik Kosong,
            publik Daftar(daftar[Angka]),
            publik Object { nama: Teks, umur: Angka },
            publik Kode = 7,
        }

        implementasi Type {
            publik metode nama(ini: Apapun): Teks {
                kembalikan ini.variant;
            }
        }

        fungsi utama(): Angka {
            var id: ID = 5;
            var user: User = {nama: "elang", umur: 15};
            final status_kosong: Apapun = Type.Kosong;
            final daftar: Apapun = Type.Daftar([1, 2, 3]);
            final object: Apapun = Type.Object({nama: user["nama"], umur: user["umur"]});
            final kode: Apapun = Type.Kode;
            jika (status_kosong.nama() == "Kosong" dan daftar[0][1] == 2) {
                var hasil: Angka = id;
                hasil = hasil + object.umur;
                hasil = hasil + kode.value;
                kembalikan hasil;
            }
            kembalikan 0;
        }
        """
    )
    module_file = source.with_suffix(".idsm")
    bytecode_file = source.with_suffix(".idsc")

    compile_bytecode_file(source, bytecode_file, module_file)

    assert module_file.read_bytes().startswith(b"IDSM1\n")
    assert bytecode_file.read_bytes().startswith(b"IDSC1\n")
    assert VM(ModuleCode.from_bytes(bytecode_file.read_bytes())).run() == 27


def test_vm_supports_info_expression():
    module = BytecodeCompiler().compile_source(
        """
        tipe ID = Angka

        antarmuka User {
            nama: Teks,
            umur: Angka,
        }

        struktur Titik {
            publik x: Angka,
        }

        enum Status {
            publik Aktif,
        }

        fungsi utama(): Angka {
            var angka: Angka = 1;
            var flag: Boolean = benar;
            final titik: Titik = Titik { x: 1 };
            final status: Apapun = Status.Aktif;
            jika (identifikasi angka != 1) { kembalikan 0; }
            jika (info angka != "Angka") { kembalikan 0; }
            jika (info flag != "Boolean") { kembalikan 0; }
            jika (info titik != "Struktur") { kembalikan 0; }
            jika (info Status != "Enum") { kembalikan 0; }
            jika (info status != "VarianEnum") { kembalikan 0; }
            jika (info ID != "Tipe") { kembalikan 0; }
            jika (info User != "Antarmuka") { kembalikan 0; }
            jika (info utama != "Fungsi") { kembalikan 0; }
            kembalikan 1;
        }
        """,
        "info.ids",
    )

    assert VM(module).run() == 1


def test_vm_allows_private_enum_variant_in_root_file():
    module = BytecodeCompiler().compile_source(
        """
        enum Status {
            privat Rahasia,
        }

        fungsi utama(): Angka {
            final status: Apapun = Status.Rahasia;
            jika (status.variant == "Rahasia") { kembalikan 1; }
            kembalikan 0;
        }
        """,
        "root_private_enum.ids",
    )

    assert VM(module).run() == 1


def test_vm_rejects_private_enum_variant_from_module(tmp_path):
    source = tmp_path / "main.ids"
    status = tmp_path / "status.ids"
    status.write_text(
        """
        publik enum Status {
            privat Rahasia,
        }
        """
    )
    source.write_text(
        """
        dari "./status.ids" impor { var Status };

        fungsi utama(): Angka {
            final status: Apapun = Status.Rahasia;
            kembalikan 1;
        }
        """
    )

    module = BytecodeCompiler().compile_file(source)

    with pytest.raises(AttributeError):
        VM(module).run()


def test_vm_supports_global_and_lokal_builtins():
    module = BytecodeCompiler().compile_source(
        """
        fungsi utama(): Angka {
            Global("nilai_global", 7);
            Lokal("nilai_lokal", 5);
            kembalikan nilai_global + nilai_lokal;
        }
        """,
        "scope_builtins.ids",
    )

    assert VM(module).run() == 12


def test_vm_global_builtin_can_export_from_module(tmp_path):
    source = tmp_path / "main.ids"
    module_file = tmp_path / "scope.ids"
    module_file.write_text(
        """
        publik KONSTANTA _INIT: Kosong = Global("NILAI", 9, salah);
        """
    )
    source.write_text(
        """
        dari "./scope.ids" impor { var NILAI };

        fungsi utama(): Angka {
            kembalikan NILAI;
        }
        """
    )

    module = BytecodeCompiler().compile_file(source)

    assert VM(module).run() == 9


def test_vm_can_use_ids_builtin_atribut_and_iterasi():
    module = BytecodeCompiler().compile_source(
        '''
        dari "atribut.ids" impor { var punya_attr };
        dari "iterasi.ids" impor { var panjang, var jangkauan, var Daftar };

        fungsi utama(): Angka {
            final data: Apapun = [1, 2, 3];
            jika (bukan punya_attr(data, "__len__")) { kembalikan 1; }
            final bungkus: Apapun = Daftar(data);
            bungkus.masukan(4);
            final r: Apapun = jangkauan([3]);
            kembalikan panjang(data) + panjang(r);
        }
        ''',
        "builtin_ids_smoke.ids",
    )

    assert VM(module).run() == 7


def test_vm_can_import_compiled_idsm_and_idsc_modules(tmp_path):
    library = tmp_path / "library.ids"
    library.write_text(
        """
        publik enum Kode {
            publik Nilai = 7,
        }

        publik fungsi tambah(x: Angka): Angka {
            kembalikan x + 5;
        }
        """
    )
    module_file = library.with_suffix(".idsm")
    bytecode_file = library.with_suffix(".idsc")
    compile_bytecode_file(library, bytecode_file, module_file)

    for compiled_import in (module_file, bytecode_file):
        source = tmp_path / f"main_{compiled_import.suffix[1:]}.ids"
        source.write_text(
            f'''
            dari "./{compiled_import.name}" impor {{ var tambah, var Kode }};

            fungsi utama(): Angka {{
                kembalikan tambah(8) + Kode.Nilai.value;
            }}
            '''
        )

        module = BytecodeCompiler().compile_file(source)

        assert VM(module).run() == 20
