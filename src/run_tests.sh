#!/system/bin/sh
# =============================================================
# IDScript — Unified Test Runner
# =============================================================
# Usage:  cd src && sh run_tests.sh [--fast]
#
# Without --fast: runs ALL test suites sequentially (may take 10+ min)
# With --fast:    runs only the quick suites (skip test_compile & test_compiler)
#
# Requires: pytest, mypy, Python 3.13+, and IDScript installed in dev mode.
# =============================================================

PYTHON="python"
SRC_DIR="$(dirname "$0")"
cd "$SRC_DIR" || exit 1

echo "==================================="
echo " IDScript — Test Suite Runner"
echo "==================================="
echo "Started: $(date)"
echo ""

# ---- 1.  Fast pytest suites (non-parser) ----
echo "--- pytest: CLI, exceptions, builtins, struct runtime, maker ---"
$PYTHON -m pytest \
  IDScript/compile/testing/test_cli.py \
  IDScript/compile/testing/test_exceptions.py \
  IDScript/compile/testing/test_external_builtins.py \
  IDScript/compile/testing/test_struct_runtime.py \
  IDScript/compile/testing/test_examples.py \
  IDScript/maker/testing/test_maker.py \
  -v --tb=line -q
PYTEST_FAST_EXIT=$?
echo "Exit code: $PYTEST_FAST_EXIT"
echo ""

if [ "$1" = "--fast" ]; then
    echo "Fast mode — skipping parser tests."
    echo "Done: $(date)"
    exit $PYTEST_FAST_EXIT
fi

# ---- 2.  Slow pytest suites (Earley parser) ----
echo "--- pytest: test_compile.py (runtime compiler) ---"
$PYTHON -m pytest IDScript/compile/testing/test_compile.py -v --tb=line -q
PYTEST_COMPILE_EXIT=$?
echo "Exit code: $PYTEST_COMPILE_EXIT"
echo ""

echo "--- pytest: test_compiler.py (VM compiler) ---"
$PYTHON -m pytest IDScript/compile/Compiler/testing/test_compiler.py -v --tb=line -q
PYTEST_COMPILER_EXIT=$?
echo "Exit code: $PYTEST_COMPILER_EXIT"
echo ""

# ---- 3.  mypy (summary) ----
echo "--- mypy: type checking ---"
# Run on a few key files explicitly (full-package mypy is very slow)
$PYTHON -m mypy \
  IDScript/builtins/_Daftar.py \
  IDScript/builtins/_Regex.py \
  IDScript/builtins/_Konsol.py \
  IDScript/maker/__init__.py \
  --ignore-missing-imports --no-strict-optional
MYPY_EXIT=$?
echo "Exit code: $MYPY_EXIT"
echo ""

# ---- 4.  CLI smoke test (examples) ----
echo "--- CLI: example files ---"
for f in ../examples/example.ids ../examples/NativeIDS/*.ids; do
    [ -f "$f" ] || continue
    base=$(basename "$f")
    out=$($PYTHON -m IDScript "$f" 2>&1)
    if [ $? -eq 0 ]; then
        echo "  PASS: $base"
    else
        echo "  FAIL: $base — $out"
    fi
done
echo ""

# ---- 5.  Summary ----
echo "==================================="
echo " Summary"
echo "==================================="
echo " test_cli / exceptions / builtins / struct / examples / maker  : $PYTEST_FAST_EXIT"
echo " test_compile (runtime compiler)                                : $PYTEST_COMPILE_EXIT"
echo " test_compiler (VM compiler)                                    : $PYTEST_COMPILER_EXIT"
echo " mypy                                                          : $MYPY_EXIT"
echo ""
echo "Finished: $(date)"
echo "==================================="
