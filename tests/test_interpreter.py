"""
test_interpreter.py — pytest tests for the REXI Interpreter.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.lexer import Lexer
from src.parser import Parser
from src.interpreter import Interpreter, REXIRuntimeError


def run(source: str):
    """Helper: lex → parse → interpret, return the final value."""
    tokens = Lexer(source).tokenize()
    ast    = Parser(tokens).parse()
    return Interpreter().run(ast)


def run_interp(source: str, interp: Interpreter):
    """Run using a shared interpreter (so variables persist across calls)."""
    tokens = Lexer(source).tokenize()
    ast    = Parser(tokens).parse()
    return interp.run(ast)


# ── Arithmetic ────────────────────────────────────────────────────────────────

class TestArithmetic:
    def test_integer(self):
        assert run("42") == 42

    def test_float(self):
        assert run("3.14") == pytest.approx(3.14)

    def test_addition(self):
        assert run("1 + 2") == 3

    def test_subtraction(self):
        assert run("10 - 4") == 6

    def test_multiplication(self):
        assert run("3 * 4") == 12

    def test_division(self):
        assert run("10 / 4") == pytest.approx(2.5)

    def test_modulo(self):
        assert run("10 % 3") == 1

    def test_power(self):
        assert run("2 ^ 8") == 256

    def test_unary_minus(self):
        assert run("-7") == -7

    def test_unary_plus(self):
        assert run("+5") == 5

    def test_precedence_mul_over_add(self):
        assert run("2 + 3 * 4") == 14   # not 20

    def test_parentheses(self):
        assert run("(2 + 3) * 4") == 20

    def test_nested_parens(self):
        assert run("((2 + 3) * 4) - 1") == 19

    def test_right_assoc_power(self):
        assert run("2 ^ 3 ^ 2") == 512  # 2^(3^2) = 2^9 = 512, not (2^3)^2 = 64


# ── Booleans & comparisons ────────────────────────────────────────────────────

class TestBooleans:
    def test_true(self):
        assert run("true") is True

    def test_false(self):
        assert run("false") is False

    def test_equal_true(self):
        assert run("1 == 1") is True

    def test_equal_false(self):
        assert run("1 == 2") is False

    def test_not_equal(self):
        assert run("1 != 2") is True

    def test_less_than(self):
        assert run("3 < 4") is True

    def test_greater_than(self):
        assert run("5 > 3") is True

    def test_lte(self):
        assert run("3 <= 3") is True

    def test_gte(self):
        assert run("4 >= 5") is False

    def test_and_short_circuit(self):
        assert run("true and false") is False

    def test_or_short_circuit(self):
        assert run("false or true") is True

    def test_not_true(self):
        assert run("not true") is False

    def test_not_false(self):
        assert run("not false") is True


# ── Variables ─────────────────────────────────────────────────────────────────

class TestVariables:
    def test_assign_and_read(self):
        i = Interpreter()
        run_interp("x = 10", i)
        assert run_interp("x", i) == 10

    def test_reassign(self):
        i = Interpreter()
        run_interp("x = 5", i)
        run_interp("x = 99", i)
        assert run_interp("x", i) == 99

    def test_use_in_expression(self):
        i = Interpreter()
        run_interp("a = 3", i)
        run_interp("b = 4", i)
        assert run_interp("a + b", i) == 7

    def test_undefined_raises(self):
        with pytest.raises(REXIRuntimeError):
            run("undefined_var")


# ── Built-in functions ────────────────────────────────────────────────────────

class TestBuiltins:
    def test_sqrt(self):
        assert run("sqrt(9)") == pytest.approx(3.0)

    def test_sqrt_float(self):
        assert run("sqrt(2)") == pytest.approx(1.4142135623730951)

    def test_abs_negative(self):
        assert run("abs(-5)") == 5

    def test_abs_positive(self):
        assert run("abs(7)") == 7

    def test_max(self):
        assert run("max(3, 7)") == 7

    def test_min(self):
        assert run("min(3, 7)") == 3

    def test_pow(self):
        assert run("pow(2, 10)") == 1024

    def test_floor(self):
        assert run("floor(3.9)") == 3

    def test_ceil(self):
        assert run("ceil(3.1)") == 4

    def test_round_down(self):
        assert run("round(2.3)") == 2

    def test_round_up(self):
        assert run("round(2.7)") == 3

    def test_sqrt_negative_raises(self):
        with pytest.raises(REXIRuntimeError):
            run("sqrt(-1)")

    def test_sqrt_wrong_args_raises(self):
        with pytest.raises(REXIRuntimeError):
            run("sqrt(1, 2)")


# ── User-defined functions ────────────────────────────────────────────────────

class TestUserFunctions:
    def test_no_params(self):
        i = Interpreter()
        run_interp("def answer() = 42", i)
        assert run_interp("answer()", i) == 42

    def test_one_param(self):
        i = Interpreter()
        run_interp("def double(x) = x * 2", i)
        assert run_interp("double(5)", i) == 10

    def test_two_params(self):
        i = Interpreter()
        run_interp("def add(a, b) = a + b", i)
        assert run_interp("add(3, 4)", i) == 7

    def test_recursive_factorial(self):
        i = Interpreter()
        run_interp("def fact(n) = if n <= 1 then 1 else n * fact(n - 1)", i)
        assert run_interp("fact(5)", i) == 120

    def test_nested_calls(self):
        i = Interpreter()
        run_interp("def square(n) = n * n", i)
        assert run_interp("square(square(3))", i) == 81

    def test_wrong_arg_count(self):
        i = Interpreter()
        run_interp("def add(a, b) = a + b", i)
        with pytest.raises(REXIRuntimeError):
            run_interp("add(1)", i)

    def test_params_dont_leak(self):
        """Function parameters must not be visible outside the function."""
        i = Interpreter()
        run_interp("def f(secret) = secret * 2", i)
        run_interp("f(99)", i)
        with pytest.raises(REXIRuntimeError):
            run_interp("secret", i)


# ── If / else ─────────────────────────────────────────────────────────────────

class TestIfElse:
    def test_if_true_branch(self):
        assert run("if true then 1 else 2") == 1

    def test_if_false_branch(self):
        assert run("if false then 1 else 2") == 2

    def test_if_no_else_true(self):
        assert run("if true then 99") == 99

    def test_if_no_else_false(self):
        assert run("if false then 99") is None

    def test_if_with_comparison(self):
        i = Interpreter()
        run_interp("x = 10", i)
        assert run_interp("if x > 5 then 1 else 0", i) == 1

    def test_nested_if(self):
        code = "if true then if false then 1 else 2 else 3"
        assert run(code) == 2


# ── Division by zero ──────────────────────────────────────────────────────────

class TestErrors:
    def test_division_by_zero(self):
        with pytest.raises(REXIRuntimeError):
            run("1 / 0")

    def test_undefined_function(self):
        with pytest.raises(REXIRuntimeError):
            run("ghost()")

    def test_call_non_function(self):
        with pytest.raises(REXIRuntimeError):
            i = Interpreter()
            run_interp("x = 5", i)
            run_interp("x()", i)
