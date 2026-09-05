"""Standard math library for Ade."""

import math
from typing import Dict, List
from ade.diagnostics.span import SourceSpan
from ade.runtime.value import (
    AdeValue,
    AdeNumber,
    AdeModule,
    AdeBuiltinFunction,
)
from ade.interpreter.errors import AdeRuntimeError


def create_math_module() -> AdeModule:
    """Construct and return the standard math AdeModule."""
    exports: Dict[str, AdeValue] = {
        "pi": AdeNumber(math.pi),
        "e": AdeNumber(math.e),
    }

    def _unary(name: str, fn):
        def _fn(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
            if not isinstance(args[0], AdeNumber):
                raise AdeRuntimeError(
                    f"math.{name}() expects a number argument, got '{args[0].type_name()}'.",
                    span=span,
                )
            try:
                res = fn(args[0].value)
                if isinstance(res, float) and res.is_integer():
                    res = int(res)
                return AdeNumber(res)
            except ValueError as e:
                raise AdeRuntimeError(f"math.{name}() error: {e}", span=span)
        return AdeBuiltinFunction(f"math.{name}", 1, _fn)

    def _binary(name: str, fn):
        def _fn(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
            if not isinstance(args[0], AdeNumber) or not isinstance(args[1], AdeNumber):
                raise AdeRuntimeError(
                    f"math.{name}() expects two number arguments.",
                    span=span,
                )
            res = fn(args[0].value, args[1].value)
            if isinstance(res, float) and res.is_integer():
                res = int(res)
            return AdeNumber(res)
        return AdeBuiltinFunction(f"math.{name}", 2, _fn)

    exports["sqrt"] = _unary("sqrt", math.sqrt)
    exports["sin"] = _unary("sin", math.sin)
    exports["cos"] = _unary("cos", math.cos)
    exports["tan"] = _unary("tan", math.tan)
    exports["abs"] = _unary("abs", abs)
    exports["floor"] = _unary("floor", math.floor)
    exports["ceil"] = _unary("ceil", math.ceil)
    exports["round"] = _unary("round", round)
    exports["min"] = _binary("min", min)
    exports["max"] = _binary("max", max)
    exports["pow"] = _binary("pow", pow)

    return AdeModule(name="math", exports=exports)
