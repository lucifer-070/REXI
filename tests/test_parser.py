"""
test_parser.py — pytest tests for the REXI Parser.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.lexer import Lexer
from src.parser import Parser, ParseError
from src.ast_nodes import (
    NumberNode, BoolNode, VarAccessNode,
    BinOpNode, UnaryOpNode,
    VarAssignNode, FuncDefNode, FuncCallNode,
    IfNode, ReturnNode, BlockNode,
)


def parse(source: str):
    """Helper: lex + parse, return the block's statement list."""
    tokens = Lexer(source).tokenize()
    block  = Parser(tokens).parse()
    return block.statements


def parse_one(source: str):
    """Parse a single-statement source and return the statement node."""
    stmts = parse(source)
    assert len(stmts) == 1, f"Expected 1 statement, got {len(stmts)}: {stmts}"
    return stmts[0]


# ── Number literals ────────────────────────────────────────────────────────────

class TestNumbers:
    def test_integer(self):
        node = parse_one("42")
        assert isinstance(node, NumberNode)
        assert node.value == 42

    def test_float(self):
        node = parse_one("3.14")
        assert isinstance(node, NumberNode)
        assert node.value == 3.14

    def test_negative_via_unary(self):
        node = parse_one("-5")
        assert isinstance(node, UnaryOpNode)
        assert node.op == '-'
        assert isinstance(node.operand, NumberNode)
        assert node.operand.value == 5


# ── Booleans ───────────────────────────────────────────────────────────────────

class TestBooleans:
    def test_true(self):
        node = parse_one("true")
        assert isinstance(node, BoolNode)
        assert node.value is True

    def test_false(self):
        node = parse_one("false")
        assert isinstance(node, BoolNode)
        assert node.value is False


# ── Arithmetic binary ops ─────────────────────────────────────────────────────

class TestBinaryOps:
    def test_addition(self):
        node = parse_one("1 + 2")
        assert isinstance(node, BinOpNode)
        assert node.op == '+'
        assert isinstance(node.left,  NumberNode)
        assert isinstance(node.right, NumberNode)

    def test_subtraction(self):
        node = parse_one("10 - 3")
        assert node.op == '-'

    def test_multiplication(self):
        node = parse_one("4 * 5")
        assert node.op == '*'

    def test_division(self):
        node = parse_one("9 / 3")
        assert node.op == '/'

    def test_modulo(self):
        node = parse_one("10 % 3")
        assert node.op == '%'

    def test_power(self):
        node = parse_one("2 ^ 3")
        assert isinstance(node, BinOpNode)
        assert node.op == '^'


# ── Operator precedence ───────────────────────────────────────────────────────

class TestPrecedence:
    def test_mul_before_add(self):
        # 1 + 2 * 3  →  BinOp(1, +, BinOp(2, *, 3))
        node = parse_one("1 + 2 * 3")
        assert node.op == '+'
        assert node.right.op == '*'

    def test_parens_override(self):
        # (1 + 2) * 3  →  BinOp(BinOp(1, +, 2), *, 3)
        node = parse_one("(1 + 2) * 3")
        assert node.op == '*'
        assert node.left.op == '+'

    def test_power_right_associative(self):
        # 2^3^2  →  BinOp(2, ^, BinOp(3, ^, 2))
        node = parse_one("2^3^2")
        assert node.op == '^'
        assert node.right.op == '^'

    def test_unary_minus_high_prec(self):
        # -2 ^ 2  →  UnaryOp(-, BinOp(2, ^, 2))
        # (unary binds tighter than ^ only when it's a nested unary in pow rule)
        node = parse_one("2 ^ -2")
        assert node.op == '^'
        assert isinstance(node.right, UnaryOpNode)


# ── Comparison operators ──────────────────────────────────────────────────────

class TestComparisons:
    def test_equal(self):
        node = parse_one("x == 1")
        assert node.op == '=='

    def test_not_equal(self):
        node = parse_one("x != 1")
        assert node.op == '!='

    def test_lt(self):
        node = parse_one("a < b")
        assert node.op == '<'

    def test_gt(self):
        node = parse_one("a > b")
        assert node.op == '>'

    def test_lte(self):
        node = parse_one("a <= b")
        assert node.op == '<='

    def test_gte(self):
        node = parse_one("a >= b")
        assert node.op == '>='


# ── Logical operators ─────────────────────────────────────────────────────────

