"""
lexer.py — Lexer (tokenizer) for REXI.

Converts a raw source string into a flat list of Token objects.
Raises LexerError on unrecognised characters.
"""

from src.tokens import Token, TokenType, KEYWORDS


# ── Custom exception ──────────────────────────────────────────────────────────

class LexerError(Exception):
    """Raised when the lexer encounters an unexpected character."""

    def __init__(self, message: str, line: int, col: int):
        super().__init__(f"[LexerError] Line {line}, Col {col}: {message}")
        self.line = line
        self.col  = col


# ── Lexer class ───────────────────────────────────────────────────────────────

class Lexer:
    """
    Converts source text into a list of tokens.

    Usage:
        lexer = Lexer(source_text)
        tokens = lexer.tokenize()
    """

    def __init__(self, source: str):
        self.source  = source
        self.pos     = 0              # current character index
        self.line    = 1
        self.col     = 1
        self.tokens  = []

    # ── Internal helpers ──────────────────────────────────────────────────────

    @property
    def current_char(self):
        """Character at the current position, or None if past end."""
        return self.source[self.pos] if self.pos < len(self.source) else None

    def peek(self, offset: int = 1):
        """Look ahead without consuming."""
        idx = self.pos + offset
        return self.source[idx] if idx < len(self.source) else None

    def advance(self):
        """Consume the current character and move forward."""
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
            self.col   = 1
        else:
            self.col += 1
        return ch

    def _mark(self):
        """Return (line, col) of the current position, for token location."""
        return self.line, self.col

    # ── Skipping ──────────────────────────────────────────────────────────────

    def skip_whitespace(self):
        """Skip spaces and tabs (but NOT newlines — those are statement separators)."""
        while self.current_char is not None and self.current_char in (' ', '\t', '\r'):
            self.advance()

    def skip_line_comment(self):
        """Skip from # to end of line."""
        while self.current_char is not None and self.current_char != '\n':
            self.advance()

    # ── Readers ───────────────────────────────────────────────────────────────

    def read_number(self, line: int, col: int) -> Token:
        """
        Read an integer or floating-point literal.
        Supports: 42, 3.14, .5
        """
        buf   = []
        is_float = False

        # Leading decimal point, e.g. .5
        if self.current_char == '.':
            is_float = True
            buf.append(self.advance())

        while self.current_char is not None and self.current_char.isdigit():
            buf.append(self.advance())

        # Decimal part (only if we haven't had a dot yet)
        if not is_float and self.current_char == '.' and (self.peek() is None or self.peek().isdigit()):
            is_float = True
            buf.append(self.advance())
            while self.current_char is not None and self.current_char.isdigit():
                buf.append(self.advance())

        raw = ''.join(buf)
        value = float(raw) if is_float else int(raw)
        return Token(TokenType.NUMBER, value, line, col)

    def read_identifier_or_keyword(self, line: int, col: int) -> Token:
        """Read an identifier and check if it is a reserved keyword."""
        buf = []
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            buf.append(self.advance())
        name = ''.join(buf)
        tok_type = KEYWORDS.get(name, TokenType.IDENTIFIER)
        # Boolean literals become NUMBER tokens (True→1, False→0) for easy eval
        if tok_type == TokenType.TRUE:
            return Token(TokenType.TRUE, True, line, col)
        if tok_type == TokenType.FALSE:
            return Token(TokenType.FALSE, False, line, col)
        return Token(tok_type, name, line, col)

    # ── Main tokenise loop ────────────────────────────────────────────────────

    def tokenize(self) -> list:
        """
        Convert the entire source string to a list of Token objects.
        The list always ends with an EOF token.
        """
        tokens = []

        while self.current_char is not None:
            self.skip_whitespace()

            if self.current_char is None:
                break

            line, col = self._mark()
            ch = self.current_char

            # ── Comment ───────────────────────────────────────
            if ch == '#':
                self.skip_line_comment()
                continue

            # ── Newline / semicolon (statement separators) ────
            if ch == '\n':
                self.advance()
                tokens.append(Token(TokenType.NEWLINE, '\n', line, col))
                continue

            if ch == ';':
                self.advance()
                tokens.append(Token(TokenType.SEMICOL, ';', line, col))
                continue

            # ── Number literal ────────────────────────────────
            if ch.isdigit() or (ch == '.' and self.peek() is not None and self.peek().isdigit()):
                tokens.append(self.read_number(line, col))
                continue

            # ── Identifier / keyword ──────────────────────────
            if ch.isalpha() or ch == '_':
                tokens.append(self.read_identifier_or_keyword(line, col))
                continue

            # ── Two-character operators ───────────────────────
            two = ch + (self.peek() or '')
            if two == '==':
                self.advance(); self.advance()
                tokens.append(Token(TokenType.EQ,  '==', line, col)); continue
            if two == '!=':
                self.advance(); self.advance()
                tokens.append(Token(TokenType.NEQ, '!=', line, col)); continue
            if two == '<=':
                self.advance(); self.advance()
                tokens.append(Token(TokenType.LTE, '<=', line, col)); continue
            if two == '>=':
                self.advance(); self.advance()
                tokens.append(Token(TokenType.GTE, '>=', line, col)); continue

            # ── Single-character operators & delimiters ───────
            single_map = {
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.MUL,
                '/': TokenType.DIV,
                '%': TokenType.MOD,
                '^': TokenType.POWER,
                '=': TokenType.ASSIGN,
                '<': TokenType.LT,
                '>': TokenType.GT,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                ',': TokenType.COMMA,
            }
            if ch in single_map:
                self.advance()
                tokens.append(Token(single_map[ch], ch, line, col))
                continue

            # ── Unknown character ─────────────────────────────
            raise LexerError(f"Unexpected character {ch!r}", line, col)

        tokens.append(Token(TokenType.EOF, None, self.line, self.col))
        return tokens
