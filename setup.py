from pathlib import Path
import os

from setuptools import find_packages, setup


ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
README = ROOT / "README.md"
<<<<<<< HEAD
setup(
    name="idscript",
    version="0.1.7",
=======

setup(
    name="idscript",
    version="0.0.1a",
>>>>>>> 3bedd79 (Update from Alternative and the new update)
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
        "IDScript": ["gramm.lark", "icons/*.jpg"],
<<<<<<< HEAD
        "IDScript.builtins": ["*.ids", "*.idsm", "*.idsc"],
        "IDScript.compile.Compiler": ["TOKEN.json"],
        "IDScript.maker": ["README.md"],
        "IDScript.IDSRepl": ["README.md"],
    },
    install_requires=[
        "click>=8.0",
        "lark>=1.0",
        "typeguard>=4.0",
        "prompt_toolkit>=3.0",
        "Pygments>=2.0",
    ],
    extras_require={
=======
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
>>>>>>> 3bedd79 (Update from Alternative and the new update)
        "dev": [
            "mypy",
            "pytest",
        ],
        "all": [
<<<<<<< HEAD
            "click",
            "lark",
            "typeguard",
            "prompt_toolkit",
            "Pygments",
        ]
    },
    python_requires=">=3.13",
=======
            "lark",
            "typeguard",
            "click"
        ]
    },
    python_requires=">=3.14",
>>>>>>> 3bedd79 (Update from Alternative and the new update)
    entry_points={
        "console_scripts": [
            "idscript=IDScript.__main__:main",
        ],
    },
    classifiers=[
<<<<<<< HEAD
        "Development Status :: 4 - Beta",
=======
        "Development Status :: 3 - Alpha",
>>>>>>> 3bedd79 (Update from Alternative and the new update)
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Compilers",
    ],
)
