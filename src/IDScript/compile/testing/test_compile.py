import io
from pathlib import Path

from lark import Lark
import pytest

from compile import Compile, Compiler, Parse
from compile.diagnostics import IDSError, IDSNameError, IDSRuntimeError, IDSSyntaxError

COMPILE_DIR = Path(__file__).resolve().parent.parent


def parse_code(code: str):
    parser = Lark(
        (COMPILE_DIR.parent / "gramm.lark").read_text(),
        parser="earley",
        ambiguity="resolve",
    )
    return Parse(parser.parse(code))


def test_compile_example_file(capsys, monkeypatch):
    code = (COMPILE_DIR.parent.parent.parent / "Example/main.ids").read_text()
    monkeypatch.setattr("sys.stdin", io.StringIO("15\n10\n"))

    result = Compile(code, "main.ids")
    assert capsys.readouterr().out == ""
    assert result.main() == 1

    assert isinstance(result, Compile)
    output = capsys.readouterr().out
    assert "Saudara Bima, keputusan kerja Anda diproses dengan tegas.\n" in output
    assert "Bima boleh masuk semua pintu.\n" in output
    assert "Status kerja: diterima\n" in output
    assert "Saudari Sari, keputusan kerja Anda diproses dengan penuh perhatian.\n" in output
    assert "Sari harus meminta izin admin, manager, atau owner.\n" in output
    assert "Status kerja: belum diterima\n" in output
    assert "Total diterima: 1\n" in output


def test_declared_function_can_return_value():
    ast = parse_code("fungsi utama(): ?Angka { kembalikan(0); }")
    compiler = Compiler("<test.ids>")

    compiler.Program(ast)
    function = compiler.current_scope.get("utama")

    assert function() == 0


def test_declared_function_argument_is_supported():
    ast = parse_code("fungsi identitas(x: Angka): Angka { kembalikan(x); }")
    compiler = Compiler("<test.ids>")

    compiler.Program(ast)
    function = compiler.current_scope.get("identitas")

    assert function(2) == 2


def test_syntax_error_reports_source_location():
    code = "fungsi utama(: Angka { kembalikan(0); }"

    with pytest.raises(IDSSyntaxError) as err:
        Compile(code, "syntax_error.ids")

    assert isinstance(err.value, IDSError)
    message = str(err.value)
    assert "syntax_error.ids:1:" in message
    assert "kesalahan sintaks" in message
    assert "^" in message


def test_undefined_identifier_raises_ids_name_error():
    result = Compile("fungsi utama(): Angka { kembalikan tidak_ada; }", "name_error.ids")

    with pytest.raises(IDSNameError) as err:
        result.main()

    assert "tidak_ada" in str(err.value)
    assert "name_error.ids:1:" in str(err.value)


def test_runtime_error_reports_source_location():
    code = """fungsi utama(): Angka {
    var nilai: Angka = "salah";
    kembalikan nilai;
}
"""
    result = Compile(code, "runtime_error.ids")

    with pytest.raises(Exception) as err:
        result.main()

    assert "runtime_error.ids:2:" in str(err.value)


def test_cpp_comment_syntax_is_ignored():
    ast = parse_code(
        """
        // komentar satu baris untuk pemula
        fungsi utama(): Angka {
            // komentar di dalam block
            kembalikan(0); // komentar setelah statement
        }
        """
    )
    compiler = Compiler("<test.ids>")

    compiler.Program(ast)
    function = compiler.current_scope.get("utama")

    assert function() == 0


def test_if_elif_else_control_flow():
    ast = parse_code(
        """
        fungsi utama(): Angka {
            var nilai: Angka = 0;
            jika (salah) { nilai = 1; }
            namun jika (benar) { nilai = 2; }
            jika tidak { nilai = 3; }
            kembalikan(nilai);
        }
        """
    )
    compiler = Compiler("<test.ids>")

    compiler.Program(ast)
    function = compiler.current_scope.get("utama")

    assert function() == 2


