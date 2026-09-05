"""Abstract Syntax Tree (AST) node definitions for Ade."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union
from ade.diagnostics.span import SourceSpan
from ade.lexer.token import Token


@dataclass
class ASTNode:
    """Base class for all AST nodes."""
    span: SourceSpan


# ============================================================================
# Type Annotations
# ============================================================================

@dataclass
class TypeAnnotation(ASTNode):
    """Base class for type annotations."""
    pass


@dataclass
class NamedTypeAnnotation(TypeAnnotation):
    """Named type: number, text, bool, null, any, void, or custom class name."""
    name: str


@dataclass
class NullableTypeAnnotation(TypeAnnotation):
    """Nullable type: inner? (e.g. text?, number?)."""
    inner: TypeAnnotation


@dataclass
class GenericTypeAnnotation(TypeAnnotation):
    """Generic type: name<arg1, arg2, ...> (e.g. list<number>, map<text, number>)."""
    name: str
    type_arguments: List[TypeAnnotation]


@dataclass
class UnionTypeAnnotation(TypeAnnotation):
    """Union type: T1 | T2 | ... (e.g. number | text)."""
    types: List[TypeAnnotation]


# ============================================================================
# Expressions
# ============================================================================

@dataclass
class Expression(ASTNode):
    """Base class for all expression nodes."""
    pass


@dataclass
class NumberLiteral(Expression):
    """Numeric literal (integer or floating decimal)."""
    value: Union[int, float]


@dataclass
class StringLiteral(Expression):
    """Text/string literal."""
    value: str


@dataclass
class BoolLiteral(Expression):
    """Boolean literal (true or false)."""
    value: bool


@dataclass
class NullLiteral(Expression):
    """Null literal."""
    pass


@dataclass
class Identifier(Expression):
    """Variable or symbol reference."""
    name: str


@dataclass
class BinaryExpr(Expression):
    """Binary operation: left op right."""
    left: Expression
    operator: Token
    right: Expression


@dataclass
class UnaryExpr(Expression):
    """Unary operation: op operand."""
    operator: Token
    operand: Expression


@dataclass
class CallExpr(Expression):
    """Function call: callee(arguments)."""
    callee: Expression
    arguments: List[Expression]


@dataclass
class NamedArgExpr(Expression):
    """Named argument in a call: name: value."""
    name: str
    value: Expression


@dataclass
class MemberAccessExpr(Expression):
    """Member access: object.member."""
    object: Expression
    member: str


@dataclass
class IndexAccessExpr(Expression):
    """Index access: object[index]."""
    object: Expression
    index: Expression


@dataclass
class ListLiteral(Expression):
    """List literal: [elem1, elem2, ...]."""
    elements: List[Expression]


@dataclass
class MapEntry:
    """A key-value pair in a map literal."""
    key: Expression
    value: Expression


@dataclass
class MapLiteral(Expression):
    """Map literal: { key: value, ... }."""
    entries: List[MapEntry]


@dataclass
class AnonymousFunctionExpr(Expression):
    """Anonymous function: function(params) -> return_type { body }."""
    params: List[str]
    body: "BlockStmt"
    param_types: Optional[Dict[str, Optional[TypeAnnotation]]] = None
    return_type: Optional[TypeAnnotation] = None


@dataclass
class StringInterpolationExpr(Expression):
    """String interpolation: parts are string chunks or expressions."""
    parts: List[Union[str, Expression]]


# ============================================================================
# Statements
# ============================================================================

@dataclass
class Statement(ASTNode):
    """Base class for all statement nodes."""
    pass


@dataclass
class Program(Statement):
    """Root program node containing a sequence of statements."""
    statements: List[Statement]


@dataclass
class BlockStmt(Statement):
    """Block of statements enclosed in braces { ... }."""
    statements: List[Statement]


@dataclass
class ExpressionStmt(Statement):
    """An expression evaluated as a statement."""
    expression: Expression


@dataclass
class VarAssignmentStmt(Statement):
    """Variable assignment: target = expression, with optional type annotation."""
    target: Expression  # Identifier, MemberAccessExpr, or IndexAccessExpr
    value: Expression
    type_annotation: Optional[TypeAnnotation] = None


@dataclass
class SayStmt(Statement):
    """Output statement: say <expression>."""
    expression: Expression


@dataclass
class IfStmt(Statement):
    """If-Else conditional branch."""
    condition: Expression
    then_branch: BlockStmt
    else_branch: Optional[Statement]  # Either BlockStmt or nested IfStmt


@dataclass
class WhileStmt(Statement):
    """While loop."""
    condition: Expression
    body: BlockStmt


@dataclass
class ForStmt(Statement):
    """For-in collection loop."""
    variable: str
    iterable: Expression
    body: BlockStmt


@dataclass
class FunctionDeclStmt(Statement):
    """Named function declaration: function name(params) -> return_type { body }."""
    name: str
    params: List[str]
    body: BlockStmt
    param_types: Optional[Dict[str, Optional[TypeAnnotation]]] = None
    return_type: Optional[TypeAnnotation] = None


@dataclass
class ReturnStmt(Statement):
    """Return statement: return <expr>?."""
    value: Optional[Expression]


@dataclass
class BreakStmt(Statement):
    """Break loop statement."""
    pass


@dataclass
class ContinueStmt(Statement):
    """Continue loop iteration statement."""
    pass


@dataclass
class ImportStmt(Statement):
    """Import statement: import <module_name> (as <alias>)?."""
    module_name: str
    alias: Optional[str]


@dataclass
class FromImportStmt(Statement):
    """From-import statement: from <module_name> import <sym> (as <alias>)?, ..."""
    module_name: str
    symbols: List[Tuple[str, Optional[str]]]  # (original_name, alias)


@dataclass
class ClassDeclStmt(Statement):
    """Class declaration: class Name (extends Super)? { fields, methods }."""
    name: str
    superclass: Optional[str]
    fields: List[str]
    methods: List[FunctionDeclStmt]
