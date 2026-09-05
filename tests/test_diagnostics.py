"""Automated tests for Ade diagnostic formatting and error reporting."""

from ade.diagnostics.span import SourceLocation, SourceSpan
from ade.diagnostics.diagnostic import Diagnostic, Severity
from ade.diagnostics.reporter import DiagnosticReporter
from ade.lexer.lexer import Lexer
from ade.lexer.errors import LexerError
from ade.parser.parser import Parser
from ade.parser.errors import ParseError


def test_diagnostic_formatting_visual():
    source = "result = add(10, 20"
    span = SourceSpan(
        start=SourceLocation("test.ade", line=1, column=19, offset=18),
        end=SourceLocation("test.ade", line=1, column=20, offset=19),
    )
    diag = Diagnostic(
        severity=Severity.ERROR,
        title="expected ')' after function arguments",
        message="The function call is missing a closing ')'.",
        span=span,
        source_code=source,
        suggested_fix="result = add(10, 20)",
    )

    reporter = DiagnosticReporter()
    output = reporter.format_diagnostic(diag)

    assert "Error: expected ')' after function arguments" in output
    assert "1 | result = add(10, 20" in output
    assert "^" in output
    assert "The function call is missing a closing ')'." in output
    assert "Try:" in output
    assert "result = add(10, 20)" in output


def test_parser_diagnostic_generation():
    source = "if true say 1"
    try:
        tokens = Lexer(source).tokenize()
        Parser(tokens, source_code=source).parse()
        assert False, "Should have raised ParseError"
    except ParseError as e:
        diag = e.to_diagnostic()
        assert diag.severity == Severity.ERROR
        assert "expected '{' before block body" in diag.message
        reporter = DiagnosticReporter()
        formatted = reporter.format_diagnostic(diag)
        assert "Error: Syntax Error" in formatted
        assert "^" in formatted
