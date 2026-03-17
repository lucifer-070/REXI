"""
REXI — Recursive Descent Expression Interpreter
Entry point: starts the REPL or runs a script file.
"""

import sys
import os

# Ensure the project root is in the path
sys.path.insert(0, os.path.dirname(__file__))

# CLI will be implemented in Phase 7
# For now, print a placeholder message

def main():
    print("REXI Interpreter — v0.1 (setup phase)")
    print("Run 'python main.py' after all phases are built.")

if __name__ == "__main__":
    main()
