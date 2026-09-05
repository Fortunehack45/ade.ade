"""Source location and span tracking for compiler diagnostics."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SourceLocation:
    """A specific point in a source file."""
    file: str
    line: int       # 1-indexed
    column: int     # 1-indexed
    offset: int     # 0-indexed byte offset

    def __str__(self) -> str:
        return f"{self.file}:{self.line}:{self.column}"


@dataclass(frozen=True)
class SourceSpan:
    """A span of characters from start to end in a source file."""
    start: SourceLocation
    end: SourceLocation

    @property
    def file(self) -> str:
        return self.start.file

    @property
    def line(self) -> int:
        return self.start.line

    @property
    def column(self) -> int:
        return self.start.column

    @classmethod
    def from_single(cls, loc: SourceLocation) -> "SourceSpan":
        return cls(start=loc, end=loc)

    @classmethod
    def merge(cls, first: "SourceSpan", second: Optional["SourceSpan"]) -> "SourceSpan":
        if second is None:
            return first
        return cls(start=first.start, end=second.end)

    def __str__(self) -> str:
        if self.start.line == self.end.line:
            return f"{self.start.file}:{self.start.line}:{self.start.column}-{self.end.column}"
        return f"{self.start.file}:{self.start.line}:{self.start.column} - {self.end.line}:{self.end.column}"
