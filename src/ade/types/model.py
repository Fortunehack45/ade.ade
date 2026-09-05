"""Type hierarchy and model definitions for the Ade Type System."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple, Union
from ade.ast.nodes import (
    TypeAnnotation,
    NamedTypeAnnotation,
    NullableTypeAnnotation,
    GenericTypeAnnotation,
    UnionTypeAnnotation,
)


class AdeType:
    """Base class for all static/gradual types in Ade."""

    def is_assignable_to(self, target: AdeType) -> bool:
        """Return True if a value of this type can be assigned to a location expecting target."""
        if target is TYPE_ANY or self is TYPE_ANY:
            return True
        if self == target:
            return True
        if isinstance(target, UnionType):
            return any(self.is_assignable_to(member) for member in target.types)
        if isinstance(target, NullableType):
            if self is TYPE_NULL:
                return True
            return self.is_assignable_to(target.inner)
        return False

    def display_name(self) -> str:
        return str(self)


@dataclass(frozen=True)
class PrimitiveType(AdeType):
    """Primitive data type: number, text, bool, null, any, void."""
    name: str

    def __str__(self) -> str:
        return self.name

    def is_assignable_to(self, target: AdeType) -> bool:
        if target is TYPE_ANY or self is TYPE_ANY:
            return True
        if isinstance(target, UnionType):
            return any(self.is_assignable_to(m) for m in target.types)
        if isinstance(target, NullableType):
            if self is TYPE_NULL:
                return True
            return self.is_assignable_to(target.inner)
        if isinstance(target, PrimitiveType):
            # Treat 'text' and 'string' as interchangeable synonyms
            if self.name in ("text", "string") and target.name in ("text", "string"):
                return True
            return self.name == target.name
        return False


TYPE_NUMBER = PrimitiveType("number")
TYPE_TEXT = PrimitiveType("text")
TYPE_BOOL = PrimitiveType("bool")
TYPE_NULL = PrimitiveType("null")
TYPE_ANY = PrimitiveType("any")
TYPE_VOID = PrimitiveType("void")


@dataclass(frozen=True)
class ListType(AdeType):
    """List collection type: list<element_type>."""
    element_type: AdeType = TYPE_ANY

    def __str__(self) -> str:
        if self.element_type is TYPE_ANY:
            return "list"
        return f"list<{self.element_type}>"

    def is_assignable_to(self, target: AdeType) -> bool:
        if target is TYPE_ANY:
            return True
        if isinstance(target, UnionType):
            return any(self.is_assignable_to(m) for m in target.types)
        if isinstance(target, NullableType):
            return self.is_assignable_to(target.inner)
        if isinstance(target, ListType):
            if target.element_type is TYPE_ANY or self.element_type is TYPE_ANY:
                return True
            return self.element_type.is_assignable_to(target.element_type)
        return False


@dataclass(frozen=True)
class MapType(AdeType):
    """Map collection type: map<key_type, value_type>."""
    key_type: AdeType = TYPE_TEXT
    value_type: AdeType = TYPE_ANY

    def __str__(self) -> str:
        if self.key_type is TYPE_TEXT and self.value_type is TYPE_ANY:
            return "map"
        return f"map<{self.key_type}, {self.value_type}>"

    def is_assignable_to(self, target: AdeType) -> bool:
        if target is TYPE_ANY:
            return True
        if isinstance(target, UnionType):
            return any(self.is_assignable_to(m) for m in target.types)
        if isinstance(target, NullableType):
            return self.is_assignable_to(target.inner)
        if isinstance(target, MapType):
            return (
                self.key_type.is_assignable_to(target.key_type)
                and self.value_type.is_assignable_to(target.value_type)
            )
        return False


@dataclass(frozen=True)
class NullableType(AdeType):
    """Nullable type: inner? (e.g. text?, number?)."""
    inner: AdeType

    def __str__(self) -> str:
        return f"{self.inner}?"

    def is_assignable_to(self, target: AdeType) -> bool:
        if target is TYPE_ANY:
            return True
        if isinstance(target, UnionType):
            return any(self.is_assignable_to(m) for m in target.types)
        if isinstance(target, NullableType):
            return self.inner.is_assignable_to(target.inner)
        return False


@dataclass(frozen=True)
class UnionType(AdeType):
    """Union type: T1 | T2 | ... (e.g. number | text)."""
    types: Tuple[AdeType, ...]

    def __str__(self) -> str:
        return " | ".join(str(t) for t in self.types)

    def is_assignable_to(self, target: AdeType) -> bool:
        if target is TYPE_ANY:
            return True
        # All members of this union must be assignable to target
        return all(member.is_assignable_to(target) for member in self.types)


@dataclass
class FunctionType(AdeType):
    """Callable function signature: (param1: T1, param2: T2) -> ReturnType."""
    param_types: List[Tuple[str, AdeType]] = field(default_factory=list)
    return_type: AdeType = TYPE_ANY

    def __str__(self) -> str:
        params_str = ", ".join(f"{name}: {t}" for name, t in self.param_types)
        return f"({params_str}) -> {self.return_type}"

    def is_assignable_to(self, target: AdeType) -> bool:
        if target is TYPE_ANY:
            return True
        if isinstance(target, UnionType):
            return any(self.is_assignable_to(m) for m in target.types)
        if isinstance(target, NullableType):
            return self.is_assignable_to(target.inner)
        if isinstance(target, FunctionType):
            if len(self.param_types) != len(target.param_types):
                return False
            # Return types must be covariant
            if not self.return_type.is_assignable_to(target.return_type):
                return False
            # Parameter types must be contravariant
            for (_, my_param), (_, target_param) in zip(self.param_types, target.param_types):
                if not target_param.is_assignable_to(my_param):
                    return False
            return True
        return False


@dataclass
class ClassType(AdeType):
    """Object class definition type."""
    name: str
    fields: Dict[str, AdeType] = field(default_factory=dict)
    methods: Dict[str, FunctionType] = field(default_factory=dict)
    superclass: Optional[ClassType] = None

    def __str__(self) -> str:
        return self.name

    def is_assignable_to(self, target: AdeType) -> bool:
        if target is TYPE_ANY:
            return True
        if isinstance(target, UnionType):
            return any(self.is_assignable_to(m) for m in target.types)
        if isinstance(target, NullableType):
            return self.is_assignable_to(target.inner)
        if isinstance(target, ClassType):
            curr: Optional[ClassType] = self
            while curr is not None:
                if curr.name == target.name:
                    return True
                curr = curr.superclass
            return False
        return False


def resolve_type_annotation(
    annotation: Optional[TypeAnnotation],
    lookup_custom: Optional[Callable[[str], Optional[AdeType]]] = None,
) -> AdeType:
    """Convert an AST TypeAnnotation node into an AdeType model."""
    if annotation is None:
        return TYPE_ANY

    if isinstance(annotation, NamedTypeAnnotation):
        name = annotation.name.lower()
        if name == "number":
            return TYPE_NUMBER
        if name in ("text", "string"):
            return TYPE_TEXT
        if name == "bool":
            return TYPE_BOOL
        if name == "null":
            return TYPE_NULL
        if name == "any":
            return TYPE_ANY
        if name == "void":
            return TYPE_VOID

        # Check for non-generic 'list' or 'map'
        if name == "list":
            return ListType(TYPE_ANY)
        if name == "map":
            return MapType(TYPE_TEXT, TYPE_ANY)

        # Check custom type lookup (classes, aliases)
        if lookup_custom is not None:
            custom = lookup_custom(annotation.name)
            if custom is not None:
                return custom

        # Default custom named type to ClassType placeholder
        return ClassType(name=annotation.name)

    if isinstance(annotation, GenericTypeAnnotation):
        name = annotation.name.lower()
        if name == "list":
            elem_type = (
                resolve_type_annotation(annotation.type_arguments[0], lookup_custom)
                if annotation.type_arguments
                else TYPE_ANY
            )
            return ListType(element_type=elem_type)
        if name == "map":
            k_type = (
                resolve_type_annotation(annotation.type_arguments[0], lookup_custom)
                if len(annotation.type_arguments) > 0
                else TYPE_TEXT
            )
            v_type = (
                resolve_type_annotation(annotation.type_arguments[1], lookup_custom)
                if len(annotation.type_arguments) > 1
                else TYPE_ANY
            )
            return MapType(key_type=k_type, value_type=v_type)

        # Unknown generic: fallback to any
        return TYPE_ANY

    if isinstance(annotation, NullableTypeAnnotation):
        inner = resolve_type_annotation(annotation.inner, lookup_custom)
        return NullableType(inner=inner)

    if isinstance(annotation, UnionTypeAnnotation):
        types = tuple(
            resolve_type_annotation(member, lookup_custom)
            for member in annotation.types
        )
        return UnionType(types=types)

    return TYPE_ANY