def test_for_and_while_control_flow():
    ast = parse_code(
        """
        fungsi utama(): Angka {
            var total: Angka = 0;
            untuk (var x dari dalam [1, 2, 3]) {
                total = total + x;
            }
            selama (total < 10) {
                total = total + 1;
            }
            kembalikan(total);
        }
        """
    )
    compiler = Compiler("<test.ids>")

    compiler.Program(ast)
    function = compiler.current_scope.get("utama")

    assert function() == 10


def test_try_catch_else_finally_control_flow():
    ast = parse_code(
        """
        fungsi utama(): Angka {
            var nilai: Angka = 0;
            coba {
                kesalahan(5);
            } tangkap (e) {
                nilai = e;
            } jika tidak {
                nilai = 99;
            } diakhiri {
                nilai = nilai + 1;
            }
            kembalikan(nilai);
        }
        """
    )
    compiler = Compiler("<test.ids>")

    compiler.Program(ast)
    function = compiler.current_scope.get("utama")

    assert function() == 6


def test_switch_case_control_flow_without_guard():
    ast = parse_code(
        """
        fungsi utama(): Angka {
            var nilai: Angka = 0;
            pilah (2) {
                kasus 1:
                    nilai = 1;
                kasus 2:
                    nilai = 2;
                kasus bawaan:
                    nilai = 3;
            }
            kembalikan(nilai);
        }
        """
    )
    compiler = Compiler("<test.ids>")

    compiler.Program(ast)
    function = compiler.current_scope.get("utama")

    assert function() == 2


def test_loop_break_and_continue_control_flow():
    ast = parse_code(
        """
        fungsi utama(): Angka {
            var total: Angka = 0;
            untuk (var x dari dalam [1, 2, 3, 4]) {
                jika (x == 2) { lanjutkan; }
                jika (x == 4) { berhentikan; }
                total = total + x;
            }
            kembalikan(total);
        }
        """
    )
    compiler = Compiler("<test.ids>")

    compiler.Program(ast)
    function = compiler.current_scope.get("utama")

    assert function() == 4


def test_switch_sequence_and_mapping_dots_patterns():
    ast = parse_code(
        """
        fungsi utama(): Angka {
            var total: Angka = 0;
            pilah ([1, 2, 3]) {
                kasus [kepala, ...ekor]:
                    var kedua: Angka = ekor[0];
                    var ketiga: Angka = ekor[1];
                    total = kepala + kedua + ketiga;
            }
            pilah ({"nama": 4, "umur": 5}) {
                kasus {"nama": nilai, ...sisa}:
                    var umur: Angka = sisa["umur"];
                    total = total + nilai + umur;
            }
            kembalikan(total);
        }
        """
    )
    compiler = Compiler("<test.ids>")

    compiler.Program(ast)
    function = compiler.current_scope.get("utama")

    assert function() == 15


def test_switch_struct_dots_pattern():
    ast = parse_code(
        """
        struktur Titik {
            publik x: Angka,
            publik y: Angka,
            publik z: Angka,
        }

        fungsi utama(): Angka {
            final titik: Titik = Titik { x: 1, y: 2, z: 3 };
            var total: Angka = 0;
            pilah (titik) {
                kasus Titik { x = nilai, ...sisa }:
                    var y: Angka = sisa["y"];
                    var z: Angka = sisa["z"];
                    total = nilai + y + z;
                kasus bawaan:
                    total = 99;
            }
            kembalikan(total);
        }
        """
    )
    compiler = Compiler("<test.ids>")

    compiler.Program(ast)
    function = compiler.current_scope.get("utama")

    assert function() == 6


def test_trait_implementation_can_compile_and_run():
    ast = parse_code(
        """
        struktur Orang {
            publik nama: Teks,
        }

        sifat BisaSapa {
            metode sapa(ini: Orang): Teks;
        }

        implementasi BisaSapa untuk Orang {
            publik metode sapa(ini: Orang): Teks {
                kembalikan(ini.nama);
            }
        }

        fungsi jalankan(): Teks {
            final budi: Orang = Orang { nama: "Budi" };
            kembalikan(budi.sapa());
        }
        """
    )
    compiler = Compiler("<test.ids>")

    compiler.Program(ast)
    function = compiler.current_scope.get("jalankan")

    assert function() == "Budi"


