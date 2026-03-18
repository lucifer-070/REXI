# ✅ REXI — Project Todo List

> Derived from `prd.md` and `tech_stack.md`. Each feature is broken down into granular implementation steps.
> ⚠️ **Constraint**: No external libraries except **`pytest`** for testing. Core implementation uses only Python standard library (`enum`, `math`, `sys`).
> Status: `[ ]` = not started · `[/]` = in progress · `[x]` = done

---

## 🗂️ Phase 1 — Project Setup (Week 1)

- [ ] Create Git repository and push initial commit
- [ ] Set up branch structure:
  - [ ] `main`
  - [ ] `feature/lexer`
  - [ ] `feature/parser`
  - [ ] `feature/interpreter`
  - [ ] `feature/cli`
- [ ] Create project folder structure:
  ```
  REXI/
  ├── lexer.py
  ├── parser.py
  ├── ast_nodes.py
  ├── interpreter.py
  ├── environment.py
  ├── cli.py
  └── main.py
  ```
- [ ] Set up `README.md` with project description
- [ ] Verify Python 3.x is installed and working
- [ ] Install `pytest` for testing (`pip install pytest`)

---

## 🔤 Phase 2 — Lexer / Tokenizer (Weeks 1–2)

> Uses: `enum` (standard library only)

- [ ] Define `TokenType` enum using Python's `enum` module:
  - [ ] `NUMBER`, `IDENTIFIER`
  - [ ] `PLUS`, `MINUS`, `MUL`, `DIV`, `MOD`, `POWER`
  - [ ] `LPAREN`, `RPAREN`
  - [ ] `ASSIGN`, `EQ`, `NEQ`, `LT`, `GT`, `LTE`, `GTE`
  - [ ] `AND`, `OR`, `NOT`
  - [ ] `IF`, `ELSE`
  - [ ] `DEF`, `RETURN`
  - [ ] `COMMA`, `NEWLINE`, `EOF`
- [ ] Implement `Token` dataclass (type, value, line, column)
- [ ] Implement `Lexer` class:
  - [ ] `__init__`: store source text, initialize position/line/col
  - [ ] `advance()`: move to next character, track line/column
  - [ ] `skip_whitespace()` and `skip_comment()`
  - [ ] `read_number()`: handle integers and floats
  - [ ] `read_identifier()`: handle keywords vs identifiers
  - [ ] `tokenize()`: main loop returning list of tokens
- [ ] Handle unary `+` and `-` tokens
- [ ] ~~Write unit tests for the lexer~~ (covered above — see Phase 8)

---

## 🌳 Phase 3 — AST Node Definitions (Week 2)

- [ ] Create `ast_nodes.py` with node classes:
  - [ ] `NumberNode(value)`
  - [ ] `BinOpNode(left, op, right)`
  - [ ] `UnaryOpNode(op, operand)`
  - [ ] `VarAssignNode(name, value)`
  - [ ] `VarAccessNode(name)`
  - [ ] `FuncDefNode(name, params, body)`
  - [ ] `FuncCallNode(name, args)`
  - [ ] `IfNode(condition, then_body, else_body)`
  - [ ] `ReturnNode(value)`
- [ ] Add `__repr__` methods to all nodes for debugging / display

---

## 🔍 Phase 4 — Parser (Recursive Descent) (Weeks 2–3)

- [ ] Implement `Parser` class:
  - [ ] `__init__`: receive token list, set position
  - [ ] `current_token()`, `advance()`, `expect(type)` helpers
- [ ] Implement grammar rules as methods:
  - [ ] `parse()` — entry point
  - [ ] `parse_statement()` — dispatch: assignment, if, func def, expression
  - [ ] `parse_assignment()` — `IDENTIFIER ASSIGN expr`
  - [ ] `parse_if()` — `IF expr THEN block [ELSE block]`
  - [ ] `parse_func_def()` — `DEF name(params) body`
  - [ ] `parse_expression()` — boolean/comparison level
  - [ ] `parse_comparison()` — `<`, `>`, `==`, `!=`, etc.
  - [ ] `parse_additive()` — `+` / `-`
  - [ ] `parse_multiplicative()` — `*` / `/` / `%`
  - [ ] `parse_unary()` — unary `+` / `-` / `NOT`
  - [ ] `parse_power()` — `^` or `**` (right-associative)
  - [ ] `parse_primary()` — number, identifier, parenthesised expr, func call
