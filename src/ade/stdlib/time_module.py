"""Standard time library for Ade."""

import time
from typing import Dict, List
from ade.diagnostics.span import SourceSpan
from ade.runtime.value import (
    AdeValue,
    AdeNumber,
    AdeNull,
    AdeModule,
    AdeBuiltinFunction,
)
from ade.interpreter.errors import AdeRuntimeError


def create_time_module() -> AdeModule:
    """Construct and return the standard time AdeModule."""
    exports: Dict[str, AdeValue] = {}

    def _now(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        return AdeNumber(time.time())

    def _timestamp(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        return AdeNumber(int(time.time()))

    def _sleep(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        if not isinstance(args[0], AdeNumber):
            raise AdeRuntimeError(
                f"time.sleep() expects number seconds, got '{args[0].type_name()}'.",
                span=span,
            )
        time.sleep(args[0].value)
        return AdeNull.INSTANCE

    exports["now"] = AdeBuiltinFunction("time.now", 0, _now)
    exports["timestamp"] = AdeBuiltinFunction("time.timestamp", 0, _timestamp)
    exports["sleep"] = AdeBuiltinFunction("time.sleep", 1, _sleep)

    return AdeModule(name="time", exports=exports)
