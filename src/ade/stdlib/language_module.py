"""Standard Language-Building Platform library (language) for Ade.

Enables developers to define, parse, and execute custom domain-specific
languages (DSLs) natively within Ade scripts.
"""

from typing import Any, Dict, List, Optional
from ade.diagnostics.diagnostic import Diagnostic, Severity
from ade.diagnostics.reporter import DiagnosticReporter
from ade.diagnostics.span import SourceSpan
from ade.interpreter.errors import AdeRuntimeError
from ade.language.ast import DSLNode
from ade.language.engine import LanguageEngine
from ade.language.evaluator import DSLContext, DSLEvaluationError
from ade.language.parser import DSLParseError
from ade.language.tokens import DSLLexerError
from ade.runtime.value import (
    AdeBool,
    AdeBuiltinFunction,
    AdeCallable,
    AdeClass,
    AdeInstance,
    AdeList,
    AdeMap,
    AdeModule,
    AdeNull,
    AdeNumber,
    AdeString,
    AdeValue,
)


def _py_to_ade(val: Any) -> AdeValue:
    """Convert a Python value to its corresponding AdeValue representation."""
    if isinstance(val, AdeValue):
        return val
    if isinstance(val, bool):
        return AdeBool.TRUE if val else AdeBool.FALSE
    if isinstance(val, (int, float)):
        return AdeNumber(val)
    if isinstance(val, str):
        return AdeString(val)
    if val is None:
        return AdeNull.INSTANCE
    if isinstance(val, list):
        return AdeList([_py_to_ade(x) for x in val])
    if isinstance(val, dict):
        return AdeMap({str(k): _py_to_ade(v) for k, v in val.items()})
    if isinstance(val, DSLNode):
        return _dsl_node_to_ade(val)
    return AdeString(str(val))


def _ade_to_py(val: AdeValue) -> Any:
    """Convert an AdeValue to a standard Python value."""
    if isinstance(val, AdeNumber):
        return val.value
    if isinstance(val, AdeString):
        return val.value
    if isinstance(val, AdeBool):
        return val.value
    if isinstance(val, AdeNull):
        return None
    if isinstance(val, AdeList):
        return [_ade_to_py(x) for x in val.elements]
    if isinstance(val, AdeMap):
        return {k: _ade_to_py(v) for k, v in val.entries.items()}
    return val


_NODE_CLASS = AdeClass(name="DSLNode", fields=["type", "value", "children"])
_ENGINE_CLASS = AdeClass(name="LanguageEngine", fields=["name"])


