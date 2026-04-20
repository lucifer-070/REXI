"""
test_harshit.py — Tests for string literal lexing and error formatting.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.lexer import Lexer, LexerError
from src.tokens import TokenType
from src.errors import format_error


# ── String literal lexing ──────────────────────────────────────────────────────

class TestStringLiterals:
    def test_simple_string(self):
        tokens = Lexer('"hello"').tokenize()
        assert tokens[0].type  == TokenType.STRING
        assert tokens[0].value == "hello"

    def test_empty_string(self):
        tokens = Lexer('""').tokenize()
        assert tokens[0].type  == TokenType.STRING
        assert tokens[0].value == ""

    def test_string_with_spaces(self):
        tokens = Lexer('"hello world"').tokenize()
        assert tokens[0].value == "hello world"

    def test_string_with_digits(self):
        tokens = Lexer('"abc123"').tokenize()
        assert tokens[0].value == "abc123"

    def test_escape_newline(self):
        tokens = Lexer('"line1\\nline2"').tokenize()
        assert tokens[0].value == "line1\nline2"

    def test_escape_double_quote(self):
        tokens = Lexer('"say \\"hi\\""').tokenize()
        assert tokens[0].value == 'say "hi"'

    def test_escape_backslash(self):
        tokens = Lexer('"a\\\\b"').tokenize()
        assert tokens[0].value == "a\\b"

    def test_string_location_line(self):
        tokens = Lexer('"hi"').tokenize()
        assert tokens[0].line == 1

    def test_string_location_col(self):
        tokens = Lexer('"hi"').tokenize()
        assert tokens[0].col == 1

    def test_unterminated_string_raises(self):
        with pytest.raises(LexerError):
            Lexer('"not closed').tokenize()

    def test_unterminated_has_location(self):
        with pytest.raises(LexerError) as exc_info:
            Lexer('"oops').tokenize()
        assert exc_info.value.line >= 1

    def test_string_followed_by_eof(self):
        tokens = Lexer('"end"').tokenize()
        assert tokens[-1].type == TokenType.EOF

    def test_string_in_assignment(self):
        tokens = Lexer('x = "hello"').tokenize()
        types  = [t.type for t in tokens[:-1]]
        assert TokenType.STRING in types

    def test_two_strings(self):
        tokens = Lexer('"a" "b"').tokenize()
        assert tokens[0].type == TokenType.STRING
        assert tokens[1].type == TokenType.STRING


# ── Error formatter ────────────────────────────────────────────────────────────

class TestErrorFormatter:
    def _lex_error(self, source: str) -> LexerError:
        try:
            Lexer(source).tokenize()
        except LexerError as e:
            return e
        pytest.fail(f"Expected LexerError for source: {source!r}")

    def test_output_contains_error_type(self):
        err = self._lex_error("1 + @")
        out = format_error("1 + @", err)
        assert "LexerError" in out

    def test_output_contains_source_line(self):
        src = "x = 1 + @"
        err = self._lex_error(src)
        out = format_error(src, err)
        assert src in out

    def test_output_contains_caret(self):
        src = "x = 1 + @"
        err = self._lex_error(src)
        out = format_error(src, err)
        assert "^" in out

    def test_caret_on_correct_column(self):
        src = "@"
        err = self._lex_error(src)
        out = format_error(src, err)
        lines = out.strip().splitlines()
        caret_line = [l for l in lines if "^" in l][0]
        # '@' is col 1 → caret should be at position 2 (after 2-space indent)
        assert caret_line.strip() == "^"

    def test_multiline_points_to_correct_line(self):
        src  = "x = 1\ny = @"
        err  = self._lex_error(src)
        out  = format_error(src, err)
        assert "y = @" in out
        assert "x = 1" not in out   # should show only the offending line

    def test_no_location_still_works(self):
        exc = ValueError("something broke")
        out = format_error("x = 1", exc)
        assert "something broke" in out

    def test_returns_string(self):
        err = self._lex_error("@")
        out = format_error("@", err)
        assert isinstance(out, str)