def test_trait_implementation_requires_declared_methods():
    ast = parse_code(
        """
        struktur Orang {
            publik nama: Teks,
        }

        sifat BisaSapa {
            metode sapa(ini: Orang): Teks;
        }

        implementasi BisaSapa untuk Orang {
            publik metode nama(ini: Orang): Teks {
                kembalikan(ini.nama);
            }
        }
        """
    )
    compiler = Compiler("<test.ids>")

    with pytest.raises(Exception, match="kekurangan method"):
        compiler.Program(ast)


def test_trait_static_abstract_method_accepts_static_implementation():
    ast = parse_code(
        """
        struktur Orang {
            publik nama: Teks,
        }

        sifat BisaBuat {
            statik metode jenis(): Teks;
        }

        implementasi BisaBuat untuk Orang {
            publik statik metode jenis(): Teks {
                kembalikan "manusia";
            }
        }
        """
    )
    compiler = Compiler("<test.ids>")

    compiler.Program(ast)


def test_trait_static_abstract_method_rejects_instance_implementation():
    ast = parse_code(
        """
        struktur Orang {
            publik nama: Teks,
        }

        sifat BisaBuat {
            statik metode jenis(): Teks;
        }

        implementasi BisaBuat untuk Orang {
            publik metode jenis(ini: Orang): Teks {
                kembalikan ini.nama;
            }
        }
        """
    )
    compiler = Compiler("<test.ids>")

    with pytest.raises(Exception, match="statik"):
        compiler.Program(ast)


def test_structure_extend_can_compile_and_run():
    ast = parse_code(
        """
        struktur Makhluk {
            publik nama: Teks,
        }

        implementasi Makhluk {
            publik metode sapa(ini: Apapun): Teks {
                kembalikan(ini.nama);
            }
        }

        struktur Orang {
            publik umur: Angka,
        } turunan dari Makhluk

        fungsi jalankan(): Teks {
            final budi: Orang = Orang { nama: "Budi", umur: 20 };
            kembalikan(budi.sapa());
        }
        """
    )
    compiler = Compiler("<test.ids>")

    compiler.Program(ast)
    function = compiler.current_scope.get("jalankan")

    assert function() == "Budi"


def test_pointer_referensial_deferensial_and_assignment_runtime():
    ast = parse_code(
        """
        fungsi jalankan(): Angka {
            var nilai: Angka = 7;
            var *ptr: Angka = &nilai;
            *ptr = 12;
            kembalikan nilai + *ptr;
        }
        """
    )
    compiler = Compiler("<test.ids>")

    compiler.Program(ast)
    function = compiler.current_scope.get("jalankan")

    assert function() == 24


def test_pointer_copy_referensial_runtime():
    ast = parse_code(
        """
        fungsi jalankan(): Angka {
            var nilai: Angka = 3;
            var *ptr: Angka = &nilai;
            var *lain: Angka = salin ptr;
            *lain = 9;
            kembalikan *ptr;
        }
        """
    )
    compiler = Compiler("<test.ids>")

    compiler.Program(ast)
    function = compiler.current_scope.get("jalankan")

    assert function() == 9


def test_deferensial_argument_mutates_caller_runtime():
    ast = parse_code(
        """
        fungsi ubah(*nilai: Angka): Angka {
            *nilai = 8;
            kembalikan *nilai;
        }

        fungsi jalankan(): Angka {
            var nilai: Angka = 3;
            ubah(&nilai);
            kembalikan nilai;
        }
        """
    )
    compiler = Compiler("<test.ids>")

    compiler.Program(ast)
    function = compiler.current_scope.get("jalankan")

    assert function() == 8


def test_deferensial_argument_requires_reference_runtime():
    ast = parse_code(
        """
        fungsi ubah(*nilai: Angka): Angka {
            *nilai = 8;
            kembalikan *nilai;
        }

        fungsi jalankan(): Angka {
            var nilai: Angka = 3;
            kembalikan ubah(nilai);
        }
        """
    )
    compiler = Compiler("<test.ids>")

    compiler.Program(ast)
    function = compiler.current_scope.get("jalankan")

    with pytest.raises(IDSRuntimeError, match="Argumen deferensial"):
        function()


