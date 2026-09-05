# Ade Programming Language & Language-Building Platform

[![Version](https://img.shields.io/badge/version-0.5.0-blue.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python: 3.12+](https://img.shields.io/badge/python-3.12%2B-brightgreen.svg)](https://python.org)

> **Ade** is a practical, beginner-friendly programming language with Python-level ergonomics and an architecture designed from day one to serve as a platform for building new programming languages and domain-specific languages (DSLs).

---

## Table of Contents

- [What is Ade?](#what-is-ade)
- [Why Does Ade Exist?](#why-does-ade-exist)
- [How is Ade Different?](#how-is-ade-different)
- [Installation & Setup](#installation--setup)
- [Quick Start: Hello World](#quick-start-hello-world)
- [Language Overview & Examples](#language-overview--examples)
  - [Variables & Types](#variables--types)
  - [Control Flow](#control-flow)
  - [Functions](#functions)
  - [Collections](#collections)
- [Architecture](#architecture)
- [The Language-Building Vision](#the-language-building-vision)
- [Project Roadmap](#project-roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## What is Ade?

Ade has two primary missions:
1. **A practical, beginner-friendly general-purpose language**: Clean, expressive syntax with readable constructs, clear error messages, and predictable behavior.
2. **A first-class language-building platform**: A modular compiler and runtime infrastructure that enables developers to construct their own DSLs, script engines, and custom languages without reinventing parsing, AST design, error diagnostics, and runtime evaluation from scratch.

```
                        ADE
                          │
              ┌───────────┴───────────┐
              │                       │
       General Purpose          Language Platform
          Language                    │
              │                       │
       ┌──────┼──────┐        ┌───────┼────────┐
       │      │      │        │       │        │
      Web    AI    Apps     DSLs   NewLangs  Compilers
```

Ade is **not** a Python clone with cosmetic syntax differences. It is an independent language designed to progress from interpreted scripts to typed representations, intermediate representations (Ade IR), and multi-target code generation.

---

## Why Does Ade Exist?

Most modern languages force a choice:
- **Beginner-friendly languages** often make building compilers, runtime inspection, and syntax extensions challenging.
- **Compiler toolkits and meta-compilers** are frequently academic, steep in learning curve, or heavily tied to C++/LLVM complexity.

Ade bridges this divide. You can write your first script in minutes, and as you grow, use the exact same language and its internal APIs to build customized query languages, configuration engines, game scripting environments, or full domain-specific programming languages.

---

## How is Ade Different?

| Feature | Ade | Traditional Scripting Languages |
| :--- | :--- | :--- |
| **Syntax** | Familiar braces `{ ... }`, clean keywords, no semicolons required | Indentation-sensitive or verbose boilerplate |
| **Error Diagnostics** | Human-centric: what went wrong, exact location, reason, and suggested fix | Raw stack traces or generic "SyntaxError" |
| **Language Building** | Built-in platform APIs (`ade.language`) for Lexer, Parser, AST, and Runtime | Requires external parser generators (Lex/Yacc, ANTLR) |
| **Compiler Pipeline** | Fully modular pipeline designed for progressive IR & native backends | Often tightly coupled interpreter loop |
| **Numeric Model** | Explicit unified numeric representation with safe operations | Complex or hidden type coercions |

---

## Installation & Setup

### Requirements
- Python 3.12 or higher.

### Setup (Virtual Environment)
```bash
# Clone the repository
git clone https://github.com/ade-lang/ade.git
cd ade

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install development dependencies
pip install -r requirements.txt
```

---

## Quick Start: Hello World

Create a file named `hello.ade`:

```ade
# hello.ade
say "Hello, World!"
```

Run it using the Ade runner:

```bash
python -m ade run hello.ade
```

Or start an interactive REPL session:

```bash
python -m ade repl
```

```text
Ade 0.1.0 Interactive REPL
Type ".help" for commands, ".exit" to quit.

ade> name = "Ade"
ade> say "Welcome to " + name + "!"
Welcome to Ade!
```

---

## Language Overview & Examples

### Variables & Types
Variables do not require variable declaration keywords:

```ade
name = "Fortune"
age = 19
height = 1.8
is_active = true
empty_val = null

say "User: " + name
```

### Control Flow
Conditionals and loops use explicit curly braces `{ ... }`:

```ade
# If-Else
score = 85
if score >= 90 {
    say "Grade: A"
} else if score >= 80 {
    say "Grade: B"
} else {
    say "Grade: C"
}

# While Loop
counter = 0
while counter < 3 {
    say counter
    counter = counter + 1
}

# For-In Loop
items = [10, 20, 30]
for item in items {
    say item
}
```

### Functions
Functions are first-class values and support closures and return values:

```ade
function add(a, b) {
    return a + b
}

function multiplier(factor) {
    return function(n) {
        return n * factor
    }
}

double = multiplier(2)
say double(10) # Outputs: 20
```

### Collections
Lists and Maps are first-class data structures:

```ade
# Lists
fruits = ["apple", "banana", "cherry"]
say fruits[0]

# Maps
user = {
    name: "Fortune",
    role: "Developer",
    level: 5
}

say user.name
say user["role"]
```

### Milestone Example
```ade
name = "Fortune"
numbers = [1, 2, 3, 4, 5]

function total(items) {
    result = 0

    for item in items {
        result = result + item
    }

    return result
}

say "Hello, " + name
say total(numbers)
```
**Output:**
```
Hello, Fortune
15
```

---

## Architecture

Ade follows a strictly decoupled compiler pipeline:

```
Ade Source Code (.ade)
       │
       ▼
   Lexer  ─────────► Source Spans & Tokens
       │
       ▼
   Parser ─────────► Pure AST (Abstract Syntax Tree)
       │
       ▼
   Semantic Analysis (Scoping & Diagnostics)
       │
       ▼
   Interpreter (Tree-walking Runtime / Future VM & IR)
```

1. **`ade.diagnostics`**: Source span tracking (`SourceLocation`, `SourceSpan`) and formatted error reports with code snippets, caret pointers, and suggestions.
2. **`ade.lexer`**: Lexical scanner converting characters to typed tokens with precise line and column numbers.
3. **`ade.ast`**: Immutable AST node definitions representing statements and expressions.
4. **`ade.parser`**: Recursive-descent Pratt parser handling operator precedence and block syntax.
5. **`ade.runtime`**: Independent value system (`AdeValue`, `AdeNumber`, `AdeString`, `AdeList`, `AdeMap`, `AdeFunction`) and lexical environments.
6. **`ade.interpreter`**: Tree-walking AST evaluator with safe control-flow signal unwinding (`return`, `break`, `continue`).
7. **`ade.cli`**: CLI commands (`run`, `repl`, `--version`, `--help`).
8. **`ade.language`**: Foundations for developers building new languages on top of Ade.

---

## The Language-Building Vision

Ade is architected so that every component of the compiler pipeline is exposed as a composable library:
- Need a custom parser for a configuration DSL? Import `ade.parser` and define custom grammar rules.
- Building a domain-specific mathematical language? Use Ade AST nodes and route execution through the Ade runtime.
- Emitting target code? The future Ade IR will allow translating arbitrary ASTs into optimized native or VM instructions.

---

## Project Roadmap

- [x] **Phase 0 — Design**: Architecture, Language Specification, and Project Roadmap.
- [ ] **Phase 1 — Lexer**: Complete tokenization, line/column tracking, and comments.
- [ ] **Phase 2 — Parser & AST**: Recursive descent and Pratt precedence parsing.
- [ ] **Phase 3 — Interpreter & Runtime**: Tree-walking evaluation and lexical scopes.
- [ ] **Phase 4 — CLI & REPL**: Command-line interface and interactive shell.
- [ ] **Phase 5 — Diagnostics**: High-fidelity Clang/Rust-style compiler diagnostics.
- [ ] **Phase 6 — Modules**: Import and module resolution system.
- [ ] **Phase 7 — Gradual Type System**: Optional type hints and type inference.
- [ ] **Phase 8 — Standard Library**: `ade.io`, `ade.fs`, `ade.math`, `ade.json`, `ade.http`.
- [ ] **Phase 9 — Async & Concurrency**: Async/await and structured parallelism.
- [ ] **Phase 10 — Ade IR**: Intermediate representation for cross-target compilation.
- [ ] **Phase 11 — Native / WASM Backend**: Compiling Ade IR to native code and WebAssembly.
- [ ] **Phase 12 — Language Toolkit**: Complete public API for building custom languages.

---

## Contributing

Contributions are welcome! Please review [CONTRIBUTING.md](CONTRIBUTING.md) and adhere to our coding standards:
- All changes must include unit and integration tests.
- Maintain independent compiler layer separation.
- Zero undocumented syntax or silent failures.

---

## License

Ade is open-source software licensed under the [MIT License](LICENSE).
