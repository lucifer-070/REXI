"""
REXI — Recursive Descent Expression Interpreter
Entry point.

    python main.py           → interactive REPL
    python main.py file.calc → run a .calc script file
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cli import run_repl, run_file


def main():
    if len(sys.argv) == 1:
        run_repl()
    else:
        run_file(sys.argv[1])


if __name__ == "__main__":
    main()
