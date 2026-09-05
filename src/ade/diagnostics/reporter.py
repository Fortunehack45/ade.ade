"""Visual renderer and console reporter for Ade compiler diagnostics."""

import sys
from typing import List, Optional, TextIO
from ade.diagnostics.diagnostic import Diagnostic, Severity


class DiagnosticReporter:
    """Renders formatted diagnostics with code snippets, line gutters, and carets."""

    def __init__(self, output_stream: Optional[TextIO] = None, use_color: bool = False):
        self.stream = output_stream or sys.stderr
        self.use_color = use_color

    def format_diagnostic(self, diagnostic: Diagnostic) -> str:
        lines: List[str] = []
        severity_label = "Error" if diagnostic.severity == Severity.ERROR else (
            "Warning" if diagnostic.severity == Severity.WARNING else "Hint"
        )
        
        # Header: Error: <title>
        lines.append(f"{severity_label}: {diagnostic.title}")
        lines.append("")

        # Source code snippet if span and source code are available
        if diagnostic.span and diagnostic.source_code is not None:
            source_lines = diagnostic.source_code.splitlines()
            start_line_idx = diagnostic.span.start.line - 1
            
            if 0 <= start_line_idx < len(source_lines):
                target_line = source_lines[start_line_idx]
                line_num_str = f"{diagnostic.span.start.line} | "
                gutter_width = len(f"{diagnostic.span.start.line} | ")
                
                # Render source line
                lines.append(f"  {diagnostic.span.start.line} | {target_line}")
                
                # Caret line
                col = max(1, diagnostic.span.start.column)
                end_col = diagnostic.span.end.column if diagnostic.span.end.line == diagnostic.span.start.line else col
                span_len = max(1, end_col - col)
                
                gutter_padding = " " * (gutter_width + 2)
                caret_indent = " " * (col - 1)
                carets = "^" * span_len
                lines.append(f"{gutter_padding}{caret_indent}{carets}")
                lines.append("")

        # Message / explanation
        if diagnostic.message:
            lines.append(diagnostic.message)
            lines.append("")

        # Hint
        if diagnostic.hint:
            lines.append(f"Note: {diagnostic.hint}")
            lines.append("")

        # Suggested fix
        if diagnostic.suggested_fix:
            lines.append("Try:")
            lines.append("")
            for fix_line in diagnostic.suggested_fix.splitlines():
                lines.append(f"  {fix_line}")
            lines.append("")

        return "\n".join(lines).rstrip() + "\n"

    def report(self, diagnostic: Diagnostic) -> None:
        formatted = self.format_diagnostic(diagnostic)
        self.stream.write(formatted)
        self.stream.flush()
