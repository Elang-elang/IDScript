from __future__ import annotations

import importlib
import re
import sys

import pytest

from IDScript.compile.Compiler import FunctionCode, ModuleCode, VM
from IDScript.exceptions import IDSError


def _import_tmp_module(tmp_path, source: str):
    module_path = tmp_path / "native_maker_mod.py"
    module_path.write_text(source)
    sys.path.insert(0, str(tmp_path))
    try:
        sys.modules.pop("native_maker_mod", None)
        return importlib.import_module("native_maker_mod")
    finally:
        sys.path.remove(str(tmp_path))


def test_idsfunction_writes_idsm_and_vm_resolves_native_callable(tmp_path):
    native = _import_tmp_module(
        tmp_path,
        """
from IDScript.maker import IDSFunction, IDSModule

@IDSFunction(name="utama", declare="public", arguments={}, annotation=int)
def utama():
    return 7

mod = IDSModule("native_func")
mod.add(utama)
""",
    )

    output = native.mod.write(tmp_path / "native_func.idsm")
    module = ModuleCode.from_bytes(output.read_bytes())

    assert module.native_symbols
    assert VM(module).run() == 7


def test_idsfunction_wraps_non_basic_python_return_values():
    from IDScript.maker import IDSFunction, IDSPyValue

    class Foreign:
        value = 3

        def __repr__(self):
            return "Foreign(value=3)"

    @IDSFunction(name="make_foreign", arguments={}, annotation=object)
    def make_foreign():
        return Foreign()

    @IDSFunction(name="make_list", arguments={}, annotation=list)
    def make_list():
        return [1, 2]

    result = make_foreign()

    assert isinstance(result, IDSPyValue)
    assert repr(result) == "<IDSPyValue<Foreign(value=3)>>"
    assert result.isiAsli.value == 3
    assert make_list() == [1, 2]


def test_vm_wraps_non_basic_native_return_values(tmp_path):
    from IDScript.maker import IDSPyValue

    native = _import_tmp_module(
        tmp_path,
        """
from IDScript.maker import IDSFunction, IDSModule

class Foreign:
    value = 5

    def __repr__(self):
        return "Foreign(value=5)"

    def __iter__(self):
        return iter([1, 2])

    def inc(self):
        return self.value + 1

@IDSFunction(name="utama", declare="public", arguments={}, annotation=object)
def utama():
    return Foreign()

mod = IDSModule("native_py_value")
mod.add(utama)
""",
    )

    result = VM(native.mod.build()).run()

    assert isinstance(result, IDSPyValue)
    assert repr(result) == "<IDSPyValue<Foreign(value=5)>>"
    assert result.isiAsli.value == 5
    assert list(result) == [1, 2]
    assert result.inc() == 6


def test_vm_isi_asli_attribute_returns_raw_python_value(tmp_path):
    from IDScript.maker import IDSPyValue

    native = _import_tmp_module(
        tmp_path,
        """
from IDScript.maker import IDSFunction, IDSModule

class Foreign:
    def __repr__(self):
        return "Foreign(raw)"

@IDSFunction(name="buat", declare="public", arguments={}, annotation=object)
def buat():
    return Foreign()

mod = IDSModule("native_py_value_raw")
mod.add(buat)
""",
    )
    module = native.mod.build()
    module.functions["utama"] = FunctionCode(
        name="utama",
        args=[],
        code=[
            ["LOAD_NAME", "buat"],
            ["CALL_FUNCTION", 0],
            ["LOAD_ATTR", "isiAsli"],
            ["RETURN_VALUE"],
        ],
    )

    result = VM(module).run()

    assert not isinstance(result, IDSPyValue)
    assert repr(result) == "Foreign(raw)"


def test_native_symbols_survive_idsc_roundtrip(tmp_path):
    native = _import_tmp_module(
        tmp_path,
        """
from IDScript.maker import IDSFunction, IDSModule

@IDSFunction(name="utama", declare="public", arguments={}, annotation=int)
def utama():
    return 11

mod = IDSModule("native_compiled")
mod.add(utama)
""",
    )

    _, compiled = native.mod.write(tmp_path / "native_compiled.idsm", both=True)
    module = ModuleCode.from_bytes(compiled.read_bytes())

    assert module.native_symbols
    assert VM(module).run() == 11


def test_idsclass_builds_struct_and_decorated_method_bridge(tmp_path):
    native = _import_tmp_module(
        tmp_path,
        """
from IDScript.maker import IDSClass, IDSMethod, IDSModule

@IDSClass(name="Orang", declare="public", properties={"nama": ("public", str)})
class Orang:
    @IDSMethod(name="sapa", declare="public", arguments={"ini": "Orang"}, annotation=str)
    def sapa(ini):
        return f"Halo {ini.nama}"

    @IDSMethod(name="jenis", declare="public", arguments={}, annotation=str, static=True)
    def jenis():
        return "manusia"

mod = IDSModule("native_class")
mod.add(Orang)
""",
    )
    module = native.mod.build()
    module.functions["utama"] = FunctionCode(
        name="utama",
        args=[],
        code=[
            ["LOAD_NAME", "Orang"],
            ["LOAD_CONST", "nama"],
            ["LOAD_CONST", "Budi"],
            ["BUILD_STRUCT_INSTANCE", 1],
            ["LOAD_ATTR", "sapa"],
            ["CALL_FUNCTION", 0],
            ["RETURN_VALUE"],
        ],
    )
    loaded = ModuleCode.from_bytes(module.to_module_bytes())

    assert VM(loaded).run() == "Halo Budi"

    module.functions["utama"] = FunctionCode(
        name="utama",
        args=[],
        code=[
            ["LOAD_NAME", "Orang"],
            ["LOAD_ATTR", "jenis"],
            ["CALL_FUNCTION", 0],
            ["RETURN_VALUE"],
        ],
    )

    assert VM(ModuleCode.from_bytes(module.to_module_bytes())).run() == "manusia"

    module.functions["utama"] = FunctionCode(
        name="utama",
        args=[],
        code=[
            ["LOAD_NAME", "Orang"],
            ["LOAD_CONST", "nama"],
            ["LOAD_CONST", "Ani"],
            ["BUILD_STRUCT_INSTANCE", 1],
            ["LOAD_ATTR", "jenis"],
            ["CALL_FUNCTION", 0],
            ["RETURN_VALUE"],
        ],
    )

    assert VM(ModuleCode.from_bytes(module.to_module_bytes())).run() == "manusia"


