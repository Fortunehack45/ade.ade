"""Symbol definitions and scoped symbol tables for semantic analysis."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional
from ade.diagnostics.span import SourceSpan
from ade.types.model import AdeType, TYPE_ANY


@dataclass
class Symbol:
    """A semantic symbol representing a variable, function, class, or type."""
    name: str
    type: AdeType
    span: SourceSpan
    is_constant: bool = False
    is_function: bool = False
    is_class: bool = False


class SymbolTable:
    """Hierarchical lexical scope table for symbols."""

    def __init__(self, parent: Optional[SymbolTable] = None, name: str = "global"):
        self.parent = parent
        self.name = name
        self.symbols: Dict[str, Symbol] = {}

    def define(self, name: str, symbol: Symbol) -> None:
        """Register a symbol in the current scope."""
        self.symbols[name] = symbol

    def resolve(self, name: str) -> Optional[Symbol]:
        """Resolve a symbol by name, walking up enclosing lexical parent scopes."""
        if name in self.symbols:
            return self.symbols[name]
        if self.parent is not None:
            return self.parent.resolve(name)
        return None

    def resolve_local(self, name: str) -> Optional[Symbol]:
        """Resolve a symbol only in the immediate local scope."""
        return self.symbols.get(name)

    def is_global(self) -> bool:
        """Return True if this is the root global scope."""
        return self.parent is None