class TestLogical:
    def test_and(self):
        node = parse_one("a and b")
        assert node.op == 'and'

    def test_or(self):
        node = parse_one("a or b")
        assert node.op == 'or'

    def test_not(self):
        node = parse_one("not x")
        assert isinstance(node, UnaryOpNode)
        assert node.op == 'not'

    def test_and_before_or(self):
        # a or b and c  →  BinOp(a, or, BinOp(b, and, c))
        node = parse_one("a or b and c")
        assert node.op == 'or'
        assert node.right.op == 'and'


# ── Variable assignment ───────────────────────────────────────────────────────

class TestAssignment:
    def test_simple_assign(self):
        node = parse_one("x = 42")
        assert isinstance(node, VarAssignNode)
        assert node.name  == 'x'
        assert isinstance(node.value, NumberNode)

    def test_assign_expression(self):
        node = parse_one("result = 1 + 2")
        assert isinstance(node, VarAssignNode)
        assert isinstance(node.value, BinOpNode)

    def test_var_access(self):
        node = parse_one("my_var")
        assert isinstance(node, VarAccessNode)
        assert node.name == 'my_var'


# ── Function definition ───────────────────────────────────────────────────────

class TestFuncDef:
    def test_no_params(self):
        node = parse_one("def answer() = 42")
        assert isinstance(node, FuncDefNode)
        assert node.name   == 'answer'
        assert node.params == []
        assert isinstance(node.body, NumberNode)

    def test_one_param(self):
        node = parse_one("def double(x) = x * 2")
        assert node.params == ['x']
        assert isinstance(node.body, BinOpNode)

    def test_two_params(self):
        node = parse_one("def add(a, b) = a + b")
        assert node.params == ['a', 'b']


# ── Function call ─────────────────────────────────────────────────────────────

class TestFuncCall:
    def test_no_args(self):
        node = parse_one("greet()")
        assert isinstance(node, FuncCallNode)
        assert node.name == 'greet'
        assert node.args == []

    def test_one_arg(self):
        node = parse_one("sqrt(9)")
        assert node.name == 'sqrt'
        assert len(node.args) == 1
        assert isinstance(node.args[0], NumberNode)

    def test_two_args(self):
        node = parse_one("max(a, b)")
        assert node.name == 'max'
        assert len(node.args) == 2

    def test_nested_call(self):
        node = parse_one("sqrt(abs(-4))")
        assert isinstance(node.args[0], FuncCallNode)
        assert node.args[0].name == 'abs'


# ── If expression ─────────────────────────────────────────────────────────────

class TestIfExpr:
    def test_if_then(self):
        node = parse_one("if x > 0 then x")
        assert isinstance(node, IfNode)
        assert node.else_body is None

    def test_if_then_else(self):
        node = parse_one("if x > 0 then x else -x")
        assert isinstance(node, IfNode)
        assert node.else_body is not None

    def test_if_without_then_keyword(self):
        node = parse_one("if a == 1 b")   # 'then' is optional
        assert isinstance(node, IfNode)


# ── Return statement ──────────────────────────────────────────────────────────

class TestReturn:
    def test_return(self):
        node = parse_one("return 42")
        assert isinstance(node, ReturnNode)
        assert isinstance(node.value, NumberNode)


# ── Multi-statement block ─────────────────────────────────────────────────────

class TestBlock:
    def test_two_statements(self):
        stmts = parse("x = 1\ny = 2")
        assert len(stmts) == 2
        assert isinstance(stmts[0], VarAssignNode)
        assert isinstance(stmts[1], VarAssignNode)

    def test_semicolon_separator(self):
        stmts = parse("x = 1; y = 2")
        assert len(stmts) == 2

    def test_blank_lines_ignored(self):
        stmts = parse("\n\nx = 1\n\n")
        assert len(stmts) == 1


# ── Error handling ────────────────────────────────────────────────────────────

class TestErrors:
    def test_unexpected_token(self):
        with pytest.raises(ParseError):
            parse("+ +")

    def test_missing_rparen(self):
        with pytest.raises(ParseError):
            parse("(1 + 2")

    def test_missing_func_body(self):
        with pytest.raises(ParseError):
            parse("def f(x) =")

    def test_error_has_location(self):
        with pytest.raises(ParseError) as exc_info:
            parse("(1 +")
        err = exc_info.value
        assert err.line >= 1
