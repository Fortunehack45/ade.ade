# Ade Development Roadmap

This document outlines the progressive phases of developing the Ade programming language and language-building platform.

---

## Phase 0: Design & Specifications (Current Phase)
- [x] Project architecture and repository layout.
- [x] Language specification (`LANGUAGE_SPEC.md`).
- [x] Architectural design document (`ARCHITECTURE.md`).
- [x] Project roadmap (`ROADMAP.md`).
- [x] Python 3.12+ project configuration (`pyproject.toml`).

---

## Phase 1: Lexer & Source Tracking (Milestone 0.1)
- [x] Source location tracking: `SourceLocation`, `SourceSpan`.
- [x] Token definitions and token types.
- [x] Robust lexer with column/line preservation, string escapes, number parsing (integers & decimals), identifiers, keywords, delimiters, and `#` comments.
- [x] Automated lexer test suite.

---

## Phase 2: AST & Parser (Milestone 0.1)
- [x] Strongly typed AST node definitions (`Program`, `Statement`, `Expression`, `Literal`, `BinaryExpr`, `UnaryExpr`, `CallExpr`, `IfStmt`, `WhileStmt`, `ForStmt`, `FunctionDecl`, etc.).
- [x] Pratt expression parser with well-defined operator precedence.
- [x] Recursive-descent statement and block parser.
- [x] AST Visitor interface.
- [x] Syntax error recovery and diagnostics.
- [x] Automated parser test suite.

---

## Phase 3: Runtime & Tree-Walk Interpreter (Milestone 0.1)
- [x] Clean runtime value model: `AdeValue`, `AdeNumber`, `AdeString`, `AdeBool`, `AdeNull`, `AdeList`, `AdeMap`, `AdeFunction`, `AdeBuiltinFunction`.
- [x] Scoped lexical environments (`Environment`) with closures.
- [x] Control flow signal management (`return`, `break`, `continue`).
- [x] Standard operations: arithmetic, comparisons, logical operations, indexing, member access.
- [x] `say` output execution.
- [x] Automated interpreter test suite.

---

## Phase 4: CLI & Interactive REPL (Milestone 0.1)
- [x] CLI runner: `ade run <file.ade>` and `python -m ade run <file.ade>`.
- [x] CLI flags: `ade --version`, `ade --help`.
- [x] Interactive REPL: `ade repl` with state persistence, multiline handling, `.help`, `.clear`, and `.exit`.
- [x] End-to-end integration tests.

---

## Phase 5: High-Quality Diagnostics (Milestone 0.1)
- [x] Source line snippet extraction with line gutters.
- [x] Underline carets (`^`) pointing to exact error spans.
- [x] Clear diagnostic messages: What happened, Where it occurred, Why it is invalid, and Suggestions for resolution.

---

## Phase 6: Modules & Package Management
- [x] Project-local module resolution (`import utils`, `from math import sqrt`).
- [x] Independent module cache and isolated module namespaces.
- [ ] Initial project manifest support (`ade.toml`).

---

## Phase 7: Gradual & Static Type System
- [x] Optional type annotations on variables (`name: text = "Fortune"`).
- [x] Function parameter and return type signatures (`function add(a: number, b: number) -> number`).
- [x] Local type inference for basic declarations.
- [x] Static type checker command: `ade check`.

---

## Phase 8: Standard Library
- [x] Core standard libraries:
  - [x] `ade.io`: Standard I/O streams (`read_line`, `print`, `println`, `eprintln`).
  - [x] `ade.fs`: Filesystem read, write, append, existence, directory traversal, deletion.
  - [x] `ade.os`: Environment variables, platform detection, cwd, exit.
  - [x] `ade.math`: Mathematical constants and functions.
  - [x] `ade.json`: Parsing and serializing JSON.
  - [x] `ade.time`: Timestamps, duration, sleep.

---

## Phase 9: Async & Structured Concurrency
- [ ] `async function` and `await` keywords.
- [ ] Structured event loop runtime.
- [ ] Parallel task combinators (`parallel [ ... ]`).

---

## Phase 10: Ade Intermediate Representation (Ade IR)
- [ ] Static Single Assignment (SSA) or linear register-based IR definition.
- [ ] AST -> Ade IR lowering pass.
- [ ] Basic optimization passes (constant folding, dead code elimination).

---

## Phase 11: Bytecode Virtual Machine (VM)
- [ ] Compact bytecode instruction format.
- [ ] Stack-based or register-based bytecode VM.
- [ ] Bytecode compilation and serialization.

---

## Phase 12: Native Compilation & WebAssembly
- [ ] Native code generation via LLVM or Cranelift.
- [ ] WebAssembly (WASM) emission target for browser runtimes.
- [ ] Embedded runtime C-API.

---

## Phase 13: Language-Building Platform Toolkit
- [x] Public compiler API: `ade.language`.
- [x] Composable lexer, grammar, and AST builder interfaces (`LanguageEngine`, `DSLLexer`, `DSLParser`, `DSLNode`).
- [x] Custom language definition syntax and runtime binding natively in Ade (`import language`).
- [x] Custom DSL CLI execution (`ade dsl <spec.ade> <file.dsl>`).

---

## Phase 14: Developer Tooling & Ecosystem
- [ ] Ade Language Server (LSP) for autocomplete, diagnostics, and hover documentation.
- [ ] Code formatter: `ade fmt`.
- [ ] Official VS Code extension.
- [ ] Interactive tutorial system: `ade learn`.
