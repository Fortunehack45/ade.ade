"""Abstract Syntax Tree (AST) node definitions for Ade."""

from dataclasses import dataclass
from typing import List, Optional, Tuple, Union
from ade.diagnostics.span import SourceSpan
from ade.lexer.token import Token


@dataclass
class ASTNode:
    """Base class for all AST nodes."""
    span: SourceSpan


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
    """Anonymous function: function(params) { body }."""
    params: List[str]
    body: "BlockStmt"


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
    """Variable assignment: target = expression."""
    target: Expression  # Identifier, MemberAccessExpr, or IndexAccessExpr
    value: Expression


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
    """Named function declaration: function name(params) { body }."""
    name: str
    params: List[str]
    body: BlockStmt


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
