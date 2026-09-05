"""Standard I/O stream library (io) for Ade."""

import sys
from typing import Dict, List
from ade.diagnostics.span import SourceSpan
from ade.runtime.value import (
    AdeValue,
    AdeString,
    AdeNull,
    AdeModule,
    AdeBuiltinFunction,
)
from ade.interpreter.errors import AdeRuntimeError


def create_io_module() -> AdeModule:
    """Construct and return the standard io AdeModule."""
    exports: Dict[str, AdeValue] = {}

    def _read_line(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        prompt_str = ""
        if args and isinstance(args[0], AdeString):
            prompt_str = args[0].value
        try:
            val = input(prompt_str)
            return AdeString(val)
        except EOFError:
            return AdeString("")
        except Exception as e:
            raise AdeRuntimeError(f"io.read_line() error: {e}", span=span)

    def _print(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        out = interpreter.output_stream or sys.stdout
        msg = " ".join(arg.to_string() for arg in args)
        out.write(msg)
        if hasattr(out, "flush"):
            out.flush()
        return AdeNull()

    def _println(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        out = interpreter.output_stream or sys.stdout
        msg = " ".join(arg.to_string() for arg in args)
        out.write(msg + "\n")
        if hasattr(out, "flush"):
            out.flush()
        return AdeNull()

    def _eprintln(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        msg = " ".join(arg.to_string() for arg in args)
        sys.stderr.write(msg + "\n")
        sys.stderr.flush()
        return AdeNull()

    exports["read_line"] = AdeBuiltinFunction("io.read_line", 0, _read_line)
    exports["print"] = AdeBuiltinFunction("io.print", 1, _print)
    exports["println"] = AdeBuiltinFunction("io.println", 1, _println)
    exports["eprintln"] = AdeBuiltinFunction("io.eprintln", 1, _eprintln)

    return AdeModule("io", exports)
