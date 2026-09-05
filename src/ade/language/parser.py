"""Composable parser and Pratt expression engine for custom DSLs."""

from typing import Any, Callable, Dict, List, Optional
from ade.diagnostics.diagnostic import Diagnostic, Severity
from ade.diagnostics.span import SourceSpan
from ade.language.ast import DSLNode
from ade.language.tokens import DSLToken


class DSLParseError(Exception):
    """Exception raised when a custom DSL syntax error occurs."""
    def __init__(self, diagnostic: Diagnostic):
        super().__init__(diagnostic.message)
        self.diagnostic = diagnostic


class InfixRule:
    def __init__(
        self,
        token_type: str,
        precedence: int,
        node_type: str,
        associativity: str = "left",
        handler: Optional[Callable[["DSLParser", DSLNode, DSLToken], DSLNode]] = None,
    ):
        self.token_type = token_type
        self.precedence = precedence
        self.node_type = node_type
        self.associativity = associativity  # "left" or "right"
        self.handler = handler


class PrefixRule:
    def __init__(
        self,
        token_type: str,
        precedence: int,
        node_type: str,
        handler: Optional[Callable[["DSLParser", DSLToken], DSLNode]] = None,
    ):
        self.token_type = token_type
        self.precedence = precedence
        self.node_type = node_type
        self.handler = handler


