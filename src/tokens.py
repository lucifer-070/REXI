"""
tokens.py — Token types and Token data class for REXI.

Defines every kind of token the lexer can produce.
"""

from enum import Enum, auto


class TokenType(Enum):
    # ── Literals ──────────────────────────────────────────────
    NUMBER      = auto()   # integer or float literal
    STRING      = auto()   # (reserved for future use)
    IDENTIFIER  = auto()   # variable / function name

    # ── Arithmetic operators ───────────────────────────────────
    PLUS    = auto()   # +
    MINUS   = auto()   # -
    MUL     = auto()   # *
    DIV     = auto()   # /
    MOD     = auto()   # %
    POWER   = auto()   # ^

    # ── Comparison operators ───────────────────────────────────
    EQ      = auto()   # ==
    NEQ     = auto()   # !=
    LT      = auto()   # <
    GT      = auto()   # >
    LTE     = auto()   # <=
    GTE     = auto()   # >=

    # ── Assignment ────────────────────────────────────────────
    ASSIGN  = auto()   # =

    # ── Logical operators (keywords) ──────────────────────────
    AND     = auto()   # and
    OR      = auto()   # or
    NOT     = auto()   # not

    # ── Keywords ──────────────────────────────────────────────
    IF      = auto()   # if
    ELSE    = auto()   # else
    DEF     = auto()   # def
    RETURN  = auto()   # return
    TRUE    = auto()   # true
    FALSE   = auto()   # false
    WHILE   = auto()   # while

    # ── Delimiters ────────────────────────────────────────────
    LPAREN  = auto()   # (
    RPAREN  = auto()   # )
    LBRACE  = auto()   # {  (block open)
    RBRACE  = auto()   # }  (block close)
    COMMA   = auto()   # ,
    NEWLINE = auto()   # \n (statement separator)
    SEMICOL = auto()   # ;  (alternative statement separator)

    # ── Control ───────────────────────────────────────────────
    EOF     = auto()   # end of input


# Map keyword strings → their TokenType
KEYWORDS = {
    "and":    TokenType.AND,
    "or":     TokenType.OR,
    "not":    TokenType.NOT,
    "if":     TokenType.IF,
    "else":   TokenType.ELSE,
    "def":    TokenType.DEF,
    "return": TokenType.RETURN,
    "true":   TokenType.TRUE,
    "false":  TokenType.FALSE,
    "while":  TokenType.WHILE,
}


class Token:
    """A single lexical token with its type, value, and source location."""

    __slots__ = ("type", "value", "line", "col")

    def __init__(self, type_: TokenType, value, line: int = 0, col: int = 0):
        self.type  = type_
        self.value = value
        self.line  = line
        self.col   = col

    def __repr__(self):
        return f"Token({self.type.name}, {self.value!r}, line={self.line}, col={self.col})"

    def __eq__(self, other):
        if not isinstance(other, Token):
            return NotImplemented
        return self.type == other.type and self.value == other.value
