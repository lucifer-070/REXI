📄 PRODUCT REQUIREMENTS DOCUMENT (PRD)
Project Name
REXI: A Recursive Descent–Based Expression Interpreter with a Command-Line Interface
________________________________________
1. Overview
REXI is a lightweight, CLI-based expression interpreter designed to demonstrate the internal working of parsing and evaluation mechanisms in programming languages. The system allows users to input mathematical expressions and small programs, which are then tokenized, parsed into an abstract syntax tree (AST), and evaluated.
The primary goal of REXI is educational: to provide a hands-on understanding of compiler design concepts such as lexical analysis, recursive descent parsing, syntax trees, and interpretation.
________________________________________
2. Problem Statement
Most existing tools for expression evaluation (such as calculators or scripting languages) hide the internal processes involved in parsing and execution. This makes it difficult for students to understand how programming languages actually interpret and execute code.
There is a need for a system that:
•	Clearly exposes parsing and evaluation steps
•	Is simple enough to understand
•	Still supports meaningful language features like variables and functions
REXI addresses this by implementing a custom expression language from scratch.
________________________________________
3. Objectives
•	To design a custom expression language grammar
•	To implement a lexer that converts input into tokens
•	To build a recursive descent parser that constructs an AST
•	To develop an interpreter that evaluates the AST
•	To support variables, functions, and conditional logic
•	To provide an interactive CLI (REPL)
•	To ensure clear and informative error handling
________________________________________
4. Target Users
•	Undergraduate students learning compiler design
•	Developers interested in understanding interpreters
•	Instructors demonstrating parsing techniques
________________________________________
5. Key Features
5.1 Core Features
•	Arithmetic expression evaluation
•	Operator precedence and associativity
•	Parentheses handling
•	Unary operators (+, -)
________________________________________
5.2 Language Features
•	Variable declaration and usage
•	Built-in functions (e.g., sqrt, max)
•	User-defined functions
•	Conditional statements (if-else)
•	Boolean and comparison expressions
________________________________________
5.3 Execution Modes
•	Interactive CLI (REPL)
•	Script execution from .calc files
________________________________________
5.4 Error Handling
•	Syntax errors with line/column info
•	Runtime errors (undefined variables, division by zero)
•	Clear and readable messages
________________________________________
6. Functional Requirements
Input Handling
•	The system must accept user input via CLI
•	The system must read script files
Lexical Analysis
•	The system must tokenize input into meaningful units
Parsing
•	The system must parse tokens using recursive descent
•	The system must generate an AST
Evaluation
•	The system must evaluate AST nodes recursively
•	The system must support variable storage
Functions
•	The system must allow function definitions and calls
•	The system must support parameter passing
Control Flow
•	The system must support conditional execution
________________________________________
7. Non-Functional Requirements
•	Usability: Simple CLI interface
•	Performance: Fast enough for small programs
•	Maintainability: Modular code structure
•	Scalability: Easy to extend grammar and features
•	Reliability: Proper error handling
________________________________________
8. System Components
•	Lexer (Tokenizer)
•	Parser (Recursive Descent)
•	AST Representation
•	Interpreter / Evaluation Engine
•	Symbol Table / Environment
•	CLI Interface
________________________________________
9. User Flow
1.	User enters an expression or program
2.	Lexer converts input into tokens
3.	Parser builds an AST
4.	Interpreter evaluates the AST
5.	Result is displayed in CLI
________________________________________
10. Constraints
•	Limited to CLI (no GUI)
•	Designed for educational use, not production
•	Grammar complexity kept manageable
________________________________________
11. Risks and Mitigation
Risk	Mitigation
Complex parsing bugs	Incremental development
Team coordination issues	Clear role division
Time constraints	Weekly milestones
Scope creep	Stick to defined features
________________________________________
12. Success Criteria
•	Correct parsing of expressions
•	Accurate evaluation results
•	Stable CLI interaction
•	Clear error reporting
•	Demonstration-ready system
________________________________________
13. Timeline Summary
Phase	Duration
Lexer & Parser	Weeks 1–3
Interpreter & Variables	Weeks 4–6
Functions & Control Flow	Weeks 7–9
CLI, Testing & Docs	Weeks 10–12

