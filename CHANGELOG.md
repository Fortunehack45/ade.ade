# Changelog

All notable changes to Ade will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-09-05

### Added
- **Gradual & Static Type System (`ade.types`, `ade.semantic`)**:
  - Optional variable type annotations: `name: text = "Fortune"`, `age: number = 19`, `active: bool = true`, `val: text? = null`.
  - Function signatures with parameter and return types: `function add(a: number, b: number) -> number`.
  - Generic collection types: `list<number>`, `map<text, number>`.
  - Nullable types: `T?` accepting `T` or `null`.
  - Union types: `T1 | T2` permitting multiple candidate types.
  - Hierarchical type compatibility and assignability engine (`AdeType`, `PrimitiveType`, `ListType`, `MapType`, `NullableType`, `UnionType`, `FunctionType`, `ClassType`).
  - Scoped semantic symbol resolution tables (`Symbol`, `SymbolTable`).
  - Static type checker pass (`TypeChecker`) detecting mismatches, invalid arguments, return type errors, and undefined variables before execution.
- **CLI Command `ade check <file.ade>` (`ade.cli`)**:
  - New subcommand executing full static semantic analysis without code execution.
  - Rust/Clang-grade visual diagnostics with line snippets, gutters, carets (`^`), notes, and actionable `Try:` suggestions.

## [0.2.0] - 2026-09-05

### Added
- **Independent Module System (`ade.modules`)**:
  - `import <module>` and `from <module> import <symbols>` with file-relative resolution and caching.
  - Isolated lexical execution environments for imported modules.
  - Aliasing support with `as` keyword.
- **String Interpolation**:
  - Embedded expression evaluation within double-quoted strings: `"Hello {name}"` and `"Math: {1 + 2}"`.
- **Object-Oriented Programming (Classes & Instances)**:
  - `class <Name> { ... }` supporting field declarations and method definitions.
  - Constructor support and instance instantiation with positional and named arguments.
  - Implicit `self` instance binding in methods and dynamic property mutation.
- **Standard Library Foundations (`ade.stdlib`)**:
  - Standard `math` module (`sqrt`, `sin`, `cos`, `tan`, `abs`, `floor`, `ceil`, `min`, `max`, `pow`, `pi`, `e`).
  - Standard `time` module (`now`, `timestamp`, `sleep`).
  - Standard `json` module (`parse`, `stringify`).

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
