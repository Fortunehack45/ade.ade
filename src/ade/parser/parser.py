"""Parser for the Ade programming language."""

from typing import List, Optional, Union
from ade.diagnostics.span import SourceSpan
from ade.lexer.token import Token, TokenType
from ade.ast.nodes import (
    Program,
    Statement,
    Expression,
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
    NamedArgExpr,
    MemberAccessExpr,
    IndexAccessExpr,
    ListLiteral,
    MapLiteral,
    MapEntry,
    AnonymousFunctionExpr,
    StringInterpolationExpr,
    ImportStmt,
    FromImportStmt,
    ClassDeclStmt,
)
from ade.parser.errors import ParseError


class Parser:
    """Parses a stream of tokens into an Ade Abstract Syntax Tree (AST)."""

    def __init__(self, tokens: List[Token], source_code: Optional[str] = None):
        self.tokens = tokens
        self.source_code = source_code
        self.current = 0

    def parse(self) -> Program:
        """Parse all tokens into a Program node."""
        statements: List[Statement] = []
        self._skip_newlines()

        first_span = self._peek().span
        while not self._is_at_end():
            stmt = self._parse_declaration_or_statement()
            if stmt is not None:
                statements.append(stmt)
            self._skip_newlines()

        last_span = self._previous().span if self.current > 0 else first_span
        program_span = SourceSpan.merge(first_span, last_span)
        return Program(span=program_span, statements=statements)

    # ========================================================================
    # Token Navigation Helpers
    # ========================================================================

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _check(self, token_type: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().type == token_type

    def _match(self, *types: TokenType) -> bool:
        for t in types:
            if self._check(t):
                self._advance()
                return True
        return False

    def _expect(
        self,
        token_type: TokenType,
        message: str,
        hint: Optional[str] = None,
        suggested_fix: Optional[str] = None,
    ) -> Token:
        if self._check(token_type):
            return self._advance()

        current_token = self._peek()
        raise ParseError(
            message=message,
            span=current_token.span,
            source_code=self.source_code,
            hint=hint,
            suggested_fix=suggested_fix,
        )

    def _skip_newlines(self) -> None:
        while self._match(TokenType.NEWLINE):
            pass

    # ========================================================================
    # Statement Parsing
    # ========================================================================

    def _parse_declaration_or_statement(self) -> Statement:
        if self._match(TokenType.FUNCTION):
            # Check if this is a named function declaration
            if self._check(TokenType.IDENTIFIER):
                return self._parse_function_declaration()
            # Otherwise it's an anonymous function in an expression
            self.current -= 1

        if self._match(TokenType.IMPORT):
            return self._parse_import_statement()

        if self._match(TokenType.FROM):
            return self._parse_from_import_statement()

        if self._match(TokenType.CLASS):
            return self._parse_class_declaration()

        if self._match(TokenType.SAY):
            return self._parse_say_statement()

        if self._match(TokenType.IF):
            return self._parse_if_statement()

        if self._match(TokenType.WHILE):
            return self._parse_while_statement()

        if self._match(TokenType.FOR):
            return self._parse_for_statement()

        if self._match(TokenType.RETURN):
            return self._parse_return_statement()

        if self._match(TokenType.BREAK):
            return BreakStmt(span=self._previous().span)

        if self._match(TokenType.CONTINUE):
            return ContinueStmt(span=self._previous().span)

        if self._check(TokenType.LBRACE):
            return self._parse_block()

        return self._parse_assignment_or_expression_statement()

    def _parse_import_statement(self) -> ImportStmt:
        import_token = self._previous()
        module_token = self._expect(
            TokenType.IDENTIFIER,
            message="expected module name after 'import'",
            hint="Provide a module name to import, e.g. 'import math'."
        )
        alias = None
        if self._match(TokenType.AS):
            alias_token = self._expect(
                TokenType.IDENTIFIER,
                message="expected alias name after 'as'",
                hint="Provide an alias name, e.g. 'import math as m'."
            )
            alias = alias_token.lexeme
        span = SourceSpan.merge(import_token.span, self._previous().span)
        return ImportStmt(span=span, module_name=module_token.lexeme, alias=alias)

    def _parse_from_import_statement(self) -> FromImportStmt:
        from_token = self._previous()
        module_token = self._expect(
            TokenType.IDENTIFIER,
            message="expected module name after 'from'",
            hint="Provide a module name, e.g. 'from math import sqrt'."
        )
        self._expect(
            TokenType.IMPORT,
            message="expected 'import' after module name in from-import statement",
            hint="Use 'from <module> import <symbols>'."
        )
        symbols: List[tuple[str, Optional[str]]] = []
        while True:
            self._skip_newlines()
            sym_token = self._expect(
                TokenType.IDENTIFIER,
                message="expected symbol name to import",
                hint="Specify function, class, or variable name to import."
            )
            alias = None
            if self._match(TokenType.AS):
                alias_token = self._expect(
                    TokenType.IDENTIFIER,
                    message="expected alias name after 'as'",
                )
                alias = alias_token.lexeme
            symbols.append((sym_token.lexeme, alias))
            self._skip_newlines()
            if not self._match(TokenType.COMMA):
                break
        span = SourceSpan.merge(from_token.span, self._previous().span)
        return FromImportStmt(span=span, module_name=module_token.lexeme, symbols=symbols)

    def _parse_class_declaration(self) -> ClassDeclStmt:
        class_token = self._previous()
        name_token = self._expect(
            TokenType.IDENTIFIER,
            message="expected class name after 'class'",
            hint="Classes in Ade are declared with an identifier name, e.g. 'class User'."
        )
        superclass = None
        if self._match(TokenType.LESS):
            super_token = self._expect(TokenType.IDENTIFIER, message="expected superclass name")
            superclass = super_token.lexeme

        self._skip_newlines()
        self._expect(
            TokenType.LBRACE,
            message="expected '{' before class body",
            hint="Enclose class members and methods inside '{ ... }'."
        )

        fields: List[str] = []
        methods: List[FunctionDeclStmt] = []
        self._skip_newlines()

        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            if self._match(TokenType.FUNCTION):
                methods.append(self._parse_function_declaration())
            elif self._match(TokenType.IDENTIFIER):
                fields.append(self._previous().lexeme)
            else:
                curr = self._peek()
                raise ParseError(
                    message=f"Unexpected token '{curr.lexeme}' in class body.",
                    span=curr.span,
                    source_code=self.source_code,
                    hint="Class bodies can contain field names or method definitions ('function name() { ... }')."
                )
            self._skip_newlines()

        end_brace = self._expect(
            TokenType.RBRACE,
            message="expected '}' after class body"
        )
        span = SourceSpan.merge(class_token.span, end_brace.span)
        return ClassDeclStmt(
            span=span,
            name=name_token.lexeme,
            superclass=superclass,
            fields=fields,
            methods=methods
        )

    def _parse_function_declaration(self) -> FunctionDeclStmt:
        func_token = self._previous()
        name_token = self._expect(
            TokenType.IDENTIFIER,
            message="expected function name after 'function'",
            hint="A function declaration requires an identifier name (e.g. 'function calculate()')."
        )
        self._expect(
            TokenType.LPAREN,
            message="expected '(' after function name",
            hint="Function parameters must follow the function name enclosed in parentheses."
        )

        params: List[str] = []
        self._skip_newlines()
        if not self._check(TokenType.RPAREN):
            while True:
                self._skip_newlines()
                param_token = self._expect(
                    TokenType.IDENTIFIER,
                    message="expected parameter name",
                    hint="Function parameters must be valid identifier names."
                )
                params.append(param_token.lexeme)
                self._skip_newlines()
                if not self._match(TokenType.COMMA):
                    break

        self._skip_newlines()
        self._expect(
            TokenType.RPAREN,
            message="expected ')' after parameter list",
            hint="Close the function parameter list with ')' before opening the body block."
        )

        self._skip_newlines()
        body = self._parse_block()
        span = SourceSpan.merge(func_token.span, body.span)
        return FunctionDeclStmt(span=span, name=name_token.lexeme, params=params, body=body)

    def _parse_say_statement(self) -> SayStmt:
        say_token = self._previous()
        expr = self._parse_expression()
        span = SourceSpan.merge(say_token.span, expr.span)
        return SayStmt(span=span, expression=expr)

    def _parse_if_statement(self) -> IfStmt:
        if_token = self._previous()
        condition = self._parse_expression()
        self._skip_newlines()
        then_branch = self._parse_block()

        else_branch: Optional[Statement] = None
        self._skip_newlines()
        if self._match(TokenType.ELSE):
            self._skip_newlines()
            if self._match(TokenType.IF):
                else_branch = self._parse_if_statement()
            else:
                else_branch = self._parse_block()

        end_span = else_branch.span if else_branch else then_branch.span
        span = SourceSpan.merge(if_token.span, end_span)
        return IfStmt(
            span=span, condition=condition, then_branch=then_branch, else_branch=else_branch
        )

    def _parse_while_statement(self) -> WhileStmt:
        while_token = self._previous()
        condition = self._parse_expression()
        self._skip_newlines()
        body = self._parse_block()
        span = SourceSpan.merge(while_token.span, body.span)
        return WhileStmt(span=span, condition=condition, body=body)

    def _parse_for_statement(self) -> ForStmt:
        for_token = self._previous()
        var_token = self._expect(
            TokenType.IDENTIFIER,
            message="expected variable name after 'for'",
            hint="Specify an iteration variable, e.g., 'for item in items'."
        )
        self._expect(
            TokenType.IN,
            message="expected 'in' after for loop variable",
            hint="Use 'in' followed by the collection expression to iterate over."
        )
        iterable = self._parse_expression()
        self._skip_newlines()
        body = self._parse_block()
        span = SourceSpan.merge(for_token.span, body.span)
        return ForStmt(span=span, variable=var_token.lexeme, iterable=iterable, body=body)

    def _parse_return_statement(self) -> ReturnStmt:
        return_token = self._previous()
        value: Optional[Expression] = None
        if not self._check(TokenType.NEWLINE) and not self._check(TokenType.RBRACE) and not self._is_at_end():
            value = self._parse_expression()
        end_span = value.span if value else return_token.span
        return ReturnStmt(span=SourceSpan.merge(return_token.span, end_span), value=value)

    def _parse_block(self) -> BlockStmt:
        start_brace = self._expect(
            TokenType.LBRACE,
            message="expected '{' before block body",
            hint="Blocks in Ade must be enclosed within curly braces '{ ... }'."
        )
        statements: List[Statement] = []
        self._skip_newlines()

        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            stmt = self._parse_declaration_or_statement()
            if stmt is not None:
                statements.append(stmt)
            self._skip_newlines()

        end_brace = self._expect(
            TokenType.RBRACE,
            message="expected '}' after block body",
            hint="Blocks opened with '{' must be terminated with a matching '}'."
        )
        span = SourceSpan.merge(start_brace.span, end_brace.span)
        return BlockStmt(span=span, statements=statements)

    def _parse_assignment_or_expression_statement(self) -> Statement:
        expr = self._parse_expression()

        # Check for assignment: target = value
        if self._match(TokenType.EQUAL):
            equal_token = self._previous()
            if not isinstance(expr, (Identifier, MemberAccessExpr, IndexAccessExpr)):
                raise ParseError(
                    message="Invalid assignment target.",
                    span=expr.span,
                    source_code=self.source_code,
                    hint="Only identifiers (variables), member access (obj.prop), or index access (arr[i]) can be assigned to."
                )
            value = self._parse_expression()
            span = SourceSpan.merge(expr.span, value.span)
            return VarAssignmentStmt(span=span, target=expr, value=value)

        return ExpressionStmt(span=expr.span, expression=expr)

    # ========================================================================
    # Expression Parsing (Pratt Precedence Climbing)
    # ========================================================================

    def _parse_expression(self) -> Expression:
        return self._parse_logical_or()

    def _parse_logical_or(self) -> Expression:
        expr = self._parse_logical_and()
        while self._match(TokenType.OR):
            op = self._previous()
            right = self._parse_logical_and()
            expr = BinaryExpr(
                span=SourceSpan.merge(expr.span, right.span),
                left=expr,
                operator=op,
                right=right,
            )
        return expr

    def _parse_logical_and(self) -> Expression:
        expr = self._parse_equality()
        while self._match(TokenType.AND):
            op = self._previous()
            right = self._parse_equality()
            expr = BinaryExpr(
                span=SourceSpan.merge(expr.span, right.span),
                left=expr,
                operator=op,
                right=right,
            )
        return expr

    def _parse_equality(self) -> Expression:
        expr = self._parse_relational()
        while self._match(TokenType.EQUAL_EQUAL, TokenType.BANG_EQUAL):
            op = self._previous()
            right = self._parse_relational()
            expr = BinaryExpr(
                span=SourceSpan.merge(expr.span, right.span),
                left=expr,
                operator=op,
                right=right,
            )
        return expr

    def _parse_relational(self) -> Expression:
        expr = self._parse_additive()
        while self._match(
            TokenType.LESS, TokenType.LESS_EQUAL, TokenType.GREATER, TokenType.GREATER_EQUAL
        ):
            op = self._previous()
            right = self._parse_additive()
            expr = BinaryExpr(
                span=SourceSpan.merge(expr.span, right.span),
                left=expr,
                operator=op,
                right=right,
            )
        return expr

    def _parse_additive(self) -> Expression:
        expr = self._parse_multiplicative()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op = self._previous()
            right = self._parse_multiplicative()
            expr = BinaryExpr(
                span=SourceSpan.merge(expr.span, right.span),
                left=expr,
                operator=op,
                right=right,
            )
        return expr

    def _parse_multiplicative(self) -> Expression:
        expr = self._parse_unary()
        while self._match(TokenType.STAR, TokenType.SLASH, TokenType.PERCENT):
            op = self._previous()
            right = self._parse_unary()
            expr = BinaryExpr(
                span=SourceSpan.merge(expr.span, right.span),
                left=expr,
                operator=op,
                right=right,
            )
        return expr

    def _parse_unary(self) -> Expression:
        if self._match(TokenType.MINUS, TokenType.NOT):
            op = self._previous()
            operand = self._parse_unary()
            return UnaryExpr(
                span=SourceSpan.merge(op.span, operand.span),
                operator=op,
                operand=operand,
            )
        return self._parse_postfix()

    def _parse_postfix(self) -> Expression:
        expr = self._parse_primary()

        while True:
            if self._match(TokenType.LPAREN):
                # Call expression: expr(arg1, arg2)
                args: List[Expression] = []
                self._skip_newlines()
                if not self._check(TokenType.RPAREN):
                    while True:
                        self._skip_newlines()
                        if (
                            self._check(TokenType.IDENTIFIER)
                            and self.current + 1 < len(self.tokens)
                            and self.tokens[self.current + 1].type == TokenType.COLON
                        ):
                            name_tok = self._advance()
                            self._advance()  # consume ':'
                            self._skip_newlines()
                            val_expr = self._parse_expression()
                            arg_span = SourceSpan.merge(name_tok.span, val_expr.span)
                            args.append(NamedArgExpr(span=arg_span, name=name_tok.lexeme, value=val_expr))
                        else:
                            args.append(self._parse_expression())
                        self._skip_newlines()
                        if not self._match(TokenType.COMMA):
                            break
                self._skip_newlines()
                rparen = self._expect(
                    TokenType.RPAREN,
                    message="expected ')' after function arguments",
                    hint="The function call is missing a closing ')'.",
                    suggested_fix=None,
                )
                expr = CallExpr(
                    span=SourceSpan.merge(expr.span, rparen.span),
                    callee=expr,
                    arguments=args,
                )
            elif self._match(TokenType.DOT):
                # Member access: expr.member
                member_token = self._expect(
                    TokenType.IDENTIFIER,
                    message="expected property or method name after '.'",
                    hint="Access an object property with an identifier name, e.g., 'user.name'."
                )
                expr = MemberAccessExpr(
                    span=SourceSpan.merge(expr.span, member_token.span),
                    object=expr,
                    member=member_token.lexeme,
                )
            elif self._match(TokenType.LBRACKET):
                # Index access: expr[index]
                self._skip_newlines()
                index_expr = self._parse_expression()
                self._skip_newlines()
                rbrack = self._expect(
                    TokenType.RBRACKET,
                    message="expected ']' after index expression",
                    hint="Index expressions must be closed with ']'."
                )
                expr = IndexAccessExpr(
                    span=SourceSpan.merge(expr.span, rbrack.span),
                    object=expr,
                    index=index_expr,
                )
            else:
                break

        return expr

    def _parse_primary(self) -> Expression:
        if self._match(TokenType.NUMBER):
            token = self._previous()
            return NumberLiteral(span=token.span, value=token.literal)

        if self._match(TokenType.STRING):
            token = self._previous()
            val = str(token.literal)
            if "{" in val and "}" in val:
                parts = self._parse_interpolated_string(val, token.span)
                if len(parts) == 1 and isinstance(parts[0], str):
                    return StringLiteral(span=token.span, value=parts[0])
                return StringInterpolationExpr(span=token.span, parts=parts)
            return StringLiteral(span=token.span, value=token.literal)

        if self._match(TokenType.TRUE):
            return BoolLiteral(span=self._previous().span, value=True)

        if self._match(TokenType.FALSE):
            return BoolLiteral(span=self._previous().span, value=False)

        if self._match(TokenType.NULL):
            return NullLiteral(span=self._previous().span)

        if self._match(TokenType.IDENTIFIER):
            token = self._previous()
            return Identifier(span=token.span, name=token.lexeme)

        if self._match(TokenType.LPAREN):
            # Grouped expression: (expr)
            start_paren = self._previous()
            self._skip_newlines()
            expr = self._parse_expression()
            self._skip_newlines()
            end_paren = self._expect(
                TokenType.RPAREN,
                message="expected ')' after grouped expression",
                hint="Parentheses in expressions must be closed."
            )
            expr.span = SourceSpan.merge(start_paren.span, end_paren.span)
            return expr

        if self._match(TokenType.LBRACKET):
            # List literal: [elem1, elem2, ...]
            return self._parse_list_literal()

        if self._match(TokenType.LBRACE):
            # Map literal: { key: value, ... }
            return self._parse_map_literal()

        if self._match(TokenType.FUNCTION):
            # Anonymous function: function(params) { body }
            return self._parse_anonymous_function()

        token = self._peek()
        raise ParseError(
            message=f"Unexpected token '{token.lexeme}'. Expected an expression.",
            span=token.span,
            source_code=self.source_code,
            hint="Check for missing operands, mismatched brackets, or unexpected keywords."
        )

    def _parse_list_literal(self) -> ListLiteral:
        start_bracket = self._previous()
        elements: List[Expression] = []
        self._skip_newlines()

        if not self._check(TokenType.RBRACKET):
            while True:
                self._skip_newlines()
                elements.append(self._parse_expression())
                self._skip_newlines()
                if not self._match(TokenType.COMMA):
                    break

        self._skip_newlines()
        end_bracket = self._expect(
            TokenType.RBRACKET,
            message="expected ']' to close list literal",
            hint="List literals opened with '[' must end with ']'."
        )
        span = SourceSpan.merge(start_bracket.span, end_bracket.span)
        return ListLiteral(span=span, elements=elements)

    def _parse_map_literal(self) -> MapLiteral:
        start_brace = self._previous()
        entries: List[MapEntry] = []
        self._skip_newlines()

        if not self._check(TokenType.RBRACE):
            while True:
                self._skip_newlines()
                # Key can be an identifier or a string literal
                if self._match(TokenType.IDENTIFIER):
                    key_token = self._previous()
                    key_expr: Expression = StringLiteral(
                        span=key_token.span, value=key_token.lexeme
                    )
                elif self._match(TokenType.STRING):
                    key_token = self._previous()
                    key_expr = StringLiteral(
                        span=key_token.span, value=key_token.literal
                    )
                else:
                    curr = self._peek()
                    raise ParseError(
                        message=f"Invalid map key '{curr.lexeme}'. Expected an identifier or string.",
                        span=curr.span,
                        source_code=self.source_code,
                        hint="Keys in map literals must be identifiers or strings, e.g., '{ name: \"Ade\", \"version\": 1 }'."
                    )

                self._skip_newlines()
                self._expect(
                    TokenType.COLON,
                    message="expected ':' after map key",
                    hint="Separate map keys and values with a colon ':', e.g. '{ key: value }'."
                )
                self._skip_newlines()
                val_expr = self._parse_expression()
                entries.append(MapEntry(key=key_expr, value=val_expr))

                self._skip_newlines()
                if not self._match(TokenType.COMMA):
                    break

        self._skip_newlines()
        end_brace = self._expect(
            TokenType.RBRACE,
            message="expected '}' to close map literal",
            hint="Map literals opened with '{' must be closed with '}'."
        )
        span = SourceSpan.merge(start_brace.span, end_brace.span)
        return MapLiteral(span=span, entries=entries)

    def _parse_anonymous_function(self) -> AnonymousFunctionExpr:
        func_token = self._previous()
        self._expect(
            TokenType.LPAREN,
            message="expected '(' after 'function'",
            hint="Anonymous functions declare parameter lists enclosed in '(', e.g. 'function(x) { ... }'."
        )

        params: List[str] = []
        self._skip_newlines()
        if not self._check(TokenType.RPAREN):
            while True:
                self._skip_newlines()
                param_token = self._expect(
                    TokenType.IDENTIFIER,
                    message="expected parameter name",
                    hint="Function parameters must be identifiers."
                )
                params.append(param_token.lexeme)
                self._skip_newlines()
                if not self._match(TokenType.COMMA):
                    break

        self._skip_newlines()
        self._expect(
            TokenType.RPAREN,
            message="expected ')' after function parameters",
            hint="Close the function parameter list with ')'."
        )

        self._skip_newlines()
        body = self._parse_block()
        span = SourceSpan.merge(func_token.span, body.span)
        return AnonymousFunctionExpr(span=span, params=params, body=body)

    def _parse_interpolated_string(
        self, text: str, span: SourceSpan
    ) -> List[Union[str, Expression]]:
        """Decompose a string containing '{...}' into string slices and parsed Ade expressions."""
        from ade.lexer.lexer import Lexer

        parts: List[Union[str, Expression]] = []
        i = 0
        n = len(text)
        current_str: List[str] = []

        while i < n:
            if text[i] == "{" and (i == 0 or text[i - 1] != "\\"):
                brace_depth = 1
                j = i + 1
                while j < n and brace_depth > 0:
                    if text[j] == "{" and text[j - 1] != "\\":
                        brace_depth += 1
                    elif text[j] == "}" and text[j - 1] != "\\":
                        brace_depth -= 1
                    j += 1

                if brace_depth == 0:
                    if current_str:
                        parts.append("".join(current_str))
                        current_str = []
                    expr_code = text[i + 1 : j - 1].strip()
                    if expr_code:
                        try:
                            sub_lexer = Lexer(expr_code, file_path=span.file)
                            sub_tokens = sub_lexer.tokenize()
                            sub_parser = Parser(sub_tokens, source_code=expr_code)
                            sub_expr = sub_parser._parse_expression()
                            parts.append(sub_expr)
                        except Exception:
                            # Fallback if inner expression fails to parse
                            parts.append("{" + expr_code + "}")
                    i = j
                    continue

            current_str.append(text[i])
            i += 1

        if current_str:
            parts.append("".join(current_str))

        return parts
