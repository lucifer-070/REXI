"""
parser.py — Recursive Descent Parser for REXI.

Consumes a flat list of tokens (from the Lexer) and produces an AST.
Raises ParseError on unexpected or missing tokens.

Grammar (simplified, precedence low → high):
    program      ::= statement* EOF
    statement    ::= func_def | var_assign | if_expr | return_stmt | expression
    func_def     ::= DEF IDENTIFIER LPAREN params RPAREN ASSIGN expression
    var_assign   ::= IDENTIFIER ASSIGN expression
    return_stmt  ::= RETURN expression
    if_expr      ::= IF expression THEN expression (ELSE expression)?
    expression   ::= or_expr
    or_expr      ::= and_expr (OR and_expr)*
    and_expr     ::= not_expr (AND not_expr)*
    not_expr     ::= NOT not_expr | comparison
    comparison   ::= additive ((EQ|NEQ|LT|GT|LTE|GTE) additive)*
    additive     ::= multiplicative ((PLUS|MINUS) multiplicative)*
    multiplicative ::= unary ((MUL|DIV|MOD) unary)*
    unary        ::= (PLUS|MINUS) unary | power
    power        ::= primary (POWER unary)*   ← right-associative
    primary      ::= NUMBER | TRUE | FALSE | IDENTIFIER [LPAREN args RPAREN]
                   | LPAREN expression RPAREN
"""

from src.tokens import TokenType, Token
from src.ast_nodes import (
    NumberNode, BoolNode, VarAccessNode,
    BinOpNode, UnaryOpNode,
    VarAssignNode, FuncDefNode, FuncCallNode,
    IfNode, ReturnNode, BlockNode, WhileNode,
)


# ── Custom exception ──────────────────────────────────────────────────────────

class ParseError(Exception):
    """Raised when the parser encounters an unexpected token."""

    def __init__(self, message: str, line: int, col: int):
        super().__init__(f"[ParseError] Line {line}, Col {col}: {message}")
        self.line = line
        self.col  = col


# ── Parser class ──────────────────────────────────────────────────────────────

