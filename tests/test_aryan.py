"""
test_aryan.py — Tests for Aryan's contributions:
  - WHILE keyword token (lexer sees it correctly)
  - WhileNode class definition
  - parse_while() grammar rule in the Parser
  - Environment.dump() method
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.lexer import Lexer
from src.tokens import TokenType
from src.parser import Parser, ParseError
from src.ast_nodes import WhileNode, BinOpNode, VarAssignNode, VarAccessNode
from src.environment import Environment


# ── WHILE token ───────────────────────────────────────────────────────────────

class TestWhileToken:
    def test_while_lexed_as_while_type(self):
        tokens = Lexer("while").tokenize()
        assert tokens[0].type == TokenType.WHILE

    def test_while_is_not_identifier(self):
        tokens = Lexer("while").tokenize()
        assert tokens[0].type != TokenType.IDENTIFIER

    def test_while_value(self):
        tokens = Lexer("while").tokenize()
        assert tokens[0].value == "while"

    def test_while_in_context(self):
        tokens = Lexer("while x > 0 then x").tokenize()
        assert tokens[0].type == TokenType.WHILE

    def test_whileloop_not_keyword(self):
        # 'whileloop' is not a keyword — it's an identifier
        tokens = Lexer("whileloop").tokenize()
        assert tokens[0].type == TokenType.IDENTIFIER


# ── WhileNode class ───────────────────────────────────────────────────────────

class TestWhileNode:
    def test_whilenode_importable(self):
        from src.ast_nodes import WhileNode
        assert WhileNode is not None

    def test_whilenode_stores_condition(self):
        from src.ast_nodes import BoolNode, NumberNode
        cond = BoolNode(True)
        body = NumberNode(1)
        node = WhileNode(cond, body)
        assert node.condition is cond

    def test_whilenode_stores_body(self):
        from src.ast_nodes import BoolNode, NumberNode
        cond = BoolNode(False)
        body = NumberNode(99)
        node = WhileNode(cond, body)
        assert node.body is body

    def test_whilenode_default_location(self):
        from src.ast_nodes import BoolNode, NumberNode
        node = WhileNode(BoolNode(True), NumberNode(0))
        assert node.line == 0
        assert node.col  == 0

    def test_whilenode_custom_location(self):
        from src.ast_nodes import BoolNode, NumberNode
        node = WhileNode(BoolNode(True), NumberNode(0), line=5, col=3)
        assert node.line == 5
        assert node.col  == 3

    def test_whilenode_repr_contains_name(self):
        from src.ast_nodes import BoolNode, NumberNode
        node = WhileNode(BoolNode(True), NumberNode(1))
        assert "WhileNode" in repr(node)


# ── Parser: while grammar rule ────────────────────────────────────────────────

class TestWhileParser:
    def _parse_one(self, source: str):
        tokens = Lexer(source).tokenize()
        ast    = Parser(tokens).parse()
        assert len(ast.statements) == 1, f"Expected 1 statement, got {len(ast.statements)}"
        return ast.statements[0]

    def test_while_then_produces_whilenode(self):
        node = self._parse_one("while x > 0 then x")
        assert isinstance(node, WhileNode)

    def test_while_without_then_produces_whilenode(self):
        node = self._parse_one("while x > 0 x")
        assert isinstance(node, WhileNode)

    def test_while_condition_not_none(self):
        node = self._parse_one("while x > 0 then x")
        assert node.condition is not None

    def test_while_body_not_none(self):
        node = self._parse_one("while x > 0 then x")
        assert node.body is not None

    def test_while_condition_is_comparison(self):
        node = self._parse_one("while x > 0 then x")
        assert isinstance(node.condition, BinOpNode)
        assert node.condition.op == '>'

    def test_while_body_is_assignment(self):
        node = self._parse_one("while x > 0 then x = x - 1")
        assert isinstance(node.body, VarAssignNode)

    def test_while_body_is_var_access(self):
        node = self._parse_one("while x > 0 then x")
        assert isinstance(node.body, VarAccessNode)

    def test_while_source_location_line(self):
        node = self._parse_one("while x > 0 then x")
        assert node.line == 1

    def test_while_source_location_col(self):
        node = self._parse_one("while x > 0 then x")
        assert node.col == 1

    def test_while_with_boolean_condition(self):
        from src.ast_nodes import BoolNode
        node = self._parse_one("while true then x")
        assert isinstance(node.condition, BoolNode)


# ── Environment.dump() ────────────────────────────────────────────────────────

class TestEnvironmentDump:
    def test_dump_returns_string(self):
        env = Environment()
        assert isinstance(env.dump(), str)

    def test_dump_global_label(self):
        env = Environment()
        assert "global scope" in env.dump()

    def test_dump_local_label_for_child(self):
        parent = Environment()
        child  = Environment(parent=parent)
        assert "local scope" in child.dump()

    def test_dump_shows_variable_name(self):
        env = Environment()
        env.set("myvar", 42)
        assert "myvar" in env.dump()

    def test_dump_shows_variable_value(self):
        env = Environment()
        env.set("x", 99)
        assert "99" in env.dump()

    def test_dump_shows_both_scope_variables(self):
        parent = Environment()
        parent.set("g", 10)
        child  = Environment(parent=parent)
        child.set("l", 20)
        out = child.dump()
        assert "g" in out
        assert "l" in out

    def test_dump_both_scope_labels(self):
        parent = Environment()
        child  = Environment(parent=parent)
        out = child.dump()
        assert "local scope"  in out
        assert "global scope" in out

    def test_dump_empty_scope(self):
        env = Environment()
        out = env.dump()
        assert "global scope" in out  # at minimum shows the label

    def test_dump_sorted_names(self):
        env = Environment()
        env.set("z", 3)
        env.set("a", 1)
        out = env.dump()
        assert out.index("a") < out.index("z")
