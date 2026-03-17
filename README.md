# REXI — Recursive Descent Expression Interpreter

REXI is a lightweight, CLI-based expression interpreter that demonstrates the internal workings of a compiler frontend — lexing, parsing, and evaluation.

## Features
- Arithmetic expressions with full operator precedence
- Variables and assignments
- User-defined and built-in functions (`sqrt`, `max`, `min`, `abs`)
- Conditional logic (`if / else`)
- Interactive REPL and `.calc` script file execution
- Clear syntax and runtime error messages

## Project Structure
```
REXI/
├── main.py              # Entry point
├── src/
│   ├── tokens.py        # Token types and Token class
│   ├── lexer.py         # Lexer (tokenizer)
│   ├── ast_nodes.py     # AST node definitions
│   ├── parser.py        # Recursive descent parser
│   ├── interpreter.py   # AST evaluator
│   ├── environment.py   # Symbol table / scoped environment
│   └── cli.py           # REPL and script runner
└── tests/
    ├── test_lexer.py
    ├── test_parser.py
    └── test_interpreter.py
```

## Tech Stack
- **Language**: Python 3.x (standard library only)
- **Testing**: pytest

## Usage

### Interactive REPL
```bash
python main.py
```

### Run a script file
```bash
python main.py script.calc
```

## Example
```
>> x = 10 + 5 * 2
>> x
20
>> def square(n) = n * n
>> square(7)
49
```

## Running Tests
```bash
pip install pytest
pytest tests/
```
