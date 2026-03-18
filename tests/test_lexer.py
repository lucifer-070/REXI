"""
test_lexer.py — pytest tests for the REXI Lexer.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.lexer import Lexer, LexerError
from src.tokens import Token, TokenType


def lex(source: str):
    """Helper: tokenise source and strip the trailing EOF token."""
    tokens = Lexer(source).tokenize()
    return tokens[:-1]  # remove EOF for brevity in assertions


def tok(t: TokenType, v):
    """Quick Token constructor (ignores location for equality checks)."""
    return Token(t, v)


# ── Number literals ────────────────────────────────────────────────────────────

class TestNumbers:
    def test_integer(self):
        assert lex("42") == [tok(TokenType.NUMBER, 42)]

    def test_float(self):
        assert lex("3.14") == [tok(TokenType.NUMBER, 3.14)]

    def test_leading_dot(self):
        assert lex(".5") == [tok(TokenType.NUMBER, 0.5)]

    def test_multiple_numbers(self):
        result = lex("1 2 3")
        assert result == [
            tok(TokenType.NUMBER, 1),
            tok(TokenType.NUMBER, 2),
            tok(TokenType.NUMBER, 3),
        ]


# ── Operators ──────────────────────────────────────────────────────────────────

class TestOperators:
    def test_arithmetic(self):
        result = lex("+ - * / % ^")
        types = [t.type for t in result]
        assert types == [
            TokenType.PLUS, TokenType.MINUS, TokenType.MUL,
            TokenType.DIV,  TokenType.MOD,   TokenType.POWER,
        ]

    def test_comparison_two_char(self):
        result = lex("== != <= >=")
        types = [t.type for t in result]
        assert types == [TokenType.EQ, TokenType.NEQ, TokenType.LTE, TokenType.GTE]

    def test_comparison_one_char(self):
        result = lex("< >")
        types = [t.type for t in result]
        assert types == [TokenType.LT, TokenType.GT]

    def test_assign(self):
        assert lex("=") == [tok(TokenType.ASSIGN, "=")]

    def test_assign_vs_eq(self):
        result = lex("= ==")
        assert result[0].type == TokenType.ASSIGN
        assert result[1].type == TokenType.EQ


# ── Identifiers and keywords ───────────────────────────────────────────────────

class TestIdentifiers:
    def test_identifier(self):
        assert lex("foo") == [tok(TokenType.IDENTIFIER, "foo")]

    def test_underscore_identifier(self):
        assert lex("_my_var") == [tok(TokenType.IDENTIFIER, "_my_var")]

    def test_keyword_if(self):
        assert lex("if")[0].type == TokenType.IF

    def test_keyword_else(self):
        assert lex("else")[0].type == TokenType.ELSE

    def test_keyword_def(self):
        assert lex("def")[0].type == TokenType.DEF

    def test_keyword_return(self):
        assert lex("return")[0].type == TokenType.RETURN

    def test_keyword_and(self):
        assert lex("and")[0].type == TokenType.AND

    def test_keyword_or(self):
        assert lex("or")[0].type == TokenType.OR

    def test_keyword_not(self):
        assert lex("not")[0].type == TokenType.NOT

    def test_true_false(self):
        result = lex("true false")
        assert result[0].type  == TokenType.TRUE
        assert result[0].value == True
        assert result[1].type  == TokenType.FALSE
        assert result[1].value == False


# ── Delimiters ────────────────────────────────────────────────────────────────

class TestDelimiters:
    def test_parens(self):
        result = lex("()")
        assert result[0].type == TokenType.LPAREN
        assert result[1].type == TokenType.RPAREN

    def test_comma(self):
        assert lex(",")[0].type == TokenType.COMMA

    def test_newline_is_token(self):
        result = lex("a\nb")
        assert result[1].type == TokenType.NEWLINE

    def test_semicol_is_token(self):
        result = lex("a;b")
        assert result[1].type == TokenType.SEMICOL


# ── Comments ──────────────────────────────────────────────────────────────────

class TestComments:
    def test_comment_skipped(self):
        assert lex("# this is a comment") == []

    def test_comment_after_expr(self):
        result = lex("42 # answer")
        assert result == [tok(TokenType.NUMBER, 42)]


# ── Expressions ───────────────────────────────────────────────────────────────

class TestExpressions:
    def test_simple_addition(self):
        result = lex("1 + 2")
        types = [t.type for t in result]
        assert types == [TokenType.NUMBER, TokenType.PLUS, TokenType.NUMBER]

    def test_function_call_tokens(self):
        result = lex("sqrt(9)")
        assert result[0] == tok(TokenType.IDENTIFIER, "sqrt")
        assert result[1].type == TokenType.LPAREN
        assert result[2] == tok(TokenType.NUMBER, 9)
        assert result[3].type == TokenType.RPAREN


# ── Source location ───────────────────────────────────────────────────────────

class TestLocation:
    def test_line_tracking(self):
        tokens = Lexer("a\nb").tokenize()
        # 'a' → line 1, newline, 'b' → line 2
        assert tokens[0].line == 1
        assert tokens[2].line == 2

    def test_col_tracking(self):
        tokens = Lexer("abc").tokenize()
        assert tokens[0].col == 1


# ── Error handling ────────────────────────────────────────────────────────────

class TestErrors:
    def test_unexpected_char(self):
        with pytest.raises(LexerError):
            Lexer("@").tokenize()

    def test_error_has_location(self):
        with pytest.raises(LexerError) as exc_info:
            Lexer("1 + @").tokenize()
        err = exc_info.value
        assert err.line == 1
        assert err.col  == 5


# ── EOF token ─────────────────────────────────────────────────────────────────

class TestEOF:
    def test_eof_present(self):
        tokens = Lexer("").tokenize()
        assert tokens[-1].type == TokenType.EOF

    def test_eof_after_tokens(self):
        tokens = Lexer("42").tokenize()
        assert tokens[-1].type == TokenType.EOF
