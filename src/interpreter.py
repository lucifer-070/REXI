"""
interpreter.py — AST evaluator for REXI.

Walks the AST produced by the Parser and computes values.
Each node type has a corresponding visit_* method.

Raises:
    REXIRuntimeError  — undefined variable, wrong arg count, etc.
    ReturnSignal      — internal exception used to unwind function returns
"""

import math
from src.ast_nodes import (
    NumberNode, BoolNode, VarAccessNode,
    BinOpNode, UnaryOpNode,
    VarAssignNode, FuncDefNode, FuncCallNode,
    IfNode, ReturnNode, BlockNode, WhileNode,
)
from src.environment import Environment


# ── Internal signals & exceptions ────────────────────────────────────────────

class ReturnSignal(Exception):
    """Raised by ReturnNode to unwind the call stack back to visit_FuncCallNode."""
    def __init__(self, value):
        self.value = value


class REXIRuntimeError(Exception):
    """A user-visible runtime error with an optional source location."""
    def __init__(self, message: str, line: int = 0, col: int = 0):
        location = f" (line {line}, col {col})" if line else ""
        super().__init__(f"[RuntimeError]{location}: {message}")
        self.line = line
        self.col  = col


# ── Built-in function registry ────────────────────────────────────────────────

def _builtin_sqrt(args):
    _expect_args('sqrt', args, 1)
    x = args[0]
    if x < 0:
        raise REXIRuntimeError("sqrt() argument must be non-negative")
    return math.sqrt(x)

def _builtin_abs(args):
    _expect_args('abs', args, 1)
    return abs(args[0])

def _builtin_max(args):
    if len(args) < 2:
        raise REXIRuntimeError("max() requires at least 2 arguments")
    return max(args)

def _builtin_min(args):
    if len(args) < 2:
        raise REXIRuntimeError("min() requires at least 2 arguments")
    return min(args)

def _builtin_pow(args):
    _expect_args('pow', args, 2)
    return args[0] ** args[1]

def _builtin_floor(args):
    _expect_args('floor', args, 1)
    return math.floor(args[0])

def _builtin_ceil(args):
    _expect_args('ceil', args, 1)
    return math.ceil(args[0])

def _builtin_round(args):
    _expect_args('round', args, 1)
    return round(args[0])

def _builtin_print(args):
    print(*[_format_value(a) for a in args])
    return None

def _expect_args(name: str, args: list, count: int):
    if len(args) != count:
        raise REXIRuntimeError(
            f"{name}() takes {count} argument(s), got {len(args)}"
        )

BUILTINS = {
    'sqrt':  _builtin_sqrt,
    'abs':   _builtin_abs,
    'max':   _builtin_max,
    'min':   _builtin_min,
    'pow':   _builtin_pow,
    'floor': _builtin_floor,
    'ceil':  _builtin_ceil,
    'round': _builtin_round,
    'print': _builtin_print,
}


