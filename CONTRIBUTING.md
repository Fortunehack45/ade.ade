# Contributing to Ade

Thank you for your interest in contributing to Ade!

## Architectural Principles
1. **Incremental Progression**: Every PR must compile, run, have automated tests, and have zero fake functionality.
2. **Decoupled Components**: Keep compiler phases (`lexer`, `parser`, `ast`, `runtime`, `interpreter`, `cli`, `diagnostics`) strictly separated.
3. **High Diagnostic Standards**: Syntax and runtime errors must never expose raw host stack traces. Errors must show source location, line gutter, caret pointer, explanation, and a suggested fix when possible.
4. **Independent Language Semantics**: Ade's semantics must not be an unprincipled leakage of Python semantics.

## Development Setup
```bash
# Set up virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run test suite
pytest -v tests
```

## Git Workflow
Use descriptive commit messages following the Conventional Commits specification:
- `feat: add lexer tokenization for numbers and strings`
- `feat: implement Pratt expression parser`
- `test: add closure and lexical scoping tests`
- `docs: update language specification for collections`
