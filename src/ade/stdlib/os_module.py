"""Standard operating system library (os) for Ade."""

import os
import sys
import platform as sys_platform
from typing import Dict, List
from ade.diagnostics.span import SourceSpan
from ade.runtime.value import (
    AdeValue,
    AdeString,
    AdeNull,
    AdeList,
    AdeNumber,
    AdeModule,
    AdeBuiltinFunction,
)
from ade.interpreter.errors import AdeRuntimeError


def create_os_module() -> AdeModule:
    """Construct and return the standard os AdeModule."""
    exports: Dict[str, AdeValue] = {}

    def _get_env(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        if not isinstance(args[0], AdeString):
            raise AdeRuntimeError(
                f"os.get_env() expects variable name string, got '{args[0].type_name()}'.",
                span=span,
            )
        var_name = args[0].value
        default_val = args[1].value if len(args) > 1 and isinstance(args[1], AdeString) else ""
        return AdeString(os.environ.get(var_name, default_val))

    def _set_env(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        if not isinstance(args[0], AdeString) or not isinstance(args[1], AdeString):
            raise AdeRuntimeError(
                "os.set_env() expects key and value strings.",
                span=span,
            )
        os.environ[args[0].value] = args[1].value
        return AdeNull()

    def _platform(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        system = sys_platform.system().lower()
        if system.startswith("win"):
            return AdeString("windows")
        elif system.startswith("darwin"):
            return AdeString("macos")
        return AdeString("linux")

    def _cwd(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        return AdeString(os.getcwd())

    def _exit(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        code = 0
        if args and isinstance(args[0], AdeNumber):
            code = int(args[0].value)
        sys.exit(code)

    def _args(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        return AdeList([AdeString(arg) for arg in sys.argv])

    exports["get_env"] = AdeBuiltinFunction("os.get_env", 1, _get_env, min_args=1, max_args=2)
    exports["set_env"] = AdeBuiltinFunction("os.set_env", 2, _set_env)
    exports["platform"] = AdeBuiltinFunction("os.platform", 0, _platform)
    exports["cwd"] = AdeBuiltinFunction("os.cwd", 0, _cwd)
    exports["exit"] = AdeBuiltinFunction("os.exit", 0, _exit, min_args=0, max_args=1)
    exports["args"] = AdeBuiltinFunction("os.args", 0, _args)

    return AdeModule("os", exports)
