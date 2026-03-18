"""
ast_printer.py — Pretty-print an AST as an indented tree for REXI.

Usage:
    from src.ast_printer import print_ast
    print_ast(ast_node)

Or from the command line:
    python -c "
    from src.lexer import Lexer
    from src.parser import Parser
    from src.ast_printer import print_ast
    tokens = Lexer('1 + 2 * (3 + 4)').tokenize()
    ast = Parser(tokens).parse()
    print_ast(ast)
    "
"""

from src.ast_nodes import (
    NumberNode, BoolNode, VarAccessNode,
    BinOpNode, UnaryOpNode,
    VarAssignNode, FuncDefNode, FuncCallNode,
    IfNode, ReturnNode, BlockNode,
)


def _node_label(node) -> tuple:
    """
    Return (label, children) for a given node.
    label    — the string shown on this tree line
    children — list of child nodes to recurse into
    """
    if isinstance(node, NumberNode):
        return f"Number({node.value!r})", []

    if isinstance(node, BoolNode):
        return f"Bool({'true' if node.value else 'false'})", []

    if isinstance(node, VarAccessNode):
        return f"Var({node.name!r})", []

    if isinstance(node, VarAssignNode):
        return f"Assign({node.name!r})", [node.value]

    if isinstance(node, BinOpNode):
        return f"BinOp({node.op!r})", [node.left, node.right]

    if isinstance(node, UnaryOpNode):
        return f"UnaryOp({node.op!r})", [node.operand]

    if isinstance(node, FuncDefNode):
        params = ', '.join(node.params) or '(none)'
        return f"FuncDef({node.name!r}, params=[{params}])", [node.body]

    if isinstance(node, FuncCallNode):
        return f"FuncCall({node.name!r})", node.args

    if isinstance(node, IfNode):
        children = [node.condition, node.then_body]
        if node.else_body is not None:
            children.append(node.else_body)
        labels = ["cond", "then"]
        if node.else_body is not None:
            labels.append("else")
        return "If", list(zip(labels, children))   # signal labelled children

    if isinstance(node, ReturnNode):
        return "Return", [node.value]

    if isinstance(node, BlockNode):
        return "Block", node.statements

    return type(node).__name__, []


def _render(node, prefix: str, is_last: bool, lines: list, label_override: str = None):
    """Recursively build tree lines."""
    connector = "└── " if is_last else "├── "
    extension = "    " if is_last else "│   "

    node_label, children = _node_label(node)
    display = label_override + ": " + node_label if label_override else node_label
    lines.append(prefix + connector + display)

    child_prefix = prefix + extension

    # Children can be plain nodes OR (label, node) tuples (for IfNode branches)
    for i, child in enumerate(children):
        child_is_last = (i == len(children) - 1)
        if isinstance(child, tuple):
            lbl, actual_node = child
            _render(actual_node, child_prefix, child_is_last, lines, label_override=lbl)
        else:
            _render(child, child_prefix, child_is_last, lines)


def format_ast(node) -> str:
    """Return the AST as a multi-line tree string."""
    lines = []

    # Special-case BlockNode at root: don't show the connector for the root
    if isinstance(node, BlockNode):
        lines.append("Block")
        for i, stmt in enumerate(node.statements):
            _render(stmt, "", i == len(node.statements) - 1, lines)
    else:
        node_label, children = _node_label(node)
        lines.append(node_label)
        for i, child in enumerate(children):
            child_is_last = (i == len(children) - 1)
            if isinstance(child, tuple):
                lbl, actual_node = child
                _render(actual_node, "", child_is_last, lines, label_override=lbl)
            else:
                _render(child, "", child_is_last, lines)

    return "\n".join(lines)


def print_ast(node):
    """Print the AST tree to stdout."""
    print(format_ast(node))
