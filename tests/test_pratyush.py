"""
test_pratyush.py — Tests for Pratyush's contributions:
  - visit_WhileNode interpreter behaviour
  - WhileNode rendering in ast_printer
  - cli helper functions
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter, REXIRuntimeError
from src.ast_printer import format_ast
from src.cli import _fmt


# ── Helpers ───────────────────────────────────────────────────────────────────

def run(source: str, interp=None):
    if interp is None:
        interp = Interpreter()
    tokens = Lexer(source).tokenize()
    ast    = Parser(tokens).parse()
    return interp.run(ast)


def make_interp(*setup_lines):
    """Create a shared interpreter with setup lines already evaluated."""
    i = Interpreter()
    for line in setup_lines:
        run(line, i)
    return i


# ── visit_WhileNode ───────────────────────────────────────────────────────────

class TestWhileInterpreter:
    def test_false_condition_returns_none(self):
        i = make_interp("x = 0")
        result = run("while x > 0 then x = x - 1", i)
        assert result is None

    def test_false_condition_variable_unchanged(self):
        i = make_interp("x = 0")
        run("while x > 0 then x = x - 1", i)
        assert run("x", i) == 0

    def test_countdown_from_one(self):
        i = make_interp("x = 1")
        run("while x > 0 then x = x - 1", i)
        assert run("x", i) == 0

    def test_countdown_from_five(self):
        i = make_interp("x = 5")
        run("while x > 0 then x = x - 1", i)
        assert run("x", i) == 0

    def test_countdown_from_ten(self):
        i = make_interp("x = 10")
        run("while x > 0 then x = x - 1", i)
        assert run("x", i) == 0

    def test_returns_last_body_value(self):
        # Body runs 3 times; last assignment x = x - 1 when x=1 returns 0
        i = make_interp("x = 3")
        result = run("while x > 0 then x = x - 1", i)
        assert result == 0

    def test_while_with_function_in_body(self):
        i = make_interp("def dec(n) = n - 1", "x = 4")
        run("while x > 0 then x = dec(x)", i)
        assert run("x", i) == 0

    def test_while_reads_outer_scope(self):
        i = make_interp("limit = 3", "n = 0")
        run("while n < limit then n = n + 1", i)
        assert run("n", i) == 3

    def test_infinite_loop_guard_raises(self):
        with pytest.raises(REXIRuntimeError):
            run("while true then 1")

    def test_infinite_loop_error_mentions_iterations(self):
        with pytest.raises(REXIRuntimeError) as exc_info:
            run("while true then 1")
        msg = str(exc_info.value).lower()
        assert "iteration" in msg or "infinite" in msg

    def test_while_boolean_breaks_after_one_iteration(self):
        i = make_interp("flag = true")
        run("while flag then flag = false", i)
        assert run("flag", i) is False


# ── AST printer: WhileNode ────────────────────────────────────────────────────

class TestWhilePrinter:
    def _ast(self, source):
        tokens = Lexer(source).tokenize()
        return Parser(tokens).parse()

    def test_printer_contains_while(self):
        out = format_ast(self._ast("while x > 0 then x"))
        assert "While" in out

    def test_printer_contains_cond_label(self):
        out = format_ast(self._ast("while x > 0 then x"))
        assert "cond" in out

    def test_printer_contains_body_label(self):
        out = format_ast(self._ast("while x > 0 then x"))
        assert "body" in out

    def test_printer_shows_condition_op(self):
        out = format_ast(self._ast("while x > 0 then x"))
        assert ">" in out

    def test_printer_shows_zero(self):
        out = format_ast(self._ast("while x > 0 then x"))
        assert "0" in out


# ── _fmt helper ───────────────────────────────────────────────────────────────

class TestFmtHelper:
    def test_none_returns_empty(self):
        assert _fmt(None) == ""

    def test_true_displays_as_true(self):
        assert _fmt(True) == "true"

    def test_false_displays_as_false(self):
        assert _fmt(False) == "false"

    def test_whole_float_shows_as_int(self):
        assert _fmt(4.0) == "4"

    def test_decimal_float_preserved(self):
        assert _fmt(3.14) == "3.14"

    def test_integer(self):
        assert _fmt(42) == "42"