def test_root_dots_pattern_is_not_supported():
    ast = parse_code(
        """
        fungsi utama(): Angka {
            var total: Angka = 0;
            pilah ([1, 2]) {
                kasus ...sisa:
                    total = 1;
                kasus bawaan:
                    total = 2;
            }
            kembalikan(total);
        }
        """
    )
    compiler = Compiler("<test.ids>")

    compiler.Program(ast)
    function = compiler.current_scope.get("utama")

    try:
        function()
    except IDSRuntimeError as err:
        assert "Pola bongkar" in str(err)
    else:
        raise AssertionError("root MatchDots should raise IDSRuntimeError")


def test_public_module_import_works(tmp_path):
    module_a = tmp_path / "module_a.ids"
    module_b = tmp_path / "module_b.ids"

    module_a.write_text(
        """
        publik KONSTANTA PUB: Angka = 7;
        privat KONSTANTA PRIV: Angka = 9;
        """
    )
    module_b.write_text(
        """
        dari "./module_a.ids" impor { var PUB, konstan PUB sebagai SALIN };
        publik fungsi utama(): Angka {
            kembalikan(PUB + SALIN);
        }
        """
    )

    result = Compile(module_b.read_text(), str(module_b))

    assert result.main() == 14


def test_private_module_symbol_cannot_be_imported(tmp_path):
    module_a = tmp_path / "module_a.ids"
    module_b = tmp_path / "module_b.ids"

    module_a.write_text(
        """
        publik KONSTANTA PUB: Angka = 7;
        privat KONSTANTA PRIV: Angka = 9;
        """
    )
    module_b.write_text(
        """
        dari "./module_a.ids" impor { var PRIV };
        publik fungsi utama(): Angka {
            kembalikan(PRIV);
        }
        """
    )

    with pytest.raises(IDSRuntimeError, match="Nama PRIV tidak pernah didefinisikan"):
        Compile(module_b.read_text(), str(module_b))


def test_private_import_binding_is_not_reexported(tmp_path):
    module_a = tmp_path / "module_a.ids"
    module_b = tmp_path / "module_b.ids"
    module_c = tmp_path / "module_c.ids"

    module_a.write_text(
        """
        publik KONSTANTA PUB: Angka = 7;
        """
    )
    module_b.write_text(
        """
        dari "./module_a.ids" impor { privat var PUB };
        publik fungsi utama(): Angka {
            kembalikan(PUB);
        }
        """
    )
    module_c.write_text(
        """
        dari "./module_b.ids" impor { var PUB };
        publik fungsi utama(): Angka {
            kembalikan(PUB);
        }
        """
    )

    with pytest.raises(IDSRuntimeError, match="Nama PUB tidak pernah didefinisikan"):
        Compile(module_c.read_text(), str(module_c))


def test_typedef_alias_is_supported_at_runtime():
    ast = parse_code(
        """
        tipe ID = Angka
        fungsi utama(): Angka {
            var nilai: ID = 12;
            kembalikan(nilai);
        }
        """
    )
    compiler = Compiler("<test.ids>")

    compiler.Program(ast)
    assert compiler.current_scope.get("utama")() == 12


def test_interface_typed_dict_is_supported_at_runtime():
    ast = parse_code(
        """
        antarmuka User {
            nama: Teks,
            umur: Angka,
        }
        fungsi utama(): Angka {
            var user: User = {nama: "elang", umur: 15};
            kembalikan(user["umur"]);
        }
        """
    )
    compiler = Compiler("<test.ids>")

    compiler.Program(ast)
    assert compiler.current_scope.get("utama")() == 15


def test_enum_variants_and_methods_are_supported_at_runtime():
    ast = parse_code(
        """
        enum Type {
            publik Kosong,
            publik Daftar(daftar<Angka>),
            publik Object { nama: Teks, umur: Angka },
            publik Kode = 7,
        }

        implementasi Type {
            publik metode nama(ini: Apapun): Teks {
                kembalikan ini.variant;
            }
        }

        fungsi utama(): Angka {
            final status_kosong: Apapun = Type.Kosong;
            final daftar: Apapun = Type.Daftar([1, 2, 3]);
            final object: Apapun = Type.Object({nama: "elang", umur: 15});
            final kode: Apapun = Type.Kode;
            jika (status_kosong.nama() == "Kosong" dan daftar[0][1] == 2) {
                kembalikan object.umur + kode.value;
            }
            kembalikan 0;
        }
        """
    )
    compiler = Compiler("<test.ids>")

    compiler.Program(ast)
    assert compiler.current_scope.get("utama")() == 22


