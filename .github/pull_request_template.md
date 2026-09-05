## Description
Briefly describe the purpose of this Pull Request and what changes were made.

Fixes #(issue number)

## Category of Change
- [ ] Language feature / syntax addition
- [ ] Lexer or Parser update
- [ ] Type System / Semantic analysis (`ade check`)
- [ ] Standard Library (`ade.stdlib`)
- [ ] Language-Building Platform (`ade.language`)
- [ ] Diagnostics / Error reporting improvements
- [ ] CLI / REPL tooling
- [ ] Documentation or Examples
- [ ] Bug fix

## Quality & Verification Checklist
- [ ] Code follows Ade architectural guidelines (decoupled compiler phases, no raw tracebacks to users).
- [ ] Source locations (`SourceSpan`) are preserved across new tokens and AST nodes.
- [ ] New unit and integration tests added in `tests/`.
- [ ] All tests pass: `pytest -v tests`.
- [ ] Static type checker passes: `ade check <example.ade>`.
- [ ] Documentation updated in `docs/` and `LANGUAGE_SPEC.md` if syntax changed.
- [ ] `CHANGELOG.md` updated with entry under Unreleased / next version.