class DSLParser:
    """Configurable Pratt and recursive-descent parser for custom DSLs."""

    def __init__(
        self,
        tokens: List[DSLToken],
        source_code: str = "",
        file_path: str = "<dsl>",
    ):
        self.tokens = tokens
        self.source_code = source_code
        self.file_path = file_path
        self.current = 0

        # Pratt rule registries
        self.prefix_rules: Dict[str, PrefixRule] = {}
        self.infix_rules: Dict[str, InfixRule] = {}

        # Custom grammar rule and statement registries
        self.custom_rules: Dict[str, Callable[["DSLParser"], DSLNode]] = {}
        self.statement_rules: Dict[str, Callable[["DSLParser", DSLToken], DSLNode]] = {}

    # --- Configuration Methods ---

    def register_literal(self, token_type: str, node_type: Optional[str] = None) -> None:
        """Register a token type as a literal expression value."""
        target_type = node_type or token_type.lower()

        def _handle_literal(parser: "DSLParser", token: DSLToken) -> DSLNode:
            return DSLNode(type=target_type, value=token.value, span=token.span)

        self.prefix_rules[token_type] = PrefixRule(
            token_type=token_type,
            precedence=0,
            node_type=target_type,
            handler=_handle_literal,
        )

    def register_prefix(
        self,
        token_type: str,
        precedence: int,
        node_type: Optional[str] = None,
        handler: Optional[Callable[["DSLParser", DSLToken], DSLNode]] = None,
    ) -> None:
        """Register a prefix operator (e.g. unary minus, not)."""
        target_type = node_type or token_type.lower()

        if handler is None:
            def _default_prefix(parser: "DSLParser", token: DSLToken) -> DSLNode:
                operand = parser.parse_expression(precedence)
                span = SourceSpan.merge(token.span, operand.span)
                return DSLNode(type=target_type, value=token.lexeme, children=[operand], span=span)
            handler = _default_prefix

        self.prefix_rules[token_type] = PrefixRule(
            token_type=token_type,
            precedence=precedence,
            node_type=target_type,
            handler=handler,
        )

    def register_infix(
        self,
        token_type: str,
        precedence: int,
        node_type: Optional[str] = None,
        associativity: str = "left",
        handler: Optional[Callable[["DSLParser", DSLNode, DSLToken], DSLNode]] = None,
    ) -> None:
        """Register an infix binary operator with precedence and associativity."""
        target_type = node_type or token_type.lower()

        if handler is None:
            def _default_infix(parser: "DSLParser", left: DSLNode, token: DSLToken) -> DSLNode:
                # Right associative operators use precedence - 1
                next_prec = precedence - 1 if associativity == "right" else precedence
                right = parser.parse_expression(next_prec)
                span = SourceSpan.merge(left.span, right.span)
                return DSLNode(
                    type=target_type,
                    value=token.lexeme,
                    children=[left, right],
                    span=span,
                )
            handler = _default_infix

        self.infix_rules[token_type] = InfixRule(
            token_type=token_type,
            precedence=precedence,
            node_type=target_type,
            associativity=associativity,
            handler=handler,
        )

    def register_group(self, open_token: str, close_token: str) -> None:
        """Register paired enclosing delimiters for grouping expressions (e.g. '(' and ')')."""
        def _handle_group(parser: "DSLParser", token: DSLToken) -> DSLNode:
            expr = parser.parse_expression(0)
            parser.consume(close_token, f"Expected closing '{close_token}' after grouped expression.")
            return expr

        self.prefix_rules[open_token] = PrefixRule(
            token_type=open_token,
            precedence=0,
            node_type="group",
            handler=_handle_group,
        )

    def register_statement(
        self, token_type: str, handler: Callable[["DSLParser", DSLToken], DSLNode]
    ) -> None:
        """Register a custom statement rule triggered when starting with a given token."""
        self.statement_rules[token_type] = handler

    def register_rule(self, name: str, handler: Callable[["DSLParser"], DSLNode]) -> None:
        """Register a named grammar production rule."""
        self.custom_rules[name] = handler

    # --- Parser State & Navigation ---

    def peek(self) -> DSLToken:
        """Return the current token without consuming it."""
        return self.tokens[self.current]

    def previous(self) -> DSLToken:
        """Return the most recently consumed token."""
        return self.tokens[self.current - 1]

    def is_at_end(self) -> bool:
        """Check if we have reached EOF."""
        return self.peek().is_eof

    def check(self, token_type: str) -> bool:
        """Check if the current token matches token_type."""
        if self.is_at_end():
            return False
        return self.peek().type == token_type

    def advance(self) -> DSLToken:
        """Consume and return the current token."""
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def match(self, *token_types: str) -> bool:
        """Advance and return True if current token matches any of the types."""
        for tt in token_types:
            if self.check(tt):
                self.advance()
                return True
        return False

    def consume(self, token_type: str, message: str) -> DSLToken:
        """Consume the specified token type or raise a formatted diagnostic error."""
        if self.check(token_type):
            return self.advance()

        current_token = self.peek()
        diag = Diagnostic(
            severity=Severity.ERROR,
            title="DSL Syntax Error",
            message=f"{message} Found '{current_token.lexeme or current_token.type}' instead.",
            span=current_token.span,
            source_code=self.source_code,
            hint=f"Expected token of type '{token_type}'.",
            suggested_fix=f"Insert '{token_type}' before '{current_token.lexeme}'.",
        )
        raise DSLParseError(diag)

    # --- Core Parsing Methods ---

    def parse_expression(self, precedence: int = 0) -> DSLNode:
        """Parse an expression using the Pratt precedence algorithm."""
        if self.is_at_end():
            tok = self.peek()
            diag = Diagnostic(
                severity=Severity.ERROR,
                title="DSL Syntax Error",
                message="Unexpected end of input while parsing expression.",
                span=tok.span,
                source_code=self.source_code,
                hint="An operand or expression was expected here.",
                suggested_fix="Complete the expression.",
            )
            raise DSLParseError(diag)

        token = self.advance()
        prefix_rule = self.prefix_rules.get(token.type)
        if prefix_rule is None:
            diag = Diagnostic(
                severity=Severity.ERROR,
                title="DSL Syntax Error",
                message=f"Unexpected token '{token.lexeme or token.type}' at start of expression.",
                span=token.span,
                source_code=self.source_code,
                hint=f"No expression rule registered for token type '{token.type}'.",
                suggested_fix="Check your expression or register this token in the language engine.",
            )
            raise DSLParseError(diag)

        left = prefix_rule.handler(self, token)

        while not self.is_at_end():
            next_token = self.peek()
            infix_rule = self.infix_rules.get(next_token.type)
            if infix_rule is None or infix_rule.precedence <= precedence:
                break

            self.advance()
            left = infix_rule.handler(self, left, next_token)

        return left

    def parse_statement(self) -> DSLNode:
        """Parse a single statement or expression."""
        if self.is_at_end():
            return DSLNode(type="empty", span=self.peek().span)

        # Check statement rules
        token = self.peek()
        if token.type in self.statement_rules:
            self.advance()
            return self.statement_rules[token.type](self, token)

        # Otherwise parse an expression
        return self.parse_expression(0)

    def parse_rule(self, name: str) -> DSLNode:
        """Execute a named grammar production rule."""
        if name not in self.custom_rules:
            raise KeyError(f"No grammar rule named '{name}' is registered.")
        return self.custom_rules[name](self)

    def parse(self) -> DSLNode:
        """Parse all tokens into a root 'program' DSLNode."""
        statements: List[DSLNode] = []
        while not self.is_at_end():
            # Skip empty newlines/semicolons if present as tokens
            if self.check("NEWLINE") or self.check("SEMICOLON"):
                self.advance()
                continue
            stmt = self.parse_statement()
            statements.append(stmt)
            if self.check("NEWLINE") or self.check("SEMICOLON"):
                self.advance()

        first_span = statements[0].span if statements else self.peek().span
        last_span = statements[-1].span if statements else self.peek().span
        root_span = SourceSpan.merge(first_span, last_span)
        return DSLNode(type="program", children=statements, span=root_span)
