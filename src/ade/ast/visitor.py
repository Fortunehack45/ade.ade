"""AST Visitor pattern for traversing and analyzing Ade syntax trees."""

from abc import ABC, abstractmethod
from typing import Any
from ade.ast.nodes import (
    Program,
    BlockStmt,
    ExpressionStmt,
    VarAssignmentStmt,
    SayStmt,
    IfStmt,
    WhileStmt,
    ForStmt,
    FunctionDeclStmt,
    ReturnStmt,
    BreakStmt,
    ContinueStmt,
    NumberLiteral,
    StringLiteral,
    BoolLiteral,
    NullLiteral,
    Identifier,
    BinaryExpr,
    UnaryExpr,
    CallExpr,
    MemberAccessExpr,
    IndexAccessExpr,
    ListLiteral,
    MapLiteral,
    AnonymousFunctionExpr,
)


class ASTVisitor(ABC):
    """Abstract base class for AST visitors."""

    @abstractmethod
    def visit_program(self, node: Program) -> Any:
        pass

    @abstractmethod
    def visit_block(self, node: BlockStmt) -> Any:
        pass

    @abstractmethod
    def visit_expression_stmt(self, node: ExpressionStmt) -> Any:
        pass

    @abstractmethod
    def visit_var_assignment(self, node: VarAssignmentStmt) -> Any:
        pass

    @abstractmethod
    def visit_say(self, node: SayStmt) -> Any:
        pass

    @abstractmethod
    def visit_if(self, node: IfStmt) -> Any:
        pass

    @abstractmethod
    def visit_while(self, node: WhileStmt) -> Any:
        pass

    @abstractmethod
    def visit_for(self, node: ForStmt) -> Any:
        pass

    @abstractmethod
    def visit_function_decl(self, node: FunctionDeclStmt) -> Any:
        pass

    @abstractmethod
    def visit_return(self, node: ReturnStmt) -> Any:
        pass

    @abstractmethod
    def visit_break(self, node: BreakStmt) -> Any:
        pass

    @abstractmethod
    def visit_continue(self, node: ContinueStmt) -> Any:
        pass

    @abstractmethod
    def visit_number_literal(self, node: NumberLiteral) -> Any:
        pass

    @abstractmethod
    def visit_string_literal(self, node: StringLiteral) -> Any:
        pass

    @abstractmethod
    def visit_bool_literal(self, node: BoolLiteral) -> Any:
        pass

    @abstractmethod
    def visit_null_literal(self, node: NullLiteral) -> Any:
        pass

    @abstractmethod
    def visit_identifier(self, node: Identifier) -> Any:
        pass

    @abstractmethod
    def visit_binary(self, node: BinaryExpr) -> Any:
        pass

    @abstractmethod
    def visit_unary(self, node: UnaryExpr) -> Any:
        pass

    @abstractmethod
    def visit_call(self, node: CallExpr) -> Any:
        pass

    @abstractmethod
    def visit_member_access(self, node: MemberAccessExpr) -> Any:
        pass

    @abstractmethod
    def visit_index_access(self, node: IndexAccessExpr) -> Any:
        pass

    @abstractmethod
    def visit_list_literal(self, node: ListLiteral) -> Any:
        pass

    @abstractmethod
    def visit_map_literal(self, node: MapLiteral) -> Any:
        pass

    @abstractmethod
    def visit_anonymous_function(self, node: AnonymousFunctionExpr) -> Any:
        pass
