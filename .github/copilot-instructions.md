# IDScript Copilot Instructions

## Overview

IDScript adalah bahasa pemrograman berorientasi objek berbasis Indonesia yang digabungkan dengan teknologi Python. Proyek ini adalah interpreter/compiler yang menerjemahkan kode IDScript (yang menggunakan sintaks Indonesian) ke dalam Python VM.

## Architecture

### Core Pipeline

The execution flow follows: **Code → Lexer/Parser → AST → Compiler → Python Execution**

1. **Grammar** (`gramm.lark`): Lark-based grammar defines IDScript syntax (e.g., `fungsi`, `konst`, `struktur`, `implemen`)
2. **Parser** (`interpreter/parser/`): Converts Lark parse tree to IDScript AST nodes
3. **AST Nodes** (`interpreter/ast_nodes/ASTNodes.py`): Defines abstract syntax tree node types
4. **Compiler** (`interpreter/compiler/`): Visits AST and generates executable context
5. **Runtime** (`properties/`): Type system, scoping, modules, functions, and structures at runtime

### Module Organization

- **`interpreter/`**: Parser and compiler engine
  - `parser/`: Expression, statement, type annotation parsing
  - `compiler/`: Expression/statement compilation, type annotation handling
  - `compile.py`: Entry point that orchestrates parsing and compilation
  
- **`properties/`**: Runtime environment and object system
  - `IDSObject/`: Function, Structure, and Operation property management
  - `Scoping/`: Namespace, scope, and constant management
  - `TypeSystem/`: Type definitions and validation
  - `Modules/`: Module loading for Python and JavaScript interop
  
- **`Builtins/`**: Built-in classes and modules
  - `.ids` files: IDScript source for built-in types (Daftar, Kamus, Konsol, etc.)
  - `.idsm` files: IDScript interface definitions
  - `.py` files: Python implementations of built-in behavior

## Key Conventions

### Indonesian Naming
- Language keywords are in Indonesian: `fungsi` (function), `konst` (const), `var` (variable), `struktur` (struct), `implemen` (implement), `metode` (method), `publik` (public), `privat` (private)
- Built-in types use Indonesian: `Teks` (text/string), `Angka` (number), `Daftar` (list), `Kamus` (dict), `Konsol` (console)
- This applies to codebase too: variable names, class names, and comments often use Indonesian

### Parser Module Organization
Each parser module (`parser/*.py`) handles a specific grammar category:
- `expression.py`: Arithmetic, logical, comparison, literals, identifiers
- `simple_stmt.py`: Variable declarations, assignments, control flow
- `top_stmt.py`: Function, struct, and module declarations
- `type_ann.py`: Type annotations
- `core.py`: Parser base class and utilities

### Compiler Module Organization
Mirror the parser structure; each compiler module (`compiler/*.py`) processes the corresponding AST:
- `expression.py`: Compiles expressions to Python code
- `simple_stmt.py`: Compiles statements to Python code
- `top_stmt.py`: Compiles declarations to Python code
- `type_ann.py`: Processes type information (used by typeguard validation)
- `core.py`: Compiler base class and context management

### Scoping and Runtime
- `Scoping/namespace.py`: Manages name-to-value bindings in current scope
- `Scoping/scope.py`: Represents scope hierarchy (local, global, module)
- `Scoping/constanta.py`: Tracks constant bindings (immutable after initialization)
- `properties/config.py`: Global compiler configuration (scope manager, type system)

### Type System
- `TypeSystem/types.py`: Type definitions (basic types like `Angka`, `Teks`)
- `TypeSystem/extra_types.py`: Complex types (unions, optionals)
- `TypeSystem/system.py`: Type checking and validation with typeguard integration

## Build, Test, and Run

### Installation (Local Development)
```bash
pip install -e .
```

### Run IDScript Program
```bash
idscript <file.ids>
```

Example:
```bash
idscript example.ids
```

The CLI is defined in `__main__.py` using Click. Programs must define a `fungsi utama()` (main function) which is called automatically.

### Testing
```bash
python testing.py
```

This runs the example code in `example.ids` (hardcoded file path). Modify `testing.py` to test different `.ids` files.

**Note:** There is no formal pytest suite. Tests are ad-hoc via `testing.py`. For comprehensive testing, create additional test scripts.

### Type Checking
```bash
mypy src/
```

Uses typeguard for runtime type validation; mypy for static analysis.

## Common Tasks

### Adding a Built-in Type
1. Create IDScript interface in `Builtins/<NamaType>.idsm`
2. Create IDScript implementation in `Builtins/<NamaType>.ids`
3. Create Python implementation in `Builtins/_<NamaType>.py`
4. Register in `Builtins/__init__.py`

### Extending the Grammar
1. Edit `gramm.lark` to add new rules
2. Add corresponding AST node in `interpreter/ast_nodes/ASTNodes.py`
3. Add parser implementation in appropriate `interpreter/parser/*.py` module
4. Add compiler implementation in corresponding `interpreter/compiler/*.py` module

### Adding a Keyword or Operator
1. Update `gramm.lark` with the rule
2. Add transformer method in the appropriate parser module (e.g., `->` keyword in lark creates method names)
3. Add compiler support to handle the new AST node type

## Debugging

### Enable Verbose Output
Modify `__main__.py` to print the AST or compiled code:
```python
compiler = Compile(...)
print(compiler._Compile__ctx__)  # Print AST
print(compiler.compiler.config)   # Print runtime config
```

### Inspect Compiled Output
The `Compile` object holds both the AST and the runtime compiler. Use `compiler.compiler.config.scope_name.global_scope` to inspect the global namespace after compilation.

### Check Grammar Parsing
Test Lark parsing directly:
```python
from src.IDScript.interpreter.compile import PARSER
tree = PARSER.parse(your_code)
print(tree.pretty())
```

## Dependencies

**Required:**
- `lark>=1.0`: Parser/grammar framework
- `typeguard>=4.0`: Runtime type checking
- `click>=8.0`: CLI framework

**Development:**
- `mypy`: Static type checking
- `pytest`: Test framework (currently unused but available)

## Files You'll Touch Often

- `gramm.lark`: When adding language features
- `interpreter/compiler/core.py`: Runtime context management
- `properties/IDSObject/`: When working with object/structure system
- `Builtins/`: When adding built-in types or methods
- `example.ids`: Quick testing of new features
