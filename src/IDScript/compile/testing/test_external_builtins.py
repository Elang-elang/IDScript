from __future__ import annotations

import pytest

from IDScript.compile import Compile
from IDScript.compile.Compiler import BytecodeCompiler, VM
from IDScript.compile.diagnostics import IDSNameError, IDSRuntimeError
from IDScript.maker import IDSPyValue


def test_internal_builtins_only_include_core_types_and_constants():
    result = Compile(
        """
        fungsi utama(): Angka {
            jika (benar dan bukan salah dan kosong == kosong) {
                final nilai: Apapun = "ok";
                final angka: Angka = 1;
                final teks: Teks = "x";
                final pecahan: Float = 1.5;
                final flag: Boolean = benar;
                kembalikan angka;
            }
            kembalikan 0;
        }
        """,
        "core_builtins.ids",
    )

    assert result.main() == 1


def test_console_builtin_must_be_imported_explicitly(capsys):
    missing = Compile(
        'fungsi utama(): Angka { println("x"); kembalikan 0; }',
        "missing_console.ids",
    )

    with pytest.raises(IDSNameError, match="println"):
        missing.main()

    result = Compile(
        """
        dari "Konsol.idsm" impor { publik println };

        fungsi utama(): Angka {
            println("jalan");
            kembalikan 0;
        }
        """,
        "console_import.ids",
    )

    assert result.main() == 0
    assert capsys.readouterr().out == "jalan\n"


def test_global_lokal_and_objek_are_not_internal():
    for source, expected in [
        ('fungsi utama(): Angka { Global("x", 1); kembalikan 0; }', "Global"),
        ('fungsi utama(): Angka { Lokal("x", 1); kembalikan 0; }', "Lokal"),
    ]:
        result = Compile(source, f"missing_{expected}.ids")
        with pytest.raises(IDSRuntimeError, match=expected):
            result.main()

    result = Compile('fungsi utama(): Angka { var x: OBJEK = kosong; kembalikan 0; }', "missing_OBJEK.ids")
    with pytest.raises(IDSRuntimeError, match="OBJEK"):
        result.main()


def test_vm_can_import_external_python_wrapped_builtins(capsys):
    module = BytecodeCompiler().compile_source(
        """
        dari "Konsol.idsm" impor { publik println };
        dari "Regex.idsm" impor { publik cocok };
        dari "Daftar.ids" impor { publik Daftar, publik adalah_daftar };
        dari "Kamus.ids" impor { publik Kamus, publik adalah_kamus };

        fungsi utama(): Angka {
            println("vm");
            final daftar: Apapun = Daftar([1, 2]);
            daftar.masukan(3);
            final kamus: Apapun = Kamus({"x": 4});
            jika (bukan cocok("v+", "vm")) { kembalikan 1; }
            jika (bukan adalah_daftar(daftar)) { kembalikan 2; }
            jika (bukan adalah_kamus(kamus)) { kembalikan 3; }
            kembalikan daftar.ambil(2) + kamus.ambil("x");
        }
        """,
        "external_vm.ids",
    )

    assert VM(module).run() == 7
    assert capsys.readouterr().out == "vm\n"


def test_python_builtin_namespace_import_and_async_helpers():
    module = BytecodeCompiler().compile_source(
        r'''
        dari "Python.idsm" impor {
            publik evaluasi,
            publik jalankan,
            publik impor,
            publik ambil,
            publik atur,
            publik punya,
            publik hapus,
            publik bersihkan,
            publik pengingatan,
            publik penungguan,
        };

        fungsi utama(): Angka {
            bersihkan();
            atur("x", 4);
            jika (bukan punya("x")) { kembalikan 1; }
            jika (ambil("x") != 4) { kembalikan 2; }
            hapus("x");
            jika (punya("x")) { kembalikan 3; }
            final math: Apapun = impor("math");
            jika (math.sqrt(9) != 3.0) { kembalikan 4; }
            final nilai: Apapun = evaluasi("lambda: asyncio.sleep(0, result=9)");
            final janji: Apapun = pengingatan(nilai, []);
            kembalikan evaluasi("1 + 2") + penungguan(janji);
        }
        ''',
        "python_builtin.ids",
    )

    assert VM(module).run() == 12


def test_regex_builtin_returns_match_object_and_text_helpers():
    module = BytecodeCompiler().compile_source(
        r'''
        dari "Regex.idsm" impor {
            publik cari,
            publik teks_cari,
            publik grup,
            publik grup_dict,
            publik escape,
        };

        fungsi utama(): Angka {
            final match: Apapun = cari("a(?P<nama>b)", "zab");
            jika (teks_cari("a.", "zab") != "ab") { kembalikan 1; }
            jika (grup(match, 0) != "ab") { kembalikan 2; }
            jika (grup(match, "nama") != "b") { kembalikan 3; }
            jika (grup_dict(match)["nama"] != "b") { kembalikan 4; }
            jika (escape("a.b") != "a\\.b") { kembalikan 5; }
            kembalikan 0;
        }
        ''',
        "regex_builtin.ids",
    )

    assert VM(module).run() == 0


def test_permintaan_builtin_wraps_requests_response(monkeypatch):
    import IDScript.builtins._Permintaan as permintaan

    class FakeResponse:
        status_code = 201
        text = "ok"
        ok = True
        url = "https://contoh.local/"
        headers = {"X-Test": "1"}

        def json(self):
            return {"hasil": 7}

    def fake_get(url, **opsi):
        assert url == "https://contoh.local/"
        assert opsi == {"timeout": 1}
        return FakeResponse()

    monkeypatch.setattr(permintaan.requests, "get", fake_get)

    module = BytecodeCompiler().compile_source(
        r'''
        dari "Permintaan.idsm" impor {
            publik ambil,
            publik teks,
            publik json,
            publik status,
            publik header,
            publik url,
            publik berhasil,
        };

        fungsi utama(): Angka {
            final response: Apapun = ambil("https://contoh.local/", {"timeout": 1});
            jika (status(response) != 201) { kembalikan 1; }
            jika (teks(response) != "ok") { kembalikan 2; }
            jika (json(response)["hasil"] != 7) { kembalikan 3; }
            jika (header(response)["X-Test"] != "1") { kembalikan 4; }
            jika (url(response) != "https://contoh.local/") { kembalikan 5; }
            jika (bukan berhasil(response)) { kembalikan 6; }
            kembalikan 0;
        }
        ''',
        "permintaan_builtin.ids",
    )

    assert VM(module).run() == 0


def test_http_builtin_can_serve_static_route():
    import requests
    from IDScript.builtins._HTTP import _buat_server, _hentikan, _jalankan_thread

    server = _buat_server("127.0.0.1", 0, {"/": "jalan"})
    assert isinstance(server, IDSPyValue)
    raw_server = server.isiAsli
    _jalankan_thread(server)
    try:
        response = requests.get(f"http://127.0.0.1:{raw_server.server_address[1]}/", timeout=3)
        assert response.status_code == 200
        assert response.text == "jalan"
    finally:
        _hentikan(server)