def _format_value(value) -> str:
    """Convert a REXI value to a human-readable string."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and value == int(value):
        return str(int(value))    # show 4.0 as 4
    return str(value)


# ── Interpreter ───────────────────────────────────────────────────────────────

class Interpreter:
    """
    Tree-walking interpreter.

    Usage:
        interp = Interpreter()
        result = interp.run(ast)   # ast from Parser.parse()
    """

    def __init__(self):
        self.global_env = Environment()

    def run(self, node, env: Environment = None):
        """Public entry point. Pass a BlockNode (full program) or any single node."""
        if env is None:
            env = self.global_env
        return self.visit(node, env)

    # ── Dispatch ──────────────────────────────────────────────────────────────

    def visit(self, node, env: Environment):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.visit_unknown)
        return method(node, env)

    def visit_unknown(self, node, env):
        raise REXIRuntimeError(f"Unknown AST node type: {type(node).__name__}")

    # ── Literal nodes ─────────────────────────────────────────────────────────

    def visit_NumberNode(self, node: NumberNode, env: Environment):
        return node.value

    def visit_BoolNode(self, node: BoolNode, env: Environment):
        return node.value

    # ── Variable nodes ────────────────────────────────────────────────────────

    def visit_VarAccessNode(self, node: VarAccessNode, env: Environment):
        try:
            return env.get(node.name)
        except NameError:
            raise REXIRuntimeError(
                f"Undefined variable '{node.name}'", node.line, node.col
            )

    def visit_VarAssignNode(self, node: VarAssignNode, env: Environment):
        value = self.visit(node.value, env)
        env.set(node.name, value)
        return value

    # ── Operator nodes ────────────────────────────────────────────────────────

    def visit_UnaryOpNode(self, node: UnaryOpNode, env: Environment):
        operand = self.visit(node.operand, env)
        if node.op == '-':
            return -operand
        if node.op == '+':
            return +operand
        if node.op == 'not':
            return not operand
        raise REXIRuntimeError(f"Unknown unary operator '{node.op}'")

    def visit_BinOpNode(self, node: BinOpNode, env: Environment):
        # Short-circuit logical operators
        if node.op == 'and':
            return self.visit(node.left, env) and self.visit(node.right, env)
        if node.op == 'or':
            return self.visit(node.left, env) or  self.visit(node.right, env)

        left  = self.visit(node.left,  env)
        right = self.visit(node.right, env)

        if node.op == '+':   return left + right
        if node.op == '-':   return left - right
        if node.op == '*':   return left * right
        if node.op == '%':   return left % right
        if node.op == '^':   return left ** right
        if node.op == '==':  return left == right
        if node.op == '!=':  return left != right
        if node.op == '<':   return left <  right
        if node.op == '>':   return left >  right
        if node.op == '<=':  return left <= right
        if node.op == '>=':  return left >= right

        if node.op == '/':
            if right == 0:
                raise REXIRuntimeError(
                    "Division by zero", node.line, node.col
                )
            return left / right

        raise REXIRuntimeError(f"Unknown binary operator '{node.op}'")

    # ── Function nodes ────────────────────────────────────────────────────────

    def visit_FuncDefNode(self, node: FuncDefNode, env: Environment):
        """Store the function definition (node + closure env) in the environment."""
        env.set(node.name, node)   # store the AST node itself as the callable
        return f"<function {node.name}>"

    def visit_FuncCallNode(self, node: FuncCallNode, env: Environment):
        name = node.name

        # Evaluate all argument expressions in the CALLING scope
        args = [self.visit(arg, env) for arg in node.args]

        # ── Built-in? ──────────────────────────────────────────
        if name in BUILTINS:
            return BUILTINS[name](args)

        # ── User-defined? ──────────────────────────────────────
        try:
            func = env.get(name)
        except NameError:
            raise REXIRuntimeError(
                f"Undefined function '{name}'", node.line, node.col
            )

        if not isinstance(func, FuncDefNode):
            raise REXIRuntimeError(
                f"'{name}' is not a function", node.line, node.col
            )

        if len(args) != len(func.params):
            raise REXIRuntimeError(
                f"'{name}' takes {len(func.params)} argument(s), got {len(args)}",
                node.line, node.col
            )

        # Create a new child scope with parameter bindings
        local_env = Environment(parent=env)
        for param, value in zip(func.params, args):
            local_env.set(param, value)

        # Execute the function body
        try:
            result = self.visit(func.body, local_env)
        except ReturnSignal as ret:
            result = ret.value

        return result

    # ── Control flow ──────────────────────────────────────────────────────────

    def visit_IfNode(self, node: IfNode, env: Environment):
        condition = self.visit(node.condition, env)
        if condition:
            return self.visit(node.then_body, env)
        elif node.else_body is not None:
            return self.visit(node.else_body, env)
        return None

    def visit_WhileNode(self, node: WhileNode, env: Environment):
        """
        Execute the body expression repeatedly while the condition is truthy.

        Returns the last value produced by the body, or None if the body
        never ran (condition was false from the start).

        A safety cap of 100,000 iterations prevents accidental infinite loops
        from hanging the REPL.
        """
        result    = None
        max_iters = 100_000
        iters     = 0

        while self.visit(node.condition, env):
            result  = self.visit(node.body, env)
            iters  += 1
            if iters >= max_iters:
                raise REXIRuntimeError(
                    f"While loop exceeded {max_iters} iterations — "
                    f"possible infinite loop",
                    node.line, node.col
                )

        return result

    def visit_ReturnNode(self, node: ReturnNode, env: Environment):
        value = self.visit(node.value, env)
        raise ReturnSignal(value)

    # ── Block ─────────────────────────────────────────────────────────────────

    def visit_BlockNode(self, node: BlockNode, env: Environment):
        """Execute statements in order; return the value of the last one."""
        result = None
        for stmt in node.statements:
            result = self.visit(stmt, env)
        return result
