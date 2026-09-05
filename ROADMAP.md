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
- [ ] Source location tracking: `SourceLocation`, `SourceSpan`.
- [ ] Token definitions and token types.
- [ ] Robust lexer with column/line preservation, string escapes, number parsing (integers & decimals), identifiers, keywords, delimiters, and `#` comments.
- [ ] Automated lexer test suite.

---

## Phase 2: AST & Parser (Milestone 0.1)
- [ ] Strongly typed AST node definitions (`Program`, `Statement`, `Expression`, `Literal`, `BinaryExpr`, `UnaryExpr`, `CallExpr`, `IfStmt`, `WhileStmt`, `ForStmt`, `FunctionDecl`, etc.).
- [ ] Pratt expression parser with well-defined operator precedence.
- [ ] Recursive-descent statement and block parser.
- [ ] AST Visitor interface.
- [ ] Syntax error recovery and diagnostics.
- [ ] Automated parser test suite.

---

## Phase 3: Runtime & Tree-Walk Interpreter (Milestone 0.1)
- [ ] Clean runtime value model: `AdeValue`, `AdeNumber`, `AdeString`, `AdeBool`, `AdeNull`, `AdeList`, `AdeMap`, `AdeFunction`, `AdeBuiltinFunction`.
- [ ] Scoped lexical environments (`Environment`) with closures.
- [ ] Control flow signal management (`return`, `break`, `continue`).
- [ ] Standard operations: arithmetic, comparisons, logical operations, indexing, member access.
- [ ] `say` output execution.
- [ ] Automated interpreter test suite.

---

## Phase 4: CLI & Interactive REPL (Milestone 0.1)
- [ ] CLI runner: `ade run <file.ade>` and `python -m ade run <file.ade>`.
- [ ] CLI flags: `ade --version`, `ade --help`.
- [ ] Interactive REPL: `ade repl` with state persistence, multiline handling, `.help`, `.clear`, and `.exit`.
- [ ] End-to-end integration tests.

---

## Phase 5: High-Quality Diagnostics (Milestone 0.1)
- [ ] Source line snippet extraction with line gutters.
- [ ] Underline carets (`^`) pointing to exact error spans.
- [ ] Clear diagnostic messages: What happened, Where it occurred, Why it is invalid, and Suggestions for resolution.

---

## Phase 6: Modules & Package Management
- [ ] Project-local module resolution (`import utils`, `from math import sqrt`).
- [ ] Independent module cache and isolated module namespaces.
- [ ] Initial project manifest support (`ade.toml`).

---

## Phase 7: Gradual & Static Type System
- [ ] Optional type annotations on variables (`name: text = "Fortune"`).
- [ ] Function parameter and return type signatures (`function add(a: number, b: number) -> number`).
- [ ] Local type inference for basic declarations.
- [ ] Static type checker command: `ade check`.

---

## Phase 8: Standard Library
- [ ] Core standard libraries:
  - `ade.io`: Standard I/O streams and formatting.
  - `ade.fs`: Filesystem read, write, directory traversal.
  - `ade.os`: Environment variables, platform detection.
  - `ade.math`: Mathematical constants and functions.
  - `ade.json`: Parsing and serializing JSON.
  - `ade.time`: Timestamps, duration, formatting.

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
- [ ] Public compiler API: `ade.language`.
- [ ] Composable lexer, grammar, and AST builder interfaces.
- [ ] Custom language definition syntax and runtime binding.

---

## Phase 14: Developer Tooling & Ecosystem
- [ ] Ade Language Server (LSP) for autocomplete, diagnostics, and hover documentation.
- [ ] Code formatter: `ade fmt`.
- [ ] Official VS Code extension.
- [ ] Interactive tutorial system: `ade learn`.
