"""Lexical scope environment for variable bindings."""

from typing import Dict, Optional
from ade.runtime.value import AdeValue


class Environment:
    """Manages variable bindings with parent scope delegation."""

    def __init__(self, parent: Optional["Environment"] = None):
        self.values: Dict[str, AdeValue] = {}
        self.parent: Optional[Environment] = parent

    def define(self, name: str, value: AdeValue) -> None:
        """Bind a variable in the local scope."""
        self.values[name] = value

    def get(self, name: str) -> Optional[AdeValue]:
        """Look up a variable recursively up the scope chain."""
        if name in self.values:
            return self.values[name]
        if self.parent is not None:
            return self.parent.get(name)
        return None

    def exists(self, name: str) -> bool:
        """Check if a variable exists in this scope or any enclosing parent."""
        if name in self.values:
            return True
        if self.parent is not None:
            return self.parent.exists(name)
        return False

    def assign(self, name: str, value: AdeValue) -> None:
        """Assign to an existing variable in the nearest scope; otherwise define in current scope."""
        if name in self.values:
            self.values[name] = value
            return

        if self.parent is not None and self.parent.exists(name):
            self.parent.assign(name, value)
            return

        # New variable: bind in current local scope
        self.values[name] = value
