from pathlib import Path
import sys

from click.testing import CliRunner

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from IDScript import __version__
from IDScript.__main__ import main


def test_cli_runs_interpreter_without_compile_outputs(tmp_path):
    source = tmp_path / "main.ids"
    source.write_text(
        """
        dari "Konsol.idsm" impor { publik println };

        fungsi utama(): Angka {
            println("jalan");
            kembalikan 0;
        }
        """,
        encoding="utf-8",
    )

    result = CliRunner().invoke(main, [str(source)])

    assert result.exit_code == 0
    assert result.output == "jalan\n"
    assert not source.with_suffix(".idsm").exists()
    assert not source.with_suffix(".idsc").exists()


def test_cli_writes_module_output(tmp_path):
    source = tmp_path / "main.ids"
    output = tmp_path / "program"
    source.write_text("fungsi utama(): Angka { kembalikan 0; }", encoding="utf-8")

    result = CliRunner().invoke(main, [str(source), "-m", str(output)])

    assert result.exit_code == 0
    assert output.with_suffix(".idsm").read_bytes().startswith(b"IDSM1\n")
    assert "IDScript module ditulis:" in result.output


def test_cli_writes_bytecode_output_without_module_side_effect(tmp_path):
    source = tmp_path / "main.ids"
    output = tmp_path / "program"
    source.write_text("fungsi utama(): Angka { kembalikan 0; }", encoding="utf-8")

    result = CliRunner().invoke(main, [str(source), "-c", str(output)])

    assert result.exit_code == 0
    assert output.with_suffix(".idsc").read_bytes().startswith(b"IDSC1\n")
    assert not output.with_suffix(".idsm").exists()
    assert not source.with_suffix(".idsm").exists()
    assert "IDScript bytecode ditulis:" in result.output


def test_cli_writes_both_outputs(tmp_path):
    source = tmp_path / "main.ids"
    output = tmp_path / "program"
    source.write_text("fungsi utama(): Angka { kembalikan 0; }", encoding="utf-8")

    result = CliRunner().invoke(main, [str(source), "--both", str(output)])

    assert result.exit_code == 0
    assert output.with_suffix(".idsm").read_bytes().startswith(b"IDSM1\n")
    assert output.with_suffix(".idsc").read_bytes().startswith(b"IDSC1\n")
    assert "IDScript module ditulis:" in result.output
    assert "IDScript bytecode ditulis:" in result.output


def test_cli_compile_mode_requires_output_file(tmp_path):
    source = tmp_path / "main.ids"
    source.write_text("fungsi utama(): Angka { kembalikan 0; }", encoding="utf-8")

    result = CliRunner().invoke(main, [str(source), "-c"])

    assert result.exit_code != 0
    assert "OUTPUT_FILE wajib diisi" in result.output


def test_cli_reports_version():
    result = CliRunner().invoke(main, ["--version"])

    assert result.exit_code == 0
    assert f"idscript, version {__version__}" in result.output


def test_cli_reports_colored_help():
    result = CliRunner().invoke(main, ["--help"], color=True)

    assert result.exit_code == 0
    assert "idscript" in result.output
    assert "--version" in result.output
    assert "\x1b[" in result.output


def test_cli_reports_colored_idscript_syntax_error(tmp_path):
    source = tmp_path / "bad.ids"
    source.write_text(
        """fungsi utama(): Angka {
    var awal: Angka = 1;
    var nilai: Angka = 2
    kembalikan nilai;
    println("selesai");
}
""",
        encoding="utf-8",
    )

    result = CliRunner().invoke(main, [str(source)], color=True)

    assert result.exit_code == 1
    assert "kesalahan sintaks" in result.output
    assert "bad.ids:4:" in result.output
    assert "awal" in result.output
    assert "println" in result.output
    assert "\x1b[" in result.output
