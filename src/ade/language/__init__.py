"""Ade Language-Building Platform.

Provides compiler construction tools, composable Pratt parsers, lexers, AST
abstractions, and runtime evaluators for domain-specific languages (DSLs).
"""

from ade.language.ast import DSLNode
from ade.language.engine import LanguageEngine
from ade.language.evaluator import DSLContext, DSLEvaluationError, DSLEvaluator
from ade.language.parser import DSLParseError, DSLParser
from ade.language.tokens import DSLLexer, DSLLexerError, DSLToken, LexerRule

__all__ = [
    "LanguageEngine",
    "DSLNode",
    "DSLEvaluator",
    "DSLContext",
    "DSLEvaluationError",
    "DSLParser",
    "DSLParseError",
    "DSLLexer",
    "DSLLexerError",
    "DSLToken",
    "LexerRule",
]
