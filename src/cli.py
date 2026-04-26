"""
cli.py — Interactive REPL and script runner for REXI.

Run modes:
    python main.py            → starts the interactive REPL
    python main.py file.calc  → runs a .calc script file

REPL special commands:
    :exit  or  :quit   → exit
    :env               → show all variables and functions in scope
    :tree <expr>       → show the AST for any expression
    :clear             → reset interpreter (wipe all variables/functions)
    :help              → show command list
"""

import sys
import os

from src.lexer import Lexer, LexerError
from src.parser import Parser, ParseError
from src.interpreter import Interpreter, REXIRuntimeError, BUILTINS
from src.ast_printer import print_ast


BANNER = """
╔══════════════════════════════════════════╗
║   REXI — Recursive Descent Interpreter  ║
║   Type :help for commands, :exit to quit ║
╚══════════════════════════════════════════╝
"""

HELP_TEXT = """
Special REPL commands:
  :exit / :quit    Exit the REPL
  :env             Show all defined variables and functions
  :tree <expr>     Show the AST tree for an expression
  :clear           Reset interpreter (clears all variables and functions)
  :builtins        List all built-in functions
  :help            Show this help message

Language quick-reference:
  x = 42                       variable assignment
  def f(x) = x * 2             function definition
  f(10)                         function call
  if x > 0 then x else -x      conditional expression
  while x > 0 then x = x - 1   while loop
  sqrt(x)  abs(x)  max(a, b)   built-in functions
"""


def _fmt(value) -> str:
    """Convert an interpreter result to a display string."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and value == int(value):
        return str(int(value))
    return str(value)


def _eval(source: str, interp: Interpreter):
    """Run source text through the full Lexer → Parser → Interpreter pipeline."""
    tokens = Lexer(source).tokenize()
    ast    = Parser(tokens).parse()
    return interp.run(ast)


def run_repl():
    """Start the interactive REPL loop."""
    print(BANNER)
    interp = Interpreter()

    while True:
        try:
            line = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not line:
            continue

        # ── Special commands ──────────────────────────────────────────────────

        if line in (":exit", ":quit"):
            print("Bye!")
            break

        if line == ":help":
            print(HELP_TEXT)
            continue

        if line == ":env":
            out = interp.global_env.dump()
            print(out if out.strip() else "(no variables defined)")
            continue

        if line == ":clear":
            interp = Interpreter()
            print("(interpreter reset — all variables cleared)")
            continue

        if line == ":builtins":
            print("Built-in functions:")
            for name in sorted(BUILTINS.keys()):
                print(f"  {name}")
            continue

        if line.startswith(":tree"):
            expr = line[5:].strip()
            if not expr:
                print("Usage: :tree <expression>")
                continue
            try:
                tokens = Lexer(expr).tokenize()
                ast    = Parser(tokens).parse()
                print_ast(ast)
            except (LexerError, ParseError) as e:
                print(e)
            continue

        if line.startswith(":"):
            print(f"Unknown command '{line}'. Type :help for a list.")
            continue

        # ── Normal evaluation ─────────────────────────────────────────────────

        try:
            result  = _eval(line, interp)
            display = _fmt(result)
            if display:
                print(f"=> {display}")
        except (LexerError, ParseError, REXIRuntimeError) as e:
            print(e)


def run_file(filepath: str):
    """Read and execute a .calc script file."""
    if not os.path.exists(filepath):
        print(f"[REXI] File not found: {filepath}")
        sys.exit(1)

    with open(filepath, 'r') as f:
        source = f.read()

    interp = Interpreter()
    try:
        result  = _eval(source, interp)
        display = _fmt(result)
        if display:
            print(display)
    except (LexerError, ParseError, REXIRuntimeError) as e:
        print(e)
        sys.exit(1)
