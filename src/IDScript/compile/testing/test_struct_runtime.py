import pytest
from typeguard import TypeCheckError
from typing import Any, Callable

from compile.runtime import Structure
from compile.runtime.config import Config
from compile.runtime.structure import Trait


def test_config_tracks_runtime_context_and_file_metadata(tmp_path):
    source = tmp_path / "mod.ids"
    config = Config(source, True)

    assert config.path() == str(source)
    assert config.filepath() == str(source)
    assert config.filename == "mod.ids"
    assert config.is_module()
    assert not config.is_infunc()
    assert not config.is_inloop()

    config.enter_struct("Luar")
    assert config.is_struct_name("Luar")
    assert config.struct_name == "Luar"
    config.enter_struct("Dalam")
    assert config.is_struct_name("Dalam")
    config.leave_struct()
    assert config.is_struct_name("Luar")
    config.leave_struct()

    config.enter_func()
    config.enter_func()
    assert config.is_infunc()
    config.leave_func()
    assert config.is_infunc()
    config.leave_func()
    assert not config.is_infunc()

    config.enter_loop()
    config.enter_loop()
    assert config.is_inloop()
    config.leave_loop()
    assert config.is_inloop()
    config.leave_loop()
    assert not config.is_inloop()


def test_structure_builds_native_python_class():
    config = Config()
    orang = Structure(
        "Orang",
        config,
        {
            "nama": {"type": str},
            "umur": {"type": int, "is_priv": True},
        },
    )
    orang.set_method("inisiasi", lambda ini: None, is_priv=True)
    orang.set_method("sapa", lambda ini: f"Halo {ini.nama}")
    orang.set_method("lihat_umur", lambda ini: ini.umur)

    budi = orang(nama="Budi", umur=20)

    assert type(budi).__name__ == "Orang"
    assert isinstance(budi, orang.__PY_CLASS__)
    assert budi.nama == "Budi"

    budi.nama = "Andi"

    assert budi.nama == "Andi"
    assert budi.sapa() == "Halo Andi"
    assert budi.lihat_umur() == 20
    assert budi() is None
    assert budi.to_dict() == {"nama": "Andi"}


def test_private_field_is_hidden_outside_structure_context():
    config = Config()
    orang = Structure(
        "Orang",
        config,
        {
            "nama": {"type": str},
            "umur": {"type": int, "is_priv": True},
        },
    )
    budi = orang(nama="Budi", umur=20)

    with pytest.raises(AttributeError):
        budi.umur


def test_private_method_is_hidden_but_callable_through_internal_call():
    config = Config()
    orang = Structure("Orang", config, {"nama": {"type": str}})
    orang.set_method("rahasia", lambda ini: ini.nama, is_priv=True)
    orang.set_method("buka_rahasia", lambda ini: ini.rahasia())
    budi = orang(nama="Budi")

    with pytest.raises(AttributeError):
        budi.rahasia()

    assert budi.buka_rahasia() == "Budi"


def test_call_without_inisiasi_raises_error():
    config = Config()
    orang = Structure("Orang", config, {"nama": {"type": str}})
    budi = orang(nama="Budi")

    with pytest.raises(AttributeError):
        budi()


def test_structure_validates_required_unknown_and_type_mismatch():
    config = Config()
    orang = Structure("Orang", config, {"nama": {"type": str}})

    with pytest.raises(AttributeError):
        orang()

    with pytest.raises(AttributeError):
        orang(nama="Budi", umur=20)

    with pytest.raises(TypeCheckError):
        orang(nama=123)


def test_structure_extend_copies_fields_and_methods():
    config = Config()
    makhluk = Structure("Makhluk", config, {"nama": {"type": str}})
    makhluk.set_method("sapa", lambda ini: f"Halo {ini.nama}")

    orang = Structure("Orang", config, {"umur": {"type": int}}, makhluk)
    budi = orang(nama="Budi", umur=20)

    assert budi.nama == "Budi"
    assert budi.umur == 20
    assert budi.sapa() == "Halo Budi"


def test_structure_extend_rejects_duplicate_field():
    config = Config()
    makhluk = Structure("Makhluk", config, {"nama": {"type": str}})

    with pytest.raises(AttributeError, match="field duplikat"):
        Structure("Orang", config, {"nama": {"type": str}}, makhluk)


def test_structure_extend_rejects_duplicate_method():
    config = Config()
    makhluk = Structure("Makhluk", config, {})
    makhluk.set_method("sapa", lambda ini: "Halo")
    orang = Structure("Orang", config, {}, makhluk)

    with pytest.raises(AttributeError, match="method duplikat"):
        orang.set_method("sapa", lambda ini: "Hai")


def test_trait_accepts_matching_method_signature():
    method = type(
        "sapa",
        (object,),
        {
            "__call__": lambda self, ini: "Halo",
            "__annotations__": {"ini": object, "return": str},
        },
    )()
    sifat = Trait(
        "BisaSapa",
        {
            "sapa": {
                "annotations": {"ini": object, "return": str},
                "type": Callable[[...], Any],
            }
        },
    )

    sifat([{"name": "sapa", "value": method, "type": Callable[[...], Any]}])


def test_trait_rejects_missing_method():
    sifat = Trait(
        "BisaSapa",
        {
            "sapa": {
                "annotations": {"ini": object, "return": str},
                "type": Callable[[...], Any],
            }
        },
    )

    with pytest.raises(AttributeError, match="kekurangan method"):
        sifat([])


def test_trait_rejects_mismatched_method_signature():
    method = type(
        "sapa",
        (object,),
        {
            "__call__": lambda self, ini: "Halo",
            "__annotations__": {"ini": object, "return": int},
        },
    )()
    sifat = Trait(
        "BisaSapa",
        {
            "sapa": {
                "annotations": {"ini": object, "return": str},
                "type": Callable[[...], Any],
            }
        },
    )

    with pytest.raises(TypeError, match="annotation return"):
        sifat([{"name": "sapa", "value": method, "type": Callable[[...], Any]}])