class Parser:
    """
    Recursive-descent parser.

    Usage:
        parser = Parser(tokens)   # tokens from Lexer.tokenize()
        ast    = parser.parse()   # returns a BlockNode (the program root)
    """

    def __init__(self, tokens: list):
        self.tokens  = tokens
        self.pos     = 0

    # ── Token navigation helpers ──────────────────────────────────────────────

    def current(self) -> Token:
        return self.tokens[self.pos]

    def peek(self, offset: int = 1) -> Token:
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else self.tokens[-1]

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def expect(self, *types: TokenType) -> Token:
        """Consume the current token if it matches one of the given types; raise otherwise."""
        tok = self.current()
        if tok.type not in types:
            expected = ' or '.join(t.name for t in types)
            raise ParseError(
                f"Expected {expected}, got {tok.type.name} ({tok.value!r})",
                tok.line, tok.col
            )
        return self.advance()

    def match(self, *types: TokenType) -> bool:
        """Return True (and advance) if the current token matches any of the given types."""
        if self.current().type in types:
            self.advance()
            return True
        return False

    def skip_newlines(self):
        """Skip one or more NEWLINE / SEMICOL tokens."""
        while self.current().type in (TokenType.NEWLINE, TokenType.SEMICOL):
            self.advance()

    # ── Entry point ───────────────────────────────────────────────────────────

    def parse(self) -> BlockNode:
        """Parse the full token stream and return the program as a BlockNode."""
        self.skip_newlines()
        statements = []
        while self.current().type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self.skip_newlines()
        return BlockNode(statements)

    # ── Statement dispatcher ──────────────────────────────────────────────────

    def parse_statement(self):
        """Choose which kind of statement to parse based on the current token."""
        tok = self.current()

        if tok.type == TokenType.DEF:
            return self.parse_func_def()

        if tok.type == TokenType.RETURN:
            return self.parse_return()

        if tok.type == TokenType.IF:
            return self.parse_if()

        if tok.type == TokenType.WHILE:
            return self.parse_while()

        # Assignment: IDENTIFIER ASSIGN ...   vs just a bare expression
        if (tok.type == TokenType.IDENTIFIER
                and self.peek().type == TokenType.ASSIGN):
            return self.parse_var_assign()

        return self.parse_expression()

    # ── Function definition ───────────────────────────────────────────────────

    def parse_func_def(self) -> FuncDefNode:
        """
        def name(param1, param2) = body_expression
        """
        tok = self.expect(TokenType.DEF)
        name_tok = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.LPAREN)

        params = []
        if self.current().type != TokenType.RPAREN:
            params.append(self.expect(TokenType.IDENTIFIER).value)
            while self.current().type == TokenType.COMMA:
                self.advance()
                params.append(self.expect(TokenType.IDENTIFIER).value)

        self.expect(TokenType.RPAREN)
        self.expect(TokenType.ASSIGN)

        body = self.parse_expression()
        return FuncDefNode(name_tok.value, params, body, tok.line, tok.col)

    # ── Variable assignment ───────────────────────────────────────────────────

    def parse_var_assign(self) -> VarAssignNode:
        """
        name = expression
        """
        name_tok = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        return VarAssignNode(name_tok.value, value, name_tok.line, name_tok.col)

    # ── Return statement ──────────────────────────────────────────────────────

    def parse_return(self) -> ReturnNode:
        tok = self.expect(TokenType.RETURN)
        value = self.parse_expression()
        return ReturnNode(value, tok.line, tok.col)

    # ── If expression ─────────────────────────────────────────────────────────

    def parse_if(self) -> IfNode:
        """
        if condition then then_expr [else else_expr]
        'then' is not a keyword — we just parse the condition up to ELSE/NEWLINE/EOF
        and treat the next expression as the then-branch.
        """
        tok = self.expect(TokenType.IF)
        condition = self.parse_expression()

        # Optional 'then' keyword (we treat it as an IDENTIFIER to avoid adding a token type)
        if self.current().type == TokenType.IDENTIFIER and self.current().value == 'then':
            self.advance()

        then_body = self.parse_expression()

        else_body = None
        if self.current().type == TokenType.ELSE:
            self.advance()
            else_body = self.parse_expression()

        return IfNode(condition, then_body, else_body, tok.line, tok.col)

    # ── While statement ───────────────────────────────────────────────────────

    def parse_while(self) -> WhileNode:
        """
        Grammar rule:
            while_stmt ::= WHILE expression [IDENTIFIER('then')] expression

        'then' is optional — the parser accepts it if present but does not require it.

        Examples:
            while x > 0 then x = x - 1
            while x > 0 x = x - 1        (no 'then', also valid)
        """
        tok = self.expect(TokenType.WHILE)
        condition = self.parse_expression()

        # Accept optional 'then' keyword (it reads as IDENTIFIER since there's no THEN token)
        if self.current().type == TokenType.IDENTIFIER and self.current().value == 'then':
            self.advance()

        # Block body: while x > 0 { x = x - 1; print(x) }
        if self.current().type == TokenType.LBRACE:
            body = self.parse_block_body()
        else:
            body = self.parse_statement()
        return WhileNode(condition, body, tok.line, tok.col)

    # ── Expression hierarchy (precedence: low → high) ─────────────────────────


    # ── Block body ────────────────────────────────────────────────────────────

    def parse_block_body(self):
        """
        Parse a { stmt; stmt; ... } block into a BlockNode.

        Statements are separated by newlines or semicolons.
        Examples:
            while cond { stmt1; stmt2 }
            while cond {
                stmt1
                stmt2
            }
        """
        tok = self.expect(TokenType.LBRACE)
        self.skip_newlines()
        statements = []
        while self.current().type not in (TokenType.RBRACE, TokenType.EOF):
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self.skip_newlines()
        if self.current().type == TokenType.EOF:
            raise ParseError(
                "Unclosed block body — expected '}'",
                tok.line, tok.col
            )
        self.expect(TokenType.RBRACE)
        return BlockNode(statements, tok.line, tok.col)

    def parse_expression(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.current().type == TokenType.OR:
            op_tok = self.advance()
            right  = self.parse_and()
            left   = BinOpNode(left, 'or', right, op_tok.line, op_tok.col)
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.current().type == TokenType.AND:
            op_tok = self.advance()
            right  = self.parse_not()
            left   = BinOpNode(left, 'and', right, op_tok.line, op_tok.col)
        return left

    def parse_not(self):
        if self.current().type == TokenType.NOT:
            op_tok = self.advance()
            operand = self.parse_not()   # right-recursive
            return UnaryOpNode('not', operand, op_tok.line, op_tok.col)
        return self.parse_comparison()

    def parse_comparison(self):
        COMP_TYPES = {
            TokenType.EQ:  '==',
            TokenType.NEQ: '!=',
            TokenType.LT:  '<',
            TokenType.GT:  '>',
            TokenType.LTE: '<=',
            TokenType.GTE: '>=',
        }
        left = self.parse_additive()
        while self.current().type in COMP_TYPES:
            op_tok = self.advance()
            right  = self.parse_additive()
            left   = BinOpNode(left, COMP_TYPES[op_tok.type], right, op_tok.line, op_tok.col)
        return left

    def parse_additive(self):
        left = self.parse_multiplicative()
        while self.current().type in (TokenType.PLUS, TokenType.MINUS):
            op_tok = self.advance()
            right  = self.parse_multiplicative()
            left   = BinOpNode(left, op_tok.value, right, op_tok.line, op_tok.col)
        return left

    def parse_multiplicative(self):
        left = self.parse_unary()
        while self.current().type in (TokenType.MUL, TokenType.DIV, TokenType.MOD):
            op_tok = self.advance()
            right  = self.parse_unary()
            left   = BinOpNode(left, op_tok.value, right, op_tok.line, op_tok.col)
        return left

    def parse_unary(self):
        if self.current().type in (TokenType.PLUS, TokenType.MINUS):
            op_tok = self.advance()
            operand = self.parse_unary()   # right-recursive
            return UnaryOpNode(op_tok.value, operand, op_tok.line, op_tok.col)
        return self.parse_power()

    def parse_power(self):
        """^ is right-associative: 2^3^2  ==  2^(3^2)."""
        base = self.parse_primary()
        if self.current().type == TokenType.POWER:
            op_tok = self.advance()
            exp    = self.parse_unary()   # right-recursive through unary
            return BinOpNode(base, '^', exp, op_tok.line, op_tok.col)
        return base

    # ── Primary (atoms) ───────────────────────────────────────────────────────

    def parse_primary(self):
        tok = self.current()

        # Number literal
        if tok.type == TokenType.NUMBER:
            self.advance()
            return NumberNode(tok.value, tok.line, tok.col)

        # Boolean literals
        if tok.type == TokenType.TRUE:
            self.advance()
            return BoolNode(True, tok.line, tok.col)
        if tok.type == TokenType.FALSE:
            self.advance()
            return BoolNode(False, tok.line, tok.col)

        # Identifier — either a variable access or a function call
        if tok.type == TokenType.IDENTIFIER:
            self.advance()
            if self.current().type == TokenType.LPAREN:
                # Function call: name(arg1, arg2, ...)
                self.advance()   # consume '('
                args = []
                if self.current().type != TokenType.RPAREN:
                    args.append(self.parse_expression())
                    while self.current().type == TokenType.COMMA:
                        self.advance()
                        args.append(self.parse_expression())
                self.expect(TokenType.RPAREN)
                return FuncCallNode(tok.value, args, tok.line, tok.col)
            # Plain variable
            return VarAccessNode(tok.value, tok.line, tok.col)

        # Parenthesised expression
        if tok.type == TokenType.LPAREN:
            self.advance()
            node = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return node

        # Nested if expression
        if tok.type == TokenType.IF:
            return self.parse_if()

        # Allow 'while' as a nested expression
        if tok.type == TokenType.WHILE:
            return self.parse_while()

        raise ParseError(
            f"Unexpected token {tok.type.name} ({tok.value!r})",
            tok.line, tok.col
        )
