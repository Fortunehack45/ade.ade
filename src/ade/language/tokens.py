"""Token definitions, lexer rules, and configurable tokenizer for custom DSLs."""

import re
from dataclasses import dataclass
from typing import Any, Callable, List, Optional
from ade.diagnostics.diagnostic import Diagnostic, Severity
from ade.diagnostics.reporter import DiagnosticReporter
from ade.diagnostics.span import SourceLocation, SourceSpan


@dataclass(frozen=True)
class DSLToken:
    """Token representation in custom domain-specific languages."""
    type: str
    lexeme: str
    value: Any
    span: SourceSpan

    @property
    def is_eof(self) -> bool:
        return self.type == "EOF"

    def __repr__(self) -> str:
        return f"DSLToken({self.type}, {self.lexeme!r}, val={self.value!r})"


@dataclass
class LexerRule:
    """A rule defining how a token pattern is recognized and processed."""
    name: str
    pattern: re.Pattern
    ignore: bool = False
    converter: Optional[Callable[[str], Any]] = None


class DSLLexerError(Exception):
    """Exception raised when a custom DSL lexical error occurs."""
    def __init__(self, diagnostic: Diagnostic):
        super().__init__(diagnostic.message)
        self.diagnostic = diagnostic


class DSLLexer:
    """Dynamic, configurable tokenizer for custom languages and DSLs."""

    def __init__(
        self,
        rules: List[LexerRule],
        source: str,
        file_path: str = "<dsl>",
    ):
        self.rules = rules
        self.source = source
        self.file_path = file_path
        self.cursor = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> List[DSLToken]:
        tokens: List[DSLToken] = []
        source_len = len(self.source)

        while self.cursor < source_len:
            matched = False
            for rule in self.rules:
                match = rule.pattern.match(self.source, self.cursor)
                if match:
                    matched = True
                    lexeme = match.group(0)
                    start_loc = SourceLocation(
                        file=self.file_path,
                        line=self.line,
                        column=self.column,
                        offset=self.cursor,
                    )

                    # Advance cursor and update line/column counts
                    self.cursor += len(lexeme)
                    newline_count = lexeme.count("\n")
                    if newline_count > 0:
                        self.line += newline_count
                        last_nl = lexeme.rfind("\n")
                        self.column = len(lexeme) - last_nl
                    else:
                        self.column += len(lexeme)

                    end_loc = SourceLocation(
                        file=self.file_path,
                        line=self.line,
                        column=self.column,
                        offset=self.cursor,
                    )
                    span = SourceSpan(start=start_loc, end=end_loc)

                    if not rule.ignore:
                        if rule.converter:
                            val = rule.converter(lexeme)
                        elif rule.name == "NUMBER":
                            try:
                                val = float(lexeme) if "." in lexeme else int(lexeme)
                            except ValueError:
                                val = lexeme
                        else:
                            val = lexeme
                        tokens.append(DSLToken(type=rule.name, lexeme=lexeme, value=val, span=span))
                    break

            if not matched:
                # Unrecognized character
                bad_char = self.source[self.cursor]
                loc = SourceLocation(
                    file=self.file_path,
                    line=self.line,
                    column=self.column,
                    offset=self.cursor,
                )
                span = SourceSpan.from_single(loc)
                diag = Diagnostic(
                    severity=Severity.ERROR,
                    title="DSL Syntax Error",
                    message=f"Unexpected or unrecognized character {bad_char!r} in custom DSL.",
                    span=span,
                    source_code=self.source,
                    hint="Check if a token rule or whitespace ignore rule matches this character.",
                    suggested_fix="Define a token pattern for this character or remove it from the input.",
                )
                raise DSLLexerError(diag)

        eof_loc = SourceLocation(
            file=self.file_path,
            line=self.line,
            column=self.column,
            offset=self.cursor,
        )
        tokens.append(DSLToken(type="EOF", lexeme="", value=None, span=SourceSpan.from_single(eof_loc)))
        return tokens
