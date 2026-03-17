"""
ast_nodes.py — Abstract Syntax Tree node definitions for REXI.

Each class represents one kind of construct in the REXI language.
The interpreter will walk these nodes recursively to evaluate a program.
"""


class Node:
    """Base class for all AST nodes."""
    pass


# ── Literal / Primary nodes ───────────────────────────────────────────────────

class NumberNode(Node):
    """
    A numeric literal: integer or float.

    Example source:  42   3.14
    """
    def __init__(self, value, line: int = 0, col: int = 0):
        self.value = value   # int or float
        self.line  = line
        self.col   = col

    def __repr__(self):
        return f"NumberNode({self.value!r})"


class BoolNode(Node):
    """
    A boolean literal: true or false.

    Example source:  true   false
    """
    def __init__(self, value: bool, line: int = 0, col: int = 0):
        self.value = value
        self.line  = line
        self.col   = col

    def __repr__(self):
        return f"BoolNode({self.value!r})"


class VarAccessNode(Node):
    """
    Reading the value of a variable.

    Example source:  x   my_var
    """
    def __init__(self, name: str, line: int = 0, col: int = 0):
        self.name = name
        self.line = line
        self.col  = col

    def __repr__(self):
        return f"VarAccessNode({self.name!r})"


# ── Operator nodes ────────────────────────────────────────────────────────────

class BinOpNode(Node):
    """
    A binary operation between two expressions.

    Example source:  a + b   x * (y - 2)
    Fields:
        left  — left-hand Node
        op    — operator string  ('+', '-', '*', '/', '%', '^',
                                   '==', '!=', '<', '>', '<=', '>=',
                                   'and', 'or')
        right — right-hand Node
    """
    def __init__(self, left: Node, op: str, right: Node, line: int = 0, col: int = 0):
        self.left  = left
        self.op    = op
        self.right = right
        self.line  = line
        self.col   = col

    def __repr__(self):
        return f"BinOpNode({self.left!r}, {self.op!r}, {self.right!r})"


class UnaryOpNode(Node):
    """
    A unary operation applied to a single expression.

    Example source:  -x   not flag   +3
    Fields:
        op      — operator string  ('-', '+', 'not')
        operand — the Node being operated on
    """
    def __init__(self, op: str, operand: Node, line: int = 0, col: int = 0):
        self.op      = op
        self.operand = operand
        self.line    = line
        self.col     = col

    def __repr__(self):
        return f"UnaryOpNode({self.op!r}, {self.operand!r})"


# ── Assignment ────────────────────────────────────────────────────────────────

class VarAssignNode(Node):
    """
    Assigning a value to a variable (creates it if it doesn't exist).

    Example source:  x = 5 + 3
    """
    def __init__(self, name: str, value: Node, line: int = 0, col: int = 0):
        self.name  = name
        self.value = value   # the RHS expression node
        self.line  = line
        self.col   = col

    def __repr__(self):
        return f"VarAssignNode({self.name!r}, {self.value!r})"


# ── Function nodes ────────────────────────────────────────────────────────────

class FuncDefNode(Node):
    """
    Defining a user function.

    Example source:  def square(n) = n * n
    Fields:
        name   — function name string
        params — list of parameter name strings
        body   — a single expression Node (or a BlockNode for multi-line bodies)
    """
    def __init__(self, name: str, params: list, body: Node, line: int = 0, col: int = 0):
        self.name   = name
        self.params = params   # ['n', 'm', ...]
        self.body   = body
        self.line   = line
        self.col    = col

    def __repr__(self):
        return f"FuncDefNode({self.name!r}, params={self.params!r}, body={self.body!r})"


class FuncCallNode(Node):
    """
    Calling a function (built-in or user-defined).

    Example source:  sqrt(9)   add(x, 2)
    Fields:
        name — function name string
        args — list of argument expression Nodes
    """
    def __init__(self, name: str, args: list, line: int = 0, col: int = 0):
        self.name = name
        self.args = args   # [Node, ...]
        self.line = line
        self.col  = col

    def __repr__(self):
        return f"FuncCallNode({self.name!r}, args={self.args!r})"


# ── Control flow nodes ────────────────────────────────────────────────────────

class IfNode(Node):
    """
    A conditional if-else expression.

    Example source:  if x > 0 then x else -x
    Fields:
        condition  — boolean expression Node
        then_body  — Node evaluated when condition is truthy
        else_body  — Node evaluated when condition is falsy (may be None)
    """
    def __init__(self, condition: Node, then_body: Node, else_body=None, line: int = 0, col: int = 0):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body   # optional
        self.line      = line
        self.col       = col

    def __repr__(self):
        return (f"IfNode(condition={self.condition!r}, "
                f"then={self.then_body!r}, else={self.else_body!r})")


class ReturnNode(Node):
    """
    A return statement inside a function body.

    Example source:  return x * 2
    """
    def __init__(self, value: Node, line: int = 0, col: int = 0):
        self.value = value
        self.line  = line
        self.col   = col

    def __repr__(self):
        return f"ReturnNode({self.value!r})"


# ── Block node ────────────────────────────────────────────────────────────────

class BlockNode(Node):
    """
    A sequence of statements (used as a function body or program root).

    Fields:
        statements — list of Node objects, executed in order
    """
    def __init__(self, statements: list, line: int = 0, col: int = 0):
        self.statements = statements
        self.line       = line
        self.col        = col

    def __repr__(self):
        return f"BlockNode({self.statements!r})"
