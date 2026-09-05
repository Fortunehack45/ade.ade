"""AST visitor and evaluation runtime for custom DSLs."""

from typing import Any, Callable, Dict, List, Optional
from ade.diagnostics.diagnostic import Diagnostic, Severity
from ade.diagnostics.span import SourceSpan
from ade.language.ast import DSLNode


class DSLEvaluationError(Exception):
    """Exception raised when an error occurs during DSL AST evaluation."""
    def __init__(self, diagnostic: Diagnostic):
        super().__init__(diagnostic.message)
        self.diagnostic = diagnostic


class DSLContext:
    """Execution context and symbol table for DSL runtime evaluation."""

    def __init__(
        self,
        evaluator: "DSLEvaluator",
        variables: Optional[Dict[str, Any]] = None,
        source_code: str = "",
    ):
        self.evaluator = evaluator
        self.variables: Dict[str, Any] = variables or {}
        self.source_code = source_code

    def get(self, name: str, default: Any = None) -> Any:
        return self.variables.get(name, default)

    def set(self, name: str, value: Any) -> None:
        self.variables[name] = value

    def eval(self, node: DSLNode) -> Any:
        """Evaluate a sub-node within this context."""
        return self.evaluator.evaluate(node, self)


class DSLEvaluator:
    """Configurable AST evaluator supporting both Python and Ade callbacks."""

    def __init__(self):
        self.handlers: Dict[str, Callable[..., Any]] = {}
        self._register_default_handlers()

    def _register_default_handlers(self) -> None:
        """Provide standard evaluation rules for common node types."""
        def _eval_program(node: DSLNode, ctx: DSLContext) -> Any:
            result = None
            for child in node.children:
                result = ctx.eval(child)
            return result

        def _eval_literal(node: DSLNode, ctx: DSLContext) -> Any:
            if node.type == "number" and isinstance(node.value, str):
                try:
                    return float(node.value) if "." in node.value else int(node.value)
                except ValueError:
                    pass
            return node.value

        def _eval_identifier(node: DSLNode, ctx: DSLContext) -> Any:
            var_name = str(node.value)
            if var_name in ctx.variables:
                return ctx.variables[var_name]
            diag = Diagnostic(
                severity=Severity.ERROR,
                title="DSL Name Error",
                message=f"Undefined variable or identifier '{var_name}' in custom DSL.",
                span=node.span,
                source_code=ctx.source_code,
                hint=f"Available variables: {', '.join(ctx.variables.keys()) or 'none'}",
                suggested_fix=f"Define '{var_name}' before referencing it.",
            )
            raise DSLEvaluationError(diag)

        self.handlers["program"] = _eval_program
        self.handlers["number"] = _eval_literal
        self.handlers["string"] = _eval_literal
        self.handlers["bool"] = _eval_literal
        self.handlers["null"] = _eval_literal
        self.handlers["literal"] = _eval_literal
        self.handlers["identifier"] = _eval_identifier

    def register(self, node_type: str, handler: Callable[..., Any]) -> None:
        """Register an evaluator function for a specific node type."""
        self.handlers[node_type] = handler

    def evaluate(self, node: DSLNode, ctx: Optional[DSLContext] = None) -> Any:
        """Evaluate an AST node."""
        if ctx is None:
            ctx = DSLContext(evaluator=self)

        handler = self.handlers.get(node.type)
        if handler is None:
            diag = Diagnostic(
                severity=Severity.ERROR,
                title="DSL Evaluation Error",
                message=f"No evaluator registered for AST node type '{node.type}'.",
                span=node.span,
                source_code=ctx.source_code,
                hint="Register a handler using engine.evaluator() or engine.binary_op().",
                suggested_fix=f"Add an evaluator for node type '{node.type}'.",
            )
            raise DSLEvaluationError(diag)

        try:
            # Check how many arguments handler expects
            import inspect
            if hasattr(handler, "__call__"):
                # Handle Ade callable objects (AdeFunction, etc.) if applicable
                from ade.runtime.value import AdeFunction, AdeValue
                if isinstance(handler, AdeFunction):
                    # Call via Ade function calling convention
                    from ade.interpreter.interpreter import Interpreter
                    interp = Interpreter(source_code=ctx.source_code)
                    
                    # If binary node with 2 children, try evaluating both children first
                    if len(node.children) == 2:
                        left_val = ctx.eval(node.children[0])
                        right_val = ctx.eval(node.children[1])
                        # Convert to AdeValues if python primitives
                        from ade.runtime.value import AdeNumber, AdeString, AdeBool, AdeNull
                        def _to_ade(v: Any) -> AdeValue:
                            if isinstance(v, AdeValue):
                                return v
                            if isinstance(v, (int, float)):
                                return AdeNumber(v)
                            if isinstance(v, str):
                                return AdeString(v)
                            if isinstance(v, bool):
                                return AdeBool(v)
                            if v is None:
                                return AdeNull()
                            return AdeString(str(v))
                        
                        args = [_to_ade(left_val), _to_ade(right_val)]
                        res = interp.call_function(handler, args, None)
                        return res.to_python() if hasattr(res, "to_python") else res
                    else:
                        # Pass node value or first child
                        val = node.value if node.value is not None else (ctx.eval(node.children[0]) if node.children else None)
                        from ade.runtime.value import AdeNumber, AdeString, AdeBool, AdeNull
                        def _to_ade(v: Any) -> AdeValue:
                            if isinstance(v, AdeValue):
                                return v
                            if isinstance(v, (int, float)):
                                return AdeNumber(v)
                            if isinstance(v, str):
                                return AdeString(v)
                            if isinstance(v, bool):
                                return AdeBool(v)
                            if v is None:
                                return AdeNull()
                            return AdeString(str(v))
                        args = [_to_ade(val)]
                        res = interp.call_function(handler, args, None)
                        return res.to_python() if hasattr(res, "to_python") else res

                # Normal Python callable inspection
                try:
                    sig = inspect.signature(handler)
                    param_count = len(sig.parameters)
                except (ValueError, TypeError):
                    param_count = 2

                if param_count == 1:
                    return handler(node)
                elif param_count == 2:
                    return handler(node, ctx)
                else:
                    return handler(node, ctx)

            return handler(node, ctx)

        except DSLEvaluationError:
            raise
        except Exception as e:
            diag = Diagnostic(
                severity=Severity.ERROR,
                title="DSL Runtime Error",
                message=f"Error evaluating '{node.type}': {str(e)}",
                span=node.span,
                source_code=ctx.source_code,
                hint="An unhandled exception occurred in custom DSL evaluator.",
                suggested_fix="Review the evaluator handler logic for this node type.",
            )
            raise DSLEvaluationError(diag) from e
