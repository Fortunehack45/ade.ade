"""Generic AST node model for custom languages and DSLs."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from ade.diagnostics.span import SourceSpan


@dataclass
class DSLNode:
    """Generic AST node for domain-specific languages and custom syntax trees."""
    type: str
    value: Any = None
    children: List["DSLNode"] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    span: Optional[SourceSpan] = None

    def child(self, index: int) -> "DSLNode":
        """Convenience method to access a child node by index."""
        if 0 <= index < len(self.children):
            return self.children[index]
        raise IndexError(f"DSLNode '{self.type}' child index {index} out of range (count: {len(self.children)})")

    def pretty(self, indent: int = 0) -> str:
        """Render a readable visual tree representation of this AST node."""
        pad = "  " * indent
        val_str = f" val={self.value!r}" if self.value is not None else ""
        attr_str = f" {self.attributes}" if self.attributes else ""
        lines = [f"{pad}({self.type}{val_str}{attr_str}"]
        for child in self.children:
            lines.append(child.pretty(indent + 1))
        lines.append(f"{pad})")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Convert AST node to a serializable dictionary."""
        return {
            "type": self.type,
            "value": self.value,
            "children": [c.to_dict() for c in self.children],
            "attributes": self.attributes,
        }

    def __repr__(self) -> str:
        if self.children:
            return f"DSLNode({self.type!r}, val={self.value!r}, children={len(self.children)})"
        return f"DSLNode({self.type!r}, val={self.value!r})"
