"""Foundations for the Ade Language-Building Platform."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from ade.lexer.lexer import Lexer
from ade.parser.parser import Parser
from ade.ast.nodes import Program
from ade.interpreter.interpreter import Interpreter
from ade.runtime.environment import Environment
from ade.runtime.value import AdeValue


class LanguageDefinition(ABC):
    """Abstract base class for defining custom languages and DSLs on top of Ade."""

    def __init__(self, name: str, version: str = "0.1.0"):
        self.name = name
        self.version = version

    @abstractmethod
    def build_lexer(self, source: str, file_path: str = "<stdin>") -> Any:
        """Construct the lexer for this language."""
        pass

    @abstractmethod
    def build_parser(self, tokens: List[Any], source_code: Optional[str] = None) -> Any:
        """Construct the parser for this language."""
        pass

    @abstractmethod
    def build_interpreter(self, environment: Optional[Environment] = None) -> Any:
        """Construct the runtime evaluation engine."""
        pass


class AdeLanguagePipeline:
    """Standard compiler pipeline executing the full compilation/interpretation flow."""

    def __init__(
        self,
        language: Optional[LanguageDefinition] = None,
        environment: Optional[Environment] = None,
    ):
        self.language = language
        self.environment = environment or Environment()

    def run_source(
        self, source: str, file_path: str = "<stdin>", output_stream: Optional[Any] = None
    ) -> AdeValue:
        """Execute source code through the standard Ade pipeline."""
        lexer = Lexer(source=source, file_path=file_path)
        tokens = lexer.tokenize()

        parser = Parser(tokens=tokens, source_code=source)
        program = parser.parse()

        interpreter = Interpreter(
            output_stream=output_stream,
            source_code=source,
            environment=self.environment,
        )
        return interpreter.interpret(program)
