"""Independent module resolution and loading for Ade."""

import os
from typing import Dict, Optional
from ade.diagnostics.span import SourceSpan
from ade.runtime.value import AdeModule
from ade.runtime.environment import Environment
from ade.stdlib import get_stdlib_module
from ade.interpreter.errors import AdeRuntimeError


class ModuleLoader:
    """Resolves and loads Ade project-local and standard library modules."""

    def __init__(self):
        self.module_cache: Dict[str, AdeModule] = {}
        self._loading_stack: set[str] = set()

    def load_module(
        self,
        module_name: str,
        current_file_path: str,
        span: SourceSpan,
        interpreter: "Interpreter",
    ) -> AdeModule:
        """Resolve, parse, execute, and cache an Ade module."""
        # 1. Check Standard Library
        stdlib_mod = get_stdlib_module(module_name)
        if stdlib_mod is not None:
            return stdlib_mod

        # 2. Check Project-Local Files
        base_dir = os.path.dirname(os.path.abspath(current_file_path)) if current_file_path != "<stdin>" and current_file_path != "<repl>" else os.getcwd()

        candidate_paths = [
            os.path.join(base_dir, f"{module_name}.ade"),
            os.path.join(base_dir, module_name, "init.ade"),
            os.path.join(base_dir, module_name, "main.ade"),
        ]

        resolved_path: Optional[str] = None
        for p in candidate_paths:
            if os.path.isfile(p):
                resolved_path = os.path.abspath(p)
                break

        if resolved_path is None:
            raise AdeRuntimeError(
                f"Cannot find module '{module_name}'.",
                span=span,
                source_code=interpreter.source_code,
                hint=f"Looked for '{module_name}.ade' in '{base_dir}'.",
                suggested_fix=f"# Create file '{module_name}.ade'"
            )

        # Check Cache
        if resolved_path in self.module_cache:
            return self.module_cache[resolved_path]

        # Prevent circular imports deadlock
        if resolved_path in self._loading_stack:
            raise AdeRuntimeError(
                f"Circular import detected for module '{module_name}'.",
                span=span,
                source_code=interpreter.source_code,
            )

        self._loading_stack.add(resolved_path)
        try:
            with open(resolved_path, "r", encoding="utf-8") as f:
                source = f.read()

            from ade.lexer.lexer import Lexer
            from ade.parser.parser import Parser
            from ade.interpreter.interpreter import Interpreter

            tokens = Lexer(source=source, file_path=resolved_path).tokenize()
            program = Parser(tokens=tokens, source_code=source).parse()

            # Execute in an isolated lexical environment
            module_env = Environment()
            sub_interpreter = Interpreter(
                output_stream=interpreter.output_stream,
                source_code=source,
                environment=module_env,
                current_file_path=resolved_path,
                module_loader=self,
            )
            sub_interpreter.interpret(program)

            module = AdeModule(name=module_name, exports=dict(module_env.values))
            self.module_cache[resolved_path] = module
            return module
        finally:
            self._loading_stack.remove(resolved_path)
