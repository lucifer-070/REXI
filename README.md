# REXI — Recursive Descent Expression Interpreter

> A compiler design project demonstrating lexing, parsing, and AST evaluation from scratch — built entirely on Python's standard library.

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Language Reference](#language-reference)
- [Built-in Functions](#built-in-functions)
- [REPL Commands](#repl-commands)
- [Running Tests](#running-tests)
- [Team](#team)

---

## Overview

REXI is a tree-walking interpreter that evaluates a custom expression language. It demonstrates the full compiler frontend pipeline:

```
Source code  →  Lexer  →  Tokens  →  Parser  →  AST  →  Interpreter  →  Result
```

The language supports arithmetic, boolean logic, variables, user-defined functions with closures, conditional expressions, and while loops.

---

## Features

- ✅ Arithmetic with full operator precedence (`+`, `-`, `*`, `/`, `%`, `^`)
- ✅ Comparison and logical operators (`==`, `!=`, `<`, `>`, `<=`, `>=`, `and`, `or`, `not`)
- ✅ Variables and assignment
- ✅ User-defined functions with lexical scoping and closures
- ✅ Recursive functions
- ✅ Built-in functions (`sqrt`, `abs`, `max`, `min`, `pow`, `floor`, `ceil`, `round`, `print`)
- ✅ Boolean literals (`true`, `false`)
- ✅ String literals (`"hello world"`)
- ✅ Conditional expressions (`if … then … else …`)
- ✅ While loops (`while … then …`)
- ✅ Interactive REPL with `:tree`, `:env`, `:clear` commands
- ✅ Script file execution (`.calc` files)
- ✅ Unified error reporting with source line + caret pointer
- ✅ 212 tests, all passing

---

## Project Structure

```
REXI/
├── main.py                  # Entry point — launches REPL or runs script file
├── src/
│   ├── tokens.py            # TokenType enum + Token dataclass
│   ├── lexer.py             # Lexer: source text → token list
│   ├── ast_nodes.py         # AST node class definitions
│   ├── parser.py            # Recursive descent parser: tokens → AST
│   ├── interpreter.py       # Tree-walking interpreter: AST → value
│   ├── environment.py       # Scoped symbol table (variable/function store)
│   ├── ast_printer.py       # Pretty-prints an AST as a tree diagram
│   ├── cli.py               # Interactive REPL + script file runner
│   └── errors.py            # Unified error formatter with caret pointer
└── tests/
    ├── test_lexer.py        # 32 tests
    ├── test_parser.py       # 40 tests
    ├── test_interpreter.py  # 67 tests
    ├── test_aryan.py        # 30 tests (while grammar, token, environment)
    ├── test_harshit.py      # 21 tests (string literals, error formatter)
    └── test_pratyush.py     # 22 tests (while interpreter, AST printer, CLI)
```

---

## Architecture

```
┌─────────────┐    ┌──────────┐    ┌────────────┐    ┌───────────────┐
│  Source Text │ →  │  Lexer   │ →  │   Parser   │ →  │  Interpreter  │
│  (string)   │    │tokens.py │    │  parser.py │    │interpreter.py │
└─────────────┘    └──────────┘    └────────────┘    └───────────────┘
                        ↓                ↓                    ↓
                    Token list        AST nodes           Result value
                   (tokens.py)    (ast_nodes.py)      (environment.py)
```

Each phase has a dedicated custom exception:
- `LexerError` — unrecognised character, unterminated string
- `ParseError` — unexpected token, malformed expression
- `REXIRuntimeError` — division by zero, undefined variable, infinite loop

---

## Installation

No external dependencies required for the interpreter itself.

```bash
git clone https://github.com/lucifer-070/REXI.git
cd REXI

# Only needed for running tests
pip install pytest
```

---

## Usage

### Interactive REPL
```bash
python main.py
```

### Run a script file
```bash
python main.py path/to/script.calc
```

---

## Language Reference

### Arithmetic
```
>> 2 + 3 * 4
=> 14

>> (2 + 3) * 4
=> 20

>> 10 / 4
=> 2.5

>> 2 ^ 8
=> 256

>> 17 % 5
=> 2
```

### Variables
```
>> x = 42
>> y = x * 2
>> y
=> 84
```

### Booleans
```
>> true
=> true

>> 1 == 1
=> true

>> 5 > 3 and 2 < 4
=> true

>> not false
=> true
```

### String literals
```
>> name = "REXI"
>> print(name)
REXI
```

### Conditional expressions
```
>> x = -5
>> if x > 0 then x else -x
=> 5
```

### User-defined functions
```
>> def square(n) = n * n
>> square(9)
=> 81

>> def max2(a, b) = if a > b then a else b
>> max2(10, 7)
=> 10
```

### Recursive functions
```
>> def fact(n) = if n <= 1 then 1 else n * fact(n - 1)
>> fact(6)
=> 720
```

### While loops
```
>> x = 5
>> while x > 0 then x = x - 1
>> x
=> 0
```

### Comments
```
# This is a comment — everything after # is ignored
>> x = 10   # inline comment
```

---

## Built-in Functions

| Function | Description | Example |
|---|---|---|
| `sqrt(x)` | Square root | `sqrt(16)` → `4` |
| `abs(x)` | Absolute value | `abs(-7)` → `7` |
| `max(a, b)` | Maximum of two values | `max(3, 9)` → `9` |
| `min(a, b)` | Minimum of two values | `min(3, 9)` → `3` |
| `pow(x, n)` | Power | `pow(2, 10)` → `1024` |
| `floor(x)` | Floor | `floor(3.7)` → `3` |
| `ceil(x)` | Ceiling | `ceil(3.2)` → `4` |
| `round(x)` | Round to nearest integer | `round(3.5)` → `4` |
| `print(...)` | Print values to stdout | `print(x)` |

---

## REPL Commands

| Command | Description |
|---|---|
| `:help` | Show all commands and a language quick-reference |
| `:env` | Print all variables and functions defined in the current session |
| `:tree <expr>` | Parse an expression and display its AST as an indented tree |
| `:clear` | Reset the interpreter — clears all variables and functions |
| `:builtins` | List all built-in functions |
| `:exit` / `:quit` | Exit the REPL |

#### Example — `:tree`
```
>> :tree 1 + 2 * (3 + 4)
Block
└── BinOp('+')
    ├── Number(1)
    └── BinOp('*')
        ├── Number(2)
        └── BinOp('+')
            ├── Number(3)
            └── Number(4)
```

#### Example — `:env`
```
>> x = 10
>> def double(n) = n * 2
>> :env
[global scope]
  double = <function double>
  x = 10
```

---

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -q
```

Expected output:
```
212 passed in 0.xx s
```

---

## Team

| Name | Role |
|---|---|
| **Pratyush** | AST node definitions, interpreter engine, REPL, while loop evaluation |
| **Aryan** | Grammar design, parser, while loop grammar rule, symbol table |
| **Harshit** | Lexer / tokenizer, string literals, error handling & reporting |
