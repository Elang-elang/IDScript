from pathlib import Path

from setuptools import find_packages, setup


ROOT = Path(__file__).parent
README = ROOT / "README.md"


setup(
    name="idscript",
    version="0.1.0",
    description="IDScript adalah bahasa pemrograman berbahasa Indonesia penerus Indonesian Script (IS), dengan interpreter dan compiler VM resmi.",
    long_description=README.read_text(encoding="utf-8") if README.exists() else "",
    long_description_content_type="text/markdown",
    author="Elang MRJ",
    author_email="elangmuhamad888@gmail.com",
    url="https://github.com/Elang-elang/IDScript",
    project_urls={
        "Indonesian Script (IS)": "https://github.com/Elang-elang/indonesian_script",
        "Source": "https://github.com/Elang-elang/IDScript",
    },
    license="TODO",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    package_data={
        "IDScript": ["gramm.lark"],
        "IDScript.builtins": ["*.ids", "*.idsc", "Regex/*.ids"],
        "IDScript.compile.Compiler": ["TOKEN.json"],
    },
    install_requires=[
        "click>=8.0",
        "lark>=1.0",
        "typeguard>=4.0",
    ],
    extras_require={
        "dev": [
            "mypy",
            "pytest",
        ],
        "all": [
            "click",
            "lark",
            "typeguard",
            "mypy",
            "pytest"
        ]
    },
    python_requires=">=3.13",
    entry_points={
        "console_scripts": [
            "idscript=IDScript.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Compilers",
    ],
)