def test_idstrait_and_module_declare_typedef_are_exported(tmp_path):
    native = _import_tmp_module(
        tmp_path,
        """
from IDScript.maker import IDSMethod, IDSModule, IDSTrait

@IDSTrait(name="Bernama", declare="public")
class Bernama:
    @IDSMethod(name="sapa", declare="public", arguments={"ini": object}, annotation=str)
    def sapa(ini):
        pass

    @IDSMethod(name="jenis", declare="public", arguments={}, annotation=str, static=True)
    def jenis():
        pass

mod = IDSModule("native_trait")
mod.add(Bernama)
mod.declare("versi", str, "1.0", declare="public")
mod.typedef("ID", int, declare="public")
""",
    )
    exports = VM(native.mod.build()).exports()

    assert exports["Bernama"]["kind"] == "trait"
    assert any(method["name"] == "jenis" and method["static"] for method in exports["Bernama"]["methods"])
    assert exports["versi"] == "1.0"
    assert exports["ID"].name == "ID"


def test_module_declare_can_export_native_python_module(tmp_path):
    from IDScript.maker import IDSModule

    mod = IDSModule("native_regex")
    mod.declare("regex", object, re, declare="public")
    output = mod.write(tmp_path / "native_regex.idsm")
    module = ModuleCode.from_bytes(output.read_bytes())
    exports = VM(module).exports()

    assert exports["regex"].__name__ == "re"
    assert exports["regex"].match("a+", "aaa").group(0) == "aaa"


def test_maker_unknown_options_raise_idserror_with_english_detail():
    from IDScript.maker import IDSFunction, IDSModule, IDSStruct

    with pytest.raises(IDSError, match=r"IDSFunction option\(s\) 'what' are not supported"):
        IDSFunction(what="error")

    with pytest.raises(IDSError, match="Valid options are: declare, name, properties, extend|Valid options are: declare, extend, name, properties"):
        IDSStruct(what="error")

    with pytest.raises(IDSError, match=r"IDSModule option\(s\) 'what' are not supported"):
        IDSModule(name="Bad", what="error")


def test_maker_properties_accept_type_tuple_and_declare_type_forms():
    from IDScript.maker import IDSClass, IDSStruct

    @IDSStruct(
        name="Data",
        properties={
            "nama": str,
            "umur": (int,),
            "kode": ("public", str),
        },
    )
    class Data:
        pass

    fields = {field["name"]: field for field in Data.fields()}

    assert fields["nama"] == {"name": "nama", "type": "Teks", "is_priv": True}
    assert fields["umur"] == {"name": "umur", "type": "Angka", "is_priv": True}
    assert fields["kode"] == {"name": "kode", "type": "Teks", "is_priv": False}

    @IDSClass(name="Orang", properties={"nama": str, "id": ("private", int)})
    class Orang:
        pass

    class_fields = {field["name"]: field for field in Orang.fields()}

    assert class_fields["nama"]["is_priv"] is True
    assert class_fields["id"] == {"name": "id", "type": "Angka", "is_priv": True}


def test_maker_properties_reject_declare_without_type():
    from IDScript.maker import IDSStruct

    with pytest.raises(IDSError, match=r"property 'nama' only declares visibility 'private'"):
        @IDSStruct(name="Bad", properties={"nama": "private"})
        class Bad:
            pass

    with pytest.raises(IDSError, match=r"property 'nama' only declares visibility 'public'"):
        @IDSStruct(name="Bad", properties={"nama": ("public",)})
        class Bad:
            pass


def test_idsmethod_cannot_be_added_as_top_level_function():
    from IDScript.maker import IDSMethod, IDSModule

    @IDSMethod(name="bad", declare="public", arguments={}, annotation=str)
    def bad():
        return "bad"

    with pytest.raises(IDSError, match="IDSMethod cannot be added as a top-level module function"):
        IDSModule("bad_method").add(bad).build()


def test_maker_signature_mismatch_errors_are_idserror():
    from IDScript.maker import IDSFunction

    with pytest.raises(IDSError, match="argument 'value' type mismatch"):
        @IDSFunction(name="bad", arguments={"value": str}, annotation=int)
        def bad(value: int) -> int:
            return value


def test_maker_declare_option_error_is_english_idserror():
    from IDScript.maker import IDSFunction

    with pytest.raises(IDSError, match="Option 'declare' must be either 'private' or 'public'"):
        IDSFunction(name="bad", declare="publik")
