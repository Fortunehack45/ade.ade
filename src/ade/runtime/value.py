"""Ade runtime value representations and type hierarchy."""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Union
from ade.diagnostics.span import SourceSpan


class AdeValue(ABC):
    """Abstract base class for all runtime values in Ade."""

    @abstractmethod
    def type_name(self) -> str:
        """Return the user-facing name of the type."""
        pass

    @abstractmethod
    def is_truthy(self) -> bool:
        """Determine truthiness in conditional evaluation."""
        pass

    @abstractmethod
    def to_string(self) -> str:
        """User-facing string representation."""
        pass

    def __str__(self) -> str:
        return self.to_string()


# ============================================================================
# Primitive Types
# ============================================================================

class AdeNumber(AdeValue):
    """Numeric value (integer or floating decimal)."""

    def __init__(self, value: Union[int, float]):
        self.value = value

    def type_name(self) -> str:
        return "number"

    def is_truthy(self) -> bool:
        # In Ade, only null and false are falsy
        return True

    def to_string(self) -> str:
        if isinstance(self.value, float) and self.value.is_integer():
            return str(int(self.value))
        return str(self.value)

    def __repr__(self) -> str:
        return f"AdeNumber({self.value})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AdeNumber):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        return hash(self.value)


class AdeString(AdeValue):
    """Text/string value."""

    def __init__(self, value: str):
        self.value = value

    def type_name(self) -> str:
        return "text"

    def is_truthy(self) -> bool:
        return True

    def to_string(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"AdeString({self.value!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AdeString):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        return hash(self.value)


class AdeBool(AdeValue):
    """Boolean value (true or false)."""

    TRUE: "AdeBool"
    FALSE: "AdeBool"

    def __init__(self, value: bool):
        self.value = bool(value)

    def type_name(self) -> str:
        return "bool"

    def is_truthy(self) -> bool:
        return self.value

    def to_string(self) -> str:
        return "true" if self.value else "false"

    def __repr__(self) -> str:
        return f"AdeBool({self.value})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AdeBool):
            return self.value == other.value
        return False

    def __hash__(self) -> int:
        return hash(self.value)


AdeBool.TRUE = AdeBool(True)
AdeBool.FALSE = AdeBool(False)


class AdeNull(AdeValue):
    """Null singleton value."""

    INSTANCE: "AdeNull"

    def type_name(self) -> str:
        return "null"

    def is_truthy(self) -> bool:
        return False

    def to_string(self) -> str:
        return "null"

    def __repr__(self) -> str:
        return "AdeNull()"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, AdeNull)

    def __hash__(self) -> int:
        return hash(None)


AdeNull.INSTANCE = AdeNull()


# ============================================================================
# Collection Types
# ============================================================================

class AdeList(AdeValue):
    """Ordered dynamic list of Ade values."""

    def __init__(self, elements: Optional[List[AdeValue]] = None):
        self.elements: List[AdeValue] = list(elements) if elements is not None else []

    def type_name(self) -> str:
        return "list"

    def is_truthy(self) -> bool:
        return True

    def to_string(self) -> str:
        inner = ", ".join(
            f'"{e.to_string()}"' if isinstance(e, AdeString) else e.to_string()
            for e in self.elements
        )
        return f"[{inner}]"

    def __repr__(self) -> str:
        return f"AdeList({self.elements!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AdeList):
            return self.elements == other.elements
        return False


class AdeMap(AdeValue):
    """Key-value dictionary mapping string keys to Ade values."""

    def __init__(self, entries: Optional[Dict[str, AdeValue]] = None):
        self.entries: Dict[str, AdeValue] = dict(entries) if entries is not None else {}

    def type_name(self) -> str:
        return "map"

    def is_truthy(self) -> bool:
        return True

    def to_string(self) -> str:
        parts = []
        for k, v in self.entries.items():
            val_str = f'"{v.to_string()}"' if isinstance(v, AdeString) else v.to_string()
            parts.append(f"{k}: {val_str}")
        return "{" + ", ".join(parts) + "}"

    def __repr__(self) -> str:
        return f"AdeMap({self.entries!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, AdeMap):
            return self.entries == other.entries
        return False


# ============================================================================
# Callable Types
# ============================================================================

class AdeCallable(AdeValue):
    """Base class for all callable values (functions, builtins)."""

    def type_name(self) -> str:
        return "function"

    def is_truthy(self) -> bool:
        return True

    @abstractmethod
    def arity(self) -> int:
        """Expected number of arguments."""
        pass

    @abstractmethod
    def call(
        self, interpreter: Any, arguments: List[AdeValue], span: SourceSpan
    ) -> AdeValue:
        """Execute the function call."""
        pass


class AdeFunction(AdeCallable):
    """User-defined function with closure and parameters."""

    def __init__(
        self,
        name: Optional[str],
        params: List[str],
        body: Any,  # BlockStmt
        closure: Any,  # Environment
    ):
        self.name = name or "<anonymous>"
        self.params = params
        self.body = body
        self.closure = closure

    def arity(self) -> int:
        return len(self.params)

    def to_string(self) -> str:
        param_str = ", ".join(self.params)
        return f"<function {self.name}({param_str})>"

    def call(
        self, interpreter: Any, arguments: List[AdeValue], span: SourceSpan
    ) -> AdeValue:
        # Create a new environment enclosed by this function's closure
        from ade.runtime.environment import Environment
        from ade.interpreter.signals import ReturnSignal

        env = Environment(parent=self.closure)
        for param_name, arg_val in zip(self.params, arguments):
            env.define(param_name, arg_val)

        try:
            interpreter.execute_block(self.body, env)
        except ReturnSignal as ret:
            return ret.value

        return AdeNull.INSTANCE


class AdeBuiltinFunction(AdeCallable):
    """Host built-in function callable from Ade."""

    def __init__(
        self,
        name: str,
        param_count: int,
        fn: Callable[[Any, List[AdeValue], SourceSpan], AdeValue],
    ):
        self.name = name
        self.param_count = param_count
        self.fn = fn

    def arity(self) -> int:
        return self.param_count

    def to_string(self) -> str:
        return f"<builtin function {self.name}>"

    def call(
        self, interpreter: Any, arguments: List[AdeValue], span: SourceSpan
    ) -> AdeValue:
        return self.fn(interpreter, arguments, span)
