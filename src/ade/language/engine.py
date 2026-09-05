"""LanguageEngine: The unified compiler coordinator for custom DSLs and languages."""

import re
from typing import Any, Callable, Dict, List, Optional
from ade.diagnostics.diagnostic import Diagnostic, Severity
from ade.diagnostics.reporter import DiagnosticReporter
from ade.language.ast import DSLNode
from ade.language.evaluator import DSLContext, DSLEvaluationError, DSLEvaluator
from ade.language.parser import DSLParseError, DSLParser
from ade.language.tokens import DSLLexer, DSLLexerError, DSLToken, LexerRule


class LanguageEngine:
    """The central compiler & interpreter builder for custom languages and DSLs."""

    def __init__(self, name: str = "DSL"):
        self.name = name
        self.lexer_rules: List[LexerRule] = []
        self.evaluator_engine = DSLEvaluator()

        # Temporary parser configuration callbacks
        self._parser_setup: List[Callable[[DSLParser], None]] = []

    # --- Token & Lexer Rules ---

    def token(
        self,
        name: str,
        pattern: str,
        ignore: bool = False,
        converter: Optional[Callable[[str], Any]] = None,
    ) -> "LanguageEngine":
        """Define a token pattern using a regular expression."""
        compiled = re.compile(pattern)
        self.lexer_rules.append(
            LexerRule(name=name, pattern=compiled, ignore=ignore, converter=converter)
        )
        return self

    def ignore(self, pattern: str) -> "LanguageEngine":
        """Convenience method to define whitespace or comment patterns to skip."""
        name = f"IGNORE_{len(self.lexer_rules)}"
        return self.token(name, pattern, ignore=True)

    # --- Grammar & Parser Configuration ---

    def literal(self, token_type: str, node_type: Optional[str] = None) -> "LanguageEngine":
        """Register a token type as a literal expression value."""
        self._parser_setup.append(lambda p: p.register_literal(token_type, node_type))
        return self

    def prefix(
        self,
        token_type: str,
        precedence: int,
        node_type: Optional[str] = None,
        handler: Optional[Callable] = None,
    ) -> "LanguageEngine":
        """Register a prefix operator rule."""
        self._parser_setup.append(
            lambda p: p.register_prefix(token_type, precedence, node_type, handler)
        )
        return self

    def infix(
        self,
        token_type: str,
        precedence: int,
        node_type: Optional[str] = None,
        associativity: str = "left",
        handler: Optional[Callable] = None,
    ) -> "LanguageEngine":
        """Register an infix binary operator rule with precedence and associativity."""
        self._parser_setup.append(
            lambda p: p.register_infix(token_type, precedence, node_type, associativity, handler)
        )
        return self

    def group(self, open_token: str, close_token: str) -> "LanguageEngine":
        """Register grouped sub-expressions (e.g. parentheses '(' and ')')."""
        self._parser_setup.append(lambda p: p.register_group(open_token, close_token))
        return self

    def statement(self, token_type: str, handler: Callable) -> "LanguageEngine":
        """Register a custom statement rule."""
        self._parser_setup.append(lambda p: p.register_statement(token_type, handler))
        return self

    def rule(self, name: str, handler: Callable) -> "LanguageEngine":
        """Register a custom grammar production rule."""
        self._parser_setup.append(lambda p: p.register_rule(name, handler))
        return self

    # --- Evaluation Handlers ---

    def evaluator(self, node_type: str, handler: Callable) -> "LanguageEngine":
        """Register an AST node evaluation handler."""
        self.evaluator_engine.register(node_type, handler)
        return self

    def binary_op(
        self,
        token_type: str,
        precedence: int,
        node_type: str,
        eval_fn: Callable[[Any, Any], Any],
        associativity: str = "left",
    ) -> "LanguageEngine":
        """All-in-one helper: registers an infix operator rule and auto-evaluates both children."""
        self.infix(token_type, precedence, node_type, associativity)

        def _eval_binary(node: DSLNode, ctx: DSLContext) -> Any:
            left_val = ctx.eval(node.children[0])
            right_val = ctx.eval(node.children[1])
            return eval_fn(left_val, right_val)

        self.evaluator(node_type, _eval_binary)
        return self

    def prefix_op(
        self,
        token_type: str,
        precedence: int,
        node_type: str,
        eval_fn: Callable[[Any], Any],
    ) -> "LanguageEngine":
        """All-in-one helper: registers a prefix operator rule and evaluates its child."""
        self.prefix(token_type, precedence, node_type)

        def _eval_prefix(node: DSLNode, ctx: DSLContext) -> Any:
            operand = ctx.eval(node.children[0])
            return eval_fn(operand)

        self.evaluator(node_type, _eval_prefix)
        return self

    # --- Execution Pipeline ---

    def tokenize(self, source: str, file_path: str = "<dsl>") -> List[DSLToken]:
        """Tokenize custom DSL source code."""
        lexer = DSLLexer(rules=self.lexer_rules, source=source, file_path=file_path)
        return lexer.tokenize()

    def build_parser(self, tokens: List[DSLToken], source: str, file_path: str = "<dsl>") -> DSLParser:
        """Create and configure a parser for the token stream."""
        parser = DSLParser(tokens=tokens, source_code=source, file_path=file_path)
        for setup in self._parser_setup:
            setup(parser)
        return parser

    def parse(self, source: str, file_path: str = "<dsl>") -> DSLNode:
        """Parse source code into an AST (DSLNode)."""
        tokens = self.tokenize(source, file_path=file_path)
        parser = self.build_parser(tokens, source, file_path=file_path)
        return parser.parse()

    def execute(
        self,
        source: str,
        variables: Optional[Dict[str, Any]] = None,
        file_path: str = "<dsl>",
    ) -> Any:
        """Parse and execute custom DSL source code, returning the evaluated result."""
        ast = self.parse(source, file_path=file_path)
        ctx = DSLContext(
            evaluator=self.evaluator_engine,
            variables=variables or {},
            source_code=source,
        )
        return self.evaluator_engine.evaluate(ast, ctx)
