# Ade Architecture & Compiler System Design

This document describes the architectural principles, component boundaries, and internal pipelines of the Ade programming language and language-building platform.

---

## 1. High-Level Architectural Vision

Ade is designed with a dual objective:
1. Provide an ergonomic, reliable runtime for general-purpose programming.
2. Serve as an extensible compiler framework for building domain-specific and general-purpose languages.

```
                      Ade Source Code (.ade)
                                │
                                ▼
                       [ Lexer (ade.lexer) ]
                                │
                                ▼ Tokens + Source Spans
                       [ Parser (ade.parser) ]
                                │
                                ▼ Abstract Syntax Tree (AST)
                   [ Semantic Analyzer (ade.semantic) ]
                                │
                                ▼ Typed / Resolved AST
                    [ Ade IR (ade.ir - Future) ]
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
 [ Tree-Walk / VM ]     [ LLVM / Native ]         [ WebAssembly ]
 (Interpreter 0.1)      (Future Backend)         (Future Backend)
```

---

## 2. Component Pipeline

### 2.1 Diagnostics & Source Spans (`ade.diagnostics`)
Every token and AST node retains a `SourceSpan`, consisting of start and end `SourceLocation` points (`file`, `line`, `column`, `offset`).

Diagnostics do not produce generic uninformative errors. The diagnostic engine formats errors with:
- Error category and human-readable title.
- Exact code excerpt with line gutter and indentation alignment.
- Caret (`^`) pinpointing the exact character span.
- Plain-English explanation of why the syntax or operation is invalid.
- Concrete suggestion for resolution (`Try: ...`).

### 2.2 Lexical Analysis (`ade.lexer`)
The lexer converts raw UTF-8 text into a stream of typed `Token` objects.
- Operates on a single pass with lookahead.
- Maintains line numbers, column numbers, and byte offsets.
- Strips `#` single-line comments while preserving newline tokens where necessary to determine statement termination.
- Distinguishes exact token types: keywords, identifiers, numeric literals (integer and decimal), strings with escape sequences, operators, and delimiters.

### 2.3 Abstract Syntax Tree (`ade.ast`)
The AST represents the syntactic structure of an Ade program.
- Defined as typed, immutable dataclasses.
- Nodes are strictly categorized into `Statement` and `Expression`.
- All nodes implement a common base class `ASTNode` carrying a `span: SourceSpan`.
- Includes an `ASTVisitor` pattern for clean traversal, inspection, and transformation without polluting node definitions.

### 2.4 Syntax Analysis / Parser (`ade.parser`)
The parser is a recursive-descent parser combined with a Pratt precedence-climbing parser for binary and unary expressions.
- Deterministic token consumption with `match()`, `expect()`, and `peek()`.
- Unambiguous operator precedence table (multiplicative > additive > relational > equality > logical `and` > logical `or`).
- Comprehensive error recovery: synchronization on statement boundaries (`\n`, `}`, `EOF`) to prevent cascading false syntax errors.

### 2.5 Runtime Model & Environment (`ade.runtime`)
To ensure Ade is not merely an incidental wrapper around Python data structures, Ade defines its own value hierarchy:
- `AdeValue`: Abstract root of all runtime objects.
- `AdeNumber`: Numeric representation supporting automatic promotion between integers and floating decimals.
- `AdeString`: Text values with string operations and slicing.
- `AdeBool`: `AdeBool.TRUE` and `AdeBool.FALSE`.
- `AdeNull`: Canonical `null` representation.
- `AdeList`: Dynamic list of `AdeValue` instances.
- `AdeMap`: Key-value dictionary supporting dot and bracket access.
- `AdeFunction`: Closures holding parameter signatures, function AST bodies, and references to their defining lexical `Environment`.
- `AdeBuiltinFunction`: Host environment bindings (e.g. `len`, `type`, `str`).

### 2.6 Lexical Scoping & Environments (`ade.runtime.environment`)
Lexical scopes are managed as linked environments:
```
[ Global Environment ]
          ▲
          │ enclosing
[ Function Environment ]
          ▲
          │ enclosing
[ Block / Loop Environment ]
```
- Variables are looked up recursively up the environment chain.
- New variables are defined in the current innermost scope.
- Existing variables can be mutated in their containing scope.

### 2.7 Interpreter Execution (`ade.interpreter`)
The initial execution engine is a tree-walking interpreter.
- Evaluates AST nodes by dispatching on node type.
- Employs lightweight Python control-flow signals (`ReturnSignal`, `BreakSignal`, `ContinueSignal`) to handle non-local jumps cleanly without unstructured control flow.
- Traps runtime exceptions (such as division by zero, invalid property access, or undefined variable lookup) and formats them through the diagnostics engine.

---

## 3. Language-Building Infrastructure (`ade.language`)

Ade's defining feature is its platform capability.
The `ade.language` module defines the base interfaces for language construction:
- `LexerDefinition`: Declarative token rules, regex patterns, and keyword tables.
- `GrammarDefinition`: Production rules and precedence definitions.
- `LanguagePipeline`: Pluggable compiler pipeline enabling developers to compose their own Lexer, Parser, AST, and Evaluator.

```
       [ Custom DSL Source ]
                 │
                 ▼
     [ User LexerDefinition ]
                 │
                 ▼
    [ User GrammarDefinition ]
                 │
                 ▼
       [ Ade AST / IR ]
                 │
                 ▼
       [ Ade Execution Engine ]
```

---

## 4. Path to Future VM and Native Compilation

While the initial version is interpreted in Python:
1. The AST is completely independent of Python AST or Python bytecode.
2. The runtime value model is cleanly encapsulated, permitting replacement with a C/Rust runtime or bytecode virtual machine (VM).
3. The future Ade IR (Intermediate Representation) will introduce a static single-assignment (SSA) or linear register-based IR, enabling ahead-of-time (AOT) compilation via LLVM or Cranelift, and WebAssembly emission.
