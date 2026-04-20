# REXI — End-to-End Usage Guide

This guide walks you through everything from installation to running real programs in REXI.

---

## 1. Setup

```bash
# Clone the repo
git clone https://github.com/lucifer-070/REXI.git
cd REXI

# No dependencies needed to run — only pytest for tests
pip install pytest

# Verify tests pass
python -m pytest tests/ -q
# Expected: 212 passed
```

---

## 2. Starting the REPL

```bash
python main.py
```

You'll see:
```
╔══════════════════════════════════════════╗
║   REXI — Recursive Descent Interpreter  ║
║   Type :help for commands, :exit to quit ║
╚══════════════════════════════════════════╝

>>
```

Type any expression after `>>` and press Enter.

---

## 3. Arithmetic

REXI follows standard operator precedence (BODMAS):

```
>> 2 + 3
=> 5

>> 10 - 4 * 2
=> 2

>> (10 - 4) * 2
=> 12

>> 15 / 4
=> 3.75

>> 15 % 4
=> 3

>> 2 ^ 10
=> 1024
```

Unary minus and plus:
```
>> -5
=> -5

>> --3
=> 3
```

---

## 4. Variables

Assign with `=`. Variables persist across lines in the same REPL session.

```
>> x = 10
>> y = x * 3 + 1
>> y
=> 31

>> x = x + 5
>> x
=> 15
```

To see all current variables:
```
>> :env
[global scope]
  x = 15
  y = 31
```

---

## 5. Booleans and Comparisons

```
>> true
=> true

>> false
=> false

>> 5 > 3
=> true

>> 5 == 5
=> true

>> 5 != 3
=> true

>> 5 >= 5
=> true

>> 3 < 2
=> false
```

Logical operators:
```
>> true and false
=> false

>> true or false
=> true

>> not true
=> false

>> 5 > 3 and 2 < 4
=> true
```

---

## 6. String Literals

```
>> greeting = "Hello, REXI!"
>> print(greeting)
Hello, REXI!
```

Escape sequences:
```
>> print("line1\nline2")
line1
line2

>> print("He said \"hi\"")
He said "hi"
```

---

## 7. Conditional Expressions

Syntax: `if <condition> then <value> else <value>`

```
>> x = -8
>> if x > 0 then x else -x
=> 8

>> score = 85
>> if score >= 90 then "A" else "B"
(string result — use print to display)

>> if true then 1 else 0
=> 1
```

Nested conditions:
```
>> x = 0
>> if x > 0 then "positive" else if x < 0 then "negative" else "zero"
```

---

## 8. User-Defined Functions

Syntax: `def <name>(<params>) = <expression>`

```
>> def double(n) = n * 2
>> double(7)
=> 14

>> def add(a, b) = a + b
>> add(3, 4)
=> 7

>> def circle_area(r) = 3.14159 * r * r
>> circle_area(5)
=> 78.53975
```

Functions are stored in the environment — use `:env` to see them.

---

## 9. Recursive Functions

```
>> def fact(n) = if n <= 1 then 1 else n * fact(n - 1)
>> fact(5)
=> 120
>> fact(10)
=> 3628800

>> def fib(n) = if n <= 1 then n else fib(n - 1) + fib(n - 2)
>> fib(10)
=> 55
```

---

## 10. While Loops

Syntax: `while <condition> then <expression>`

The body is evaluated on each iteration. Variables updated in the body persist.

```
>> x = 5
>> while x > 0 then x = x - 1
>> x
=> 0
```

Countdown with a user-defined step function:
```
>> def step(n) = n - 2
>> x = 10
>> while x > 0 then x = step(x)
>> x
=> 0
```

> **Note:** Loops have a 100,000 iteration safety limit to prevent infinite loops
> from hanging the REPL. If hit, you'll see a `REXIRuntimeError`.

---

## 11. Built-in Functions

```
>> sqrt(144)
=> 12

>> abs(-42)
=> 42

>> max(3, 9)
=> 9

>> min(3, 9)
=> 3

>> pow(2, 8)
=> 256

>> floor(3.9)
=> 3

>> ceil(3.1)
=> 4

>> round(3.5)
=> 4

>> print("hello")
hello
```

---

## 12. REPL Commands

### `:help`
Shows all commands and a language quick-reference.

### `:env`
Shows all variables and functions in the current session:
```
>> x = 10
>> def double(n) = n * 2
>> :env
[global scope]
  double = <function double>
  x = 10
```

### `:tree <expression>`
Parses an expression and shows its full Abstract Syntax Tree:
```
>> :tree 1 + 2 * 3
Block
└── BinOp('+')
    ├── Number(1)
    └── BinOp('*')
        ├── Number(2)
        └── Number(3)
```

A recursive function's tree:
```
>> :tree def fact(n) = if n <= 1 then 1 else n * fact(n - 1)
Block
└── FuncDef('fact', params=[n])
    └── If
        ├── cond: BinOp('<=')
        │   ├── Var('n')
        │   └── Number(1)
        ├── then: Number(1)
        └── else: BinOp('*')
            ├── Var('n')
            └── FuncCall('fact')
                └── BinOp('-')
                    ├── Var('n')
                    └── Number(1)
```

### `:clear`
Resets the interpreter — wipes all variables and functions:
```
>> x = 42
>> :clear
(interpreter reset — all variables cleared)
>> x
[RuntimeError]: Undefined variable 'x'
```

### `:exit` / `:quit`
Exits the REPL.

---

## 13. Running Script Files

Write a `.calc` file and run it directly:

**`factorial.calc`:**
```
def fact(n) = if n <= 1 then 1 else n * fact(n - 1)
result = fact(10)
print(result)
```

```bash
python main.py factorial.calc
```
Output:
```
3628800
```

**`fibonacci.calc`:**
```
def fib(n) = if n <= 1 then n else fib(n - 1) + fib(n - 2)
i = 0
while i < 10 then i = i + 1
print(fib(i))
```

```bash
python main.py fibonacci.calc
```

---

## 14. Error Messages

REXI gives precise error messages with the exact line and column:

**Unknown character:**
```
>> x = 1 + @
[LexerError] Line 1, Col 11: Unexpected character '@'

  x = 1 + @
            ^
```

**Undefined variable:**
```
>> y + 1
[RuntimeError] (line 1, col 1): Undefined variable 'y'
```

**Division by zero:**
```
>> 10 / 0
[RuntimeError] (line 1, col 6): Division by zero
```

**Wrong argument count:**
```
>> sqrt(1, 2)
[RuntimeError]: sqrt() takes 1 argument(s), got 2
```

---

## 15. A Complete Example Session

```
>> # Define some utility functions
>> def square(n) = n * n
>> def cube(n) = n * n * n
>> def abs_val(x) = if x >= 0 then x else -x

>> # Test them
>> square(12)
=> 144
>> cube(3)
=> 27
>> abs_val(-99)
=> 99

>> # Recursive factorial
>> def fact(n) = if n <= 1 then 1 else n * fact(n - 1)
>> fact(7)
=> 5040

>> # While loop countdown
>> counter = 10
>> while counter > 0 then counter = counter - 3
>> counter
=> -2

>> # Check environment
>> :env
[global scope]
  abs_val = <function abs_val>
  counter = -2
  cube = <function cube>
  fact = <function fact>
  square = <function square>

>> # Inspect the AST of an expression
>> :tree square(n) + cube(n)
Block
└── BinOp('+')
    ├── FuncCall('square')
    │   └── Var('n')
    └── FuncCall('cube')
        └── Var('n')

>> :exit
Bye!
```