def test_info_expression_reports_idscript_runtime_categories():
    ast = parse_code(
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

        fungsi jenis(): Teks {
            var angka: Angka = 1;
            var flag: Boolean = benar;
            final titik: Titik = Titik { x: 1 };
            final status: Apapun = Status.Aktif;
            jika (identifikasi angka != 1) { kembalikan("identifikasi"); }
            jika (info angka != "Angka") { kembalikan(info angka); }
            jika (info flag != "Boolean") { kembalikan(info flag); }
            jika (info titik != "Struktur") { kembalikan(info titik); }
            jika (info Status != "Enum") { kembalikan(info Status); }
            jika (info status != "VarianEnum") { kembalikan(info status); }
            jika (info ID != "Tipe") { kembalikan(info ID); }
            jika (info User != "Antarmuka") { kembalikan(info User); }
            jika (info jenis != "Fungsi") { kembalikan(info jenis); }
            kembalikan("ok");
        }
        """
    )
    compiler = Compiler("<test.ids>")

    compiler.Program(ast)
    assert compiler.current_scope.get("jenis")() == "ok"


def test_global_and_lokal_builtins_are_not_internal_runtime():
    ast = parse_code(
        """
        fungsi utama(): Angka {
            Global("nilai_global", 7);
            Lokal("nilai_lokal", 5);
            kembalikan nilai_global + nilai_lokal;
        }
        """
    )
    compiler = Compiler("<test.ids>")

    compiler.Program(ast)
    with pytest.raises(IDSNameError, match="Global"):
        compiler.current_scope.get("utama")()


def test_runtime_module_exports_with_public_const_without_global_builtin(tmp_path):
    module_a = tmp_path / "module_a.ids"
    module_b = tmp_path / "module_b.ids"
    module_a.write_text(
        """
        publik KONSTANTA NILAI: Angka = 9;
        """
    )
    module_b.write_text(
        """
        dari "./module_a.ids" impor { var NILAI };
        fungsi utama(): Angka {
            kembalikan NILAI;
        }
        """
    )

    result = Compile(module_b.read_text(), str(module_b))

    assert result.main() == 9


def test_runtime_can_use_standalone_daftar_and_kamus_builtins():
    result = Compile(
        '''
        dari "Daftar.ids" impor { publik Daftar, publik adalah_daftar };
        dari "Kamus.ids" impor { publik Kamus, publik adalah_kamus };

        fungsi utama(): Angka {
            final daftar: Apapun = Daftar([1, 2]);
            daftar.masukan(3);

            final kamus: Apapun = Kamus({"a": 1});
            kamus.atur("b", 2);

            jika (bukan adalah_daftar(daftar)) { kembalikan 1; }
            jika (bukan adalah_daftar([1])) { kembalikan 2; }
            jika (adalah_daftar(kamus)) { kembalikan 3; }
            jika (bukan adalah_kamus(kamus)) { kembalikan 4; }
            jika (bukan adalah_kamus({"x": 1})) { kembalikan 5; }
            jika (adalah_kamus(daftar)) { kembalikan 6; }

            kembalikan daftar.ambil(2) + kamus.ambil("b");
        }
        ''',
        "standalone_daftar_kamus_runtime.ids",
    )

    assert result.main() == 5


def test_runtime_can_import_compiled_vm_module(tmp_path):
    from compile.Compiler import compile_bytecode_file

    library = tmp_path / "library.ids"
    main = tmp_path / "main.ids"
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
    bytecode_file = library.with_suffix(".idsc")
    compile_bytecode_file(library, bytecode_file)

    main.write_text(
        """
        dari "./library.idsc" impor { var tambah, var Kode };

        fungsi utama(): Angka {
            kembalikan tambah(8) + Kode.Nilai.value;
        }
        """
    )

    result = Compile(main.read_text(), str(main))

    assert result.main() == 20