- [ ] Handle operator precedence and associativity correctly
- [ ] Raise `SyntaxError` with line/column info on unexpected tokens
- [ ] Write unit tests for the parser (`tests/test_parser.py`)

---

## 🧠 Phase 5 — Interpreter / Evaluation Engine (Weeks 4–6)

- [ ] Implement `Environment` class (`environment.py`):
  - [ ] `__init__(parent=None)` for scoped environments
  - [ ] `set(name, value)` — define/update variable
  - [ ] `get(name)` — look up variable (walk parent scopes)
- [ ] Implement `Interpreter` class:
  - [ ] `__init__`: create global environment
  - [ ] `visit(node)`: dispatch to `visit_<NodeType>` methods
  - [ ] `visit_NumberNode` — return numeric value
  - [ ] `visit_BinOpNode` — apply operator, handle division by zero
  - [ ] `visit_UnaryOpNode` — apply unary operator
  - [ ] `visit_VarAssignNode` — store value in environment
  - [ ] `visit_VarAccessNode` — retrieve from environment, raise if undefined
  - [ ] `visit_FuncDefNode` — store function definition in environment
  - [ ] `visit_FuncCallNode` — create child scope, bind args, execute body
  - [ ] `visit_IfNode` — evaluate condition, branch to then/else
  - [ ] `visit_ReturnNode` — raise special `ReturnSignal` exception to unwind
- [ ] Implement built-in functions using Python's `math` module (standard library):
  - [ ] `sqrt(x)`
  - [ ] `max(a, b)`, `min(a, b)`
  - [ ] `abs(x)`
  - [ ] `pow(base, exp)`
- [ ] Write unit tests for the interpreter (`tests/test_interpreter.py`)

---

## ⚠️ Phase 6 — Error Handling (Weeks 5–6)

- [ ] Create custom exception classes:
  - [ ] `LexerError(message, line, col)`
  - [ ] `ParseError(message, line, col)`
  - [ ] `RuntimeError(message)`
- [ ] All errors must print: message + line + column
- [ ] Handle specific runtime errors:
  - [ ] Division by zero
  - [ ] Undefined variable access
  - [ ] Wrong number of arguments to function
  - [ ] Return outside of function
- [ ] Catch errors at the CLI level and display without crashing the REPL

---

## 💬 Phase 7 — CLI / REPL Interface (Weeks 10–11)

- [ ] Implement `cli.py`:
  - [ ] `run_repl()`: interactive loop using `input()` / `sys.stdin`
  - [ ] Print welcome banner and usage hint
  - [ ] Handle `exit` / `quit` commands
  - [ ] Catch and display errors without crashing
  - [ ] (Optional) Implement basic command history manually using an in-memory list (no `readline`)
- [ ] Implement `run_file(path)`:
  - [ ] Accept `.calc` file path as CLI argument via `sys.argv`
  - [ ] Read file contents and pass to lexer → parser → interpreter pipeline
  - [ ] Print output / errors
- [ ] Wire everything in `main.py`:
  - [ ] If no argument: start REPL
  - [ ] If file argument: run file

---

## 🧪 Phase 8 — Testing & Integration (Weeks 11–12)

- [ ] Write integration tests (`tests/test_integration.py`) using `pytest`:
  - [ ] Arithmetic expressions
  - [ ] Variable assignment and access
  - [ ] Nested expressions with parentheses
  - [ ] User-defined functions
  - [ ] Built-in functions
  - [ ] If-else branching
  - [ ] Error cases (div by zero, undefined var, syntax errors)
- [ ] Run full test suite with `pytest` and fix failures
- [ ] Manually test REPL session end-to-end
- [ ] Test `.calc` script file execution

---

## 📝 Phase 9 — Documentation (Week 12)

- [ ] Write `README.md`:
  - [ ] Project overview and purpose
  - [ ] Installation instructions
  - [ ] How to run REPL
  - [ ] How to run a `.calc` script
  - [ ] Language syntax reference (operators, variables, functions, if-else)
  - [ ] Example programs
- [ ] (Optional) Create architecture diagram with Draw.io
- [ ] (Optional) Document AST node hierarchy
- [ ] (Optional) Add inline docstrings to all classes/methods

---

## 🚀 Phase 10 — Final Polish & Submission

- [ ] Code review / cleanup across all modules
- [ ] Ensure all branches are merged into `main`
- [ ] Verify the project runs from a clean clone
- [ ] Prepare demo: 3–5 example programs showcasing all features
- [ ] Final commit and push to GitHub
