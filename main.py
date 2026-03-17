"""
REXI — Recursive Descent Expression Interpreter
Entry point.

Phase 5+: runs the interpreter pipeline (Lexer → Parser → Interpreter).
Phase 7:  full CLI / REPL will replace this.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.lexer import Lexer, LexerError
from src.parser import Parser, ParseError
from src.interpreter import Interpreter, REXIRuntimeError


def evaluate(source: str, interp: Interpreter):
    """Run one snippet through the full pipeline and return the result."""
    tokens = Lexer(source).tokenize()
    ast    = Parser(tokens).parse()
    return interp.run(ast)


def format_result(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and value == int(value):
        return str(int(value))
    return str(value)


def main():
    interp = Interpreter()

    # ── Demo mode (no arguments) ──────────────────────────────────────────────
    if len(sys.argv) == 1:
        print("REXI Interpreter — Phase 5 Demo")
        print("=" * 40)

        demo_lines = [
            ("Arithmetic",           "2 + 3 * (10 - 4)"),
            ("Power",                "2 ^ 10"),
            ("Variable assignment",  "x = 42"),
            ("Variable use",         "x + 8"),
            ("Built-in sqrt",        "sqrt(144)"),
            ("Built-in max",         "max(3, 7, 2)"),
            ("User function def",    "def square(n) = n * n"),
            ("User function call",   "square(9)"),
            ("Recursive factorial",  "def fact(n) = if n <= 1 then 1 else n * fact(n - 1)"),
            ("fact(7)",              "fact(7)"),
            ("If-else expression",   "if x > 10 then x * 2 else x / 2"),
            ("Boolean",              "not (1 == 2)"),
        ]

        for label, code in demo_lines:
            try:
                result = evaluate(code, interp)
                display = format_result(result)
                print(f"  {label}")
                print(f"    >> {code}")
                if display:
                    print(f"    => {display}")
            except (LexerError, ParseError, REXIRuntimeError) as e:
                print(f"    !! {e}")
            print()
        return

    # ── Script file mode ──────────────────────────────────────────────────────
    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"[REXI] File not found: {filepath}")
        sys.exit(1)

    with open(filepath, 'r') as f:
        source = f.read()

    try:
        result = evaluate(source, interp)
        if result is not None:
            print(format_result(result))
    except (LexerError, ParseError, REXIRuntimeError) as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
