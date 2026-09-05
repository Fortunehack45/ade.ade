"""Standard JSON library for Ade."""

import json
from typing import Any, Dict, List
from ade.diagnostics.span import SourceSpan
from ade.runtime.value import (
    AdeValue,
    AdeNumber,
    AdeString,
    AdeBool,
    AdeNull,
    AdeList,
    AdeMap,
    AdeModule,
    AdeBuiltinFunction,
)
from ade.interpreter.errors import AdeRuntimeError


def _python_to_ade(val: Any) -> AdeValue:
    if val is None:
        return AdeNull.INSTANCE
    if isinstance(val, bool):
        return AdeBool.TRUE if val else AdeBool.FALSE
    if isinstance(val, (int, float)):
        return AdeNumber(val)
    if isinstance(val, str):
        return AdeString(val)
    if isinstance(val, list):
        return AdeList([_python_to_ade(item) for item in val])
    if isinstance(val, dict):
        return AdeMap({str(k): _python_to_ade(v) for k, v in val.items()})
    return AdeString(str(val))


def _ade_to_python(val: AdeValue) -> Any:
    if isinstance(val, AdeNull):
        return None
    if isinstance(val, AdeBool):
        return val.value
    if isinstance(val, AdeNumber):
        return val.value
    if isinstance(val, AdeString):
        return val.value
    if isinstance(val, AdeList):
        return [_ade_to_python(e) for e in val.elements]
    if isinstance(val, AdeMap):
        return {k: _ade_to_python(v) for k, v in val.entries.items()}
    return val.to_string()


def create_json_module() -> AdeModule:
    """Construct and return the standard json AdeModule."""
    exports: Dict[str, AdeValue] = {}

    def _parse(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        if not isinstance(args[0], AdeString):
            raise AdeRuntimeError(
                f"json.parse() expects string argument, got '{args[0].type_name()}'.",
                span=span,
            )
        try:
            parsed = json.loads(args[0].value)
            return _python_to_ade(parsed)
        except Exception as e:
            raise AdeRuntimeError(f"json.parse() error: {e}", span=span)

    def _stringify(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        py_val = _ade_to_python(args[0])
        try:
            s = json.dumps(py_val)
            return AdeString(s)
        except Exception as e:
            raise AdeRuntimeError(f"json.stringify() error: {e}", span=span)

    exports["parse"] = AdeBuiltinFunction("json.parse", 1, _parse)
    exports["stringify"] = AdeBuiltinFunction("json.stringify", 1, _stringify)

    return AdeModule(name="json", exports=exports)
