from pathlib import Path
import os

from setuptools import find_packages, setup


ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
README = ROOT / "README.md"

setup(
    name="IDScript",
    version="0.0.1a3",
    description="IDScript adalah bahasa pemrograman berbahasa Indonesia penerus Indonesian Script (IS), dengan interpreter dan compiler VM resmi.",
    long_description=README.read_text(encoding="utf-8") if README.exists() else "",
    long_description_content_type="text/markdown",
    author="Elang MRJ",
    author_email="elangmuhamad888@gmail.com",
    url="https://github.com/Elang-elang/IDScript",
    project_urls={
        "Indonesian Script (IS)": "https://github.com/Elang-elang/indonesian_script",
        "Source": "https://github.com/Elang-elang/IDScript",
        "Display Icon": "https://raw.githubusercontent.com/Elang-elang/IDScript/main/icons/big.jpg",
        "Small Icon": "https://raw.githubusercontent.com/Elang-elang/IDScript/main/icons/small.jpg",
    },
    license="MIT",
    license_files=["LICENSE.md"],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=False,
    package_data={
        "IDScript": [
            "gramm.lark",
            "Builtins/*.ids",
            "Builtins/*.py",
            "Builtins/Tipe/*.py",
            "Builtins/Tipe/*.ids",
            "Builtins/Tipe/Iterator/*.py",
            "Builtins/Tipe/Iterator/*.ids",
            "WrapperIDS/Python/*.py"
            "properties/*",
            "properties/_Reprer.py",
            "properties/config.py",
            "properties/operator.py",
            "properties/__helper/*.py",
            "properties/Modules/*",
            "properties/Scoping/*.py",
            "properties/TypeSystem/*.py",
            "properties/IDSObject/*",
            "properties/Modules/LoadWrapper/*.py",
            "properties/IDSObject/Function/*.py",
            "properties/IDSObject/Operation/*.py",
            "properties/IDSObject/Structure/*.py",
            "properties/IDSObject/Structure/special_methods/*.py",
            "properties/IDSObject/Structure/special_methods/*.json",
            "properties/IDSObject/Structure/special_methods/SystemAttribute/*.py",
        ],
        "IDScript.Builtins": ["*.ids", "*.idsm", "*.idsc"],
        "IDScript.properties.IDSObject.Structure.special_methods": ["TOKEN.json", "RAW_TOKEN.json"],
    },
    install_requires=[
        "lark>=1.0",
        "typeguard>=4.0",
        "click>=8.0",
    ],
    extras_require={
        "all": [
            "mypy",
            "pytest",
            "lark",
            "typeguard"
        ],
        "dev": [
            "mypy",
            "pytest",
        ],
        "all": [
            "click",
            "lark",
            "typeguard",
        ]
    },
    python_requires=">=3.14",
    entry_points={
        "console_scripts": [
            "idscript=IDScript.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Compilers",
    ],
)
