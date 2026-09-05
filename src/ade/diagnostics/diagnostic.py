"""Diagnostic definitions and severity classifications."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from ade.diagnostics.span import SourceSpan


class Severity(Enum):
    ERROR = auto()
    WARNING = auto()
    HINT = auto()


DiagnosticSeverity = Severity


@dataclass
class Diagnostic:
    """A compiler or runtime diagnostic message with source tracking."""
    severity: Severity
    title: str
    message: str
    span: Optional[SourceSpan] = None
    source_code: Optional[str] = None
    hint: Optional[str] = None
    suggested_fix: Optional[str] = None
