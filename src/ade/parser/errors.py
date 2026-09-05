"""Parser errors and diagnostic creation."""

from typing import Optional
from ade.diagnostics.diagnostic import Diagnostic, Severity
from ade.diagnostics.span import SourceSpan


class ParseError(Exception):
    """Exception raised for syntax and grammar errors during parsing."""

    def __init__(
        self,
        message: str,
        span: SourceSpan,
        source_code: Optional[str] = None,
        hint: Optional[str] = None,
        suggested_fix: Optional[str] = None,
    ):
        super().__init__(message)
        self.message = message
        self.span = span
        self.source_code = source_code
        self.hint = hint
        self.suggested_fix = suggested_fix

    def to_diagnostic(self) -> Diagnostic:
        return Diagnostic(
            severity=Severity.ERROR,
            title="Syntax Error",
            message=self.message,
            span=self.span,
            source_code=self.source_code,
            hint=self.hint,
            suggested_fix=self.suggested_fix,
        )
