# Changelog

All notable changes to Ade will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-05

### Added
- **Phase 0 Design & Foundation**:
  - `LANGUAGE_SPEC.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `README.md`.
- **Lexer (`ade.lexer`)**:
  - Token scanner tracking line, column, byte offset, and source spans.
  - Numbers (integer and decimal), strings with escape characters, booleans, null.
  - Keywords, operators, delimiters, and single-line `#` comments.
- **AST & Parser (`ade.ast`, `ade.parser`)**:
  - Pure typed AST nodes with source span attribution.
  - Pratt expression parser with precedence climbing.
  - Recursive descent parsing for statements, blocks `{ ... }`, control flow (`if/else`, `while`, `for ... in ...`), and function declarations.
  - AST Visitor pattern.
- **Diagnostics (`ade.diagnostics`)**:
  - Informative Clang/Rust-style compiler diagnostics with source code preview, line gutters, caret (`^`) indicators, and suggestions.
- **Runtime & Interpreter (`ade.runtime`, `ade.interpreter`)**:
  - Encapsulated value hierarchy (`AdeValue`, `AdeNumber`, `AdeString`, `AdeBool`, `AdeNull`, `AdeList`, `AdeMap`, `AdeFunction`, `AdeBuiltinFunction`).
  - Lexical scoping with parent chain delegation and closures.
  - Control flow signals for `return`, `break`, and `continue`.
  - First-class functions, recursion, and higher-order functions.
  - Collections (lists and maps) with indexing, dot member access, and iteration.
  - `say` statement for console output.
- **CLI & REPL (`ade.cli`)**:
  - `ade run <file.ade>` for running Ade scripts.
  - `ade repl` for interactive REPL sessions with state persistence and meta commands (`.help`, `.exit`, `.clear`).
  - `ade --version` and `ade --help`.
- **Language Platform Foundations (`ade.language`)**:
  - Core interfaces for language building and extensible compiler pipelines.