def _dsl_node_to_ade(node: DSLNode) -> AdeInstance:
    """Wrap a DSLNode in an AdeInstance with convenient accessors."""
    inst = AdeInstance(_NODE_CLASS)
    inst.fields["type"] = AdeString(node.type)
    inst.fields["value"] = _py_to_ade(node.value)
    inst.fields["children"] = AdeList([_dsl_node_to_ade(c) for c in node.children])

    def _child(interp, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        if not isinstance(args[0], AdeNumber) or not isinstance(args[0].value, int):
            raise AdeRuntimeError("DSLNode.child() expects an integer index.", span=span)
        idx = args[0].value
        if idx < 0 or idx >= len(node.children):
            raise AdeRuntimeError(
                f"DSLNode.child() index {idx} out of range (length: {len(node.children)}).",
                span=span,
            )
        return _dsl_node_to_ade(node.children[idx])

    def _pretty(interp, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        return AdeString(node.pretty())

    inst.fields["child"] = AdeBuiltinFunction("child", 1, _child)
    inst.fields["pretty"] = AdeBuiltinFunction("pretty", 0, _pretty)
    return inst


def _wrap_language_engine(engine: LanguageEngine) -> AdeInstance:
    """Wrap a LanguageEngine in an AdeInstance with exposed configuration methods."""
    inst = AdeInstance(_ENGINE_CLASS)
    inst.fields["name"] = AdeString(engine.name)

    # 1. token(name, pattern, ignore = false)
    def _token(interp, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        if not isinstance(args[0], AdeString) or not isinstance(args[1], AdeString):
            raise AdeRuntimeError("engine.token() expects name and pattern strings.", span=span)
        name = args[0].value
        pat = args[1].value
        ignore = args[2].is_truthy() if len(args) > 2 else False
        try:
            engine.token(name, pat, ignore=ignore)
        except Exception as e:
            raise AdeRuntimeError(f"engine.token() invalid regex '{pat}': {e}", span=span)
        return inst

    # 2. ignore(pattern)
    def _ignore(interp, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        if not isinstance(args[0], AdeString):
            raise AdeRuntimeError("engine.ignore() expects pattern string.", span=span)
        pat = args[0].value
        try:
            engine.ignore(pat)
        except Exception as e:
            raise AdeRuntimeError(f"engine.ignore() invalid regex '{pat}': {e}", span=span)
        return inst

    # 3. literal(token_type, node_type = "")
    def _literal(interp, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        if not isinstance(args[0], AdeString):
            raise AdeRuntimeError("engine.literal() expects token_type string.", span=span)
        tt = args[0].value
        nt = args[1].value if len(args) > 1 and isinstance(args[1], AdeString) and args[1].value else None
        engine.literal(tt, nt)
        return inst

    # 4. prefix(token_type, precedence, node_type = "")
    def _prefix(interp, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        if not isinstance(args[0], AdeString) or not isinstance(args[1], AdeNumber):
            raise AdeRuntimeError("engine.prefix() expects token_type string and numeric precedence.", span=span)
        tt = args[0].value
        prec = int(args[1].value)
        nt = args[2].value if len(args) > 2 and isinstance(args[2], AdeString) and args[2].value else None
        engine.prefix(tt, prec, nt)
        return inst

    # 5. infix(token_type, precedence, node_type = "", associativity = "left")
    def _infix(interp, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        if not isinstance(args[0], AdeString) or not isinstance(args[1], AdeNumber):
            raise AdeRuntimeError("engine.infix() expects token_type string and numeric precedence.", span=span)
        tt = args[0].value
        prec = int(args[1].value)
        nt = args[2].value if len(args) > 2 and isinstance(args[2], AdeString) and args[2].value else None
        assoc = args[3].value if len(args) > 3 and isinstance(args[3], AdeString) else "left"
        engine.infix(tt, prec, nt, assoc)
        return inst

    # 6. group(open_token, close_token)
    def _group(interp, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        if not isinstance(args[0], AdeString) or not isinstance(args[1], AdeString):
            raise AdeRuntimeError("engine.group() expects open_token and close_token strings.", span=span)
        engine.group(args[0].value, args[1].value)
        return inst

    # 7. binary_op(token_type, precedence, node_type, handler_fn)
    def _binary_op(interp, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        if not isinstance(args[0], AdeString) or not isinstance(args[1], AdeNumber) or not isinstance(args[2], AdeString):
            raise AdeRuntimeError("engine.binary_op() expects (token_type, precedence, node_type, handler).", span=span)
        if not isinstance(args[3], AdeCallable):
            raise AdeRuntimeError("engine.binary_op() handler must be a callable function.", span=span)
        tt = args[0].value
        prec = int(args[1].value)
        nt = args[2].value
        handler = args[3]

        def _eval_binary(node: DSLNode, ctx: DSLContext) -> Any:
            left_val = _py_to_ade(ctx.eval(node.children[0]))
            right_val = _py_to_ade(ctx.eval(node.children[1]))
            res = handler.call(interp, [left_val, right_val], node.span or span)
            return _ade_to_py(res)

        engine.infix(tt, prec, nt)
        engine.evaluator(nt, _eval_binary)
        return inst

    # 8. prefix_op(token_type, precedence, node_type, handler_fn)
    def _prefix_op(interp, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        if not isinstance(args[0], AdeString) or not isinstance(args[1], AdeNumber) or not isinstance(args[2], AdeString):
            raise AdeRuntimeError("engine.prefix_op() expects (token_type, precedence, node_type, handler).", span=span)
        if not isinstance(args[3], AdeCallable):
            raise AdeRuntimeError("engine.prefix_op() handler must be a callable function.", span=span)
        tt = args[0].value
        prec = int(args[1].value)
        nt = args[2].value
        handler = args[3]

        def _eval_prefix(node: DSLNode, ctx: DSLContext) -> Any:
            operand_val = _py_to_ade(ctx.eval(node.children[0]))
            res = handler.call(interp, [operand_val], node.span or span)
            return _ade_to_py(res)

        engine.prefix(tt, prec, nt)
        engine.evaluator(nt, _eval_prefix)
        return inst

    # 9. evaluator(node_type, handler_fn)
    def _evaluator(interp, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        if not isinstance(args[0], AdeString) or not isinstance(args[1], AdeCallable):
            raise AdeRuntimeError("engine.evaluator() expects node_type string and callable handler.", span=span)
        nt = args[0].value
        handler = args[1]

        def _eval_custom(node: DSLNode, ctx: DSLContext) -> Any:
            wrapped_node = _dsl_node_to_ade(node)
            res = handler.call(interp, [wrapped_node], node.span or span)
            return _ade_to_py(res)

        engine.evaluator(nt, _eval_custom)
        return inst

    # 10. parse(source)
    def _parse(interp, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        if not isinstance(args[0], AdeString):
            raise AdeRuntimeError("engine.parse() expects a source string.", span=span)
        src = args[0].value
        try:
            ast = engine.parse(src)
            return _dsl_node_to_ade(ast)
        except (DSLLexerError, DSLParseError) as err:
            reporter = DiagnosticReporter()
            print(reporter.format_diagnostic(err.diagnostic))
            raise AdeRuntimeError(f"DSL Parse Failed: {err}", span=span)
        except Exception as e:
            raise AdeRuntimeError(f"DSL Parse Error: {e}", span=span)

    # 11. execute(source, variables = null)
    def _execute(interp, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        if not isinstance(args[0], AdeString):
            raise AdeRuntimeError("engine.execute() expects a source string.", span=span)
        src = args[0].value
        vars_dict: Dict[str, Any] = {}
        if len(args) > 1 and isinstance(args[1], AdeMap):
            vars_dict = {k: _ade_to_py(v) for k, v in args[1].entries.items()}

        try:
            result = engine.execute(src, variables=vars_dict)
            return _py_to_ade(result)
        except (DSLLexerError, DSLParseError, DSLEvaluationError) as err:
            reporter = DiagnosticReporter()
            print(reporter.format_diagnostic(err.diagnostic))
            raise AdeRuntimeError(f"DSL Execution Failed: {err}", span=span)
        except Exception as e:
            raise AdeRuntimeError(f"DSL Execution Error: {e}", span=span)

    inst.fields["token"] = AdeBuiltinFunction("token", 2, _token, min_args=2, max_args=3)
    inst.fields["ignore"] = AdeBuiltinFunction("ignore", 1, _ignore)
    inst.fields["literal"] = AdeBuiltinFunction("literal", 1, _literal, min_args=1, max_args=2)
    inst.fields["prefix"] = AdeBuiltinFunction("prefix", 2, _prefix, min_args=2, max_args=3)
    inst.fields["infix"] = AdeBuiltinFunction("infix", 2, _infix, min_args=2, max_args=4)
    inst.fields["group"] = AdeBuiltinFunction("group", 2, _group)
    inst.fields["binary_op"] = AdeBuiltinFunction("binary_op", 4, _binary_op)
    inst.fields["prefix_op"] = AdeBuiltinFunction("prefix_op", 4, _prefix_op)
    inst.fields["evaluator"] = AdeBuiltinFunction("evaluator", 2, _evaluator)
    inst.fields["parse"] = AdeBuiltinFunction("parse", 1, _parse)
    inst.fields["execute"] = AdeBuiltinFunction("execute", 1, _execute, min_args=1, max_args=2)

    return inst


def create_language_module() -> AdeModule:
    """Construct and return the standard language AdeModule."""
    exports: Dict[str, AdeValue] = {}

    def _create(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        name = args[0].value if args and isinstance(args[0], AdeString) else "CustomDSL"
        engine = LanguageEngine(name=name)
        return _wrap_language_engine(engine)

    exports["create"] = AdeBuiltinFunction("create", 1, _create, min_args=0, max_args=1)
    exports["engine"] = AdeBuiltinFunction("engine", 1, _create, min_args=0, max_args=1)

    return AdeModule("language", exports)
