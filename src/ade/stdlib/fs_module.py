"""Standard filesystem library (fs) for Ade."""

import os
from typing import Dict, List
from ade.diagnostics.span import SourceSpan
from ade.runtime.value import (
    AdeValue,
    AdeString,
    AdeBool,
    AdeNull,
    AdeList,
    AdeModule,
    AdeBuiltinFunction,
)
from ade.interpreter.errors import AdeRuntimeError


def create_fs_module() -> AdeModule:
    """Construct and return the standard fs AdeModule."""
    exports: Dict[str, AdeValue] = {}

    def _read_text(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        if not isinstance(args[0], AdeString):
            raise AdeRuntimeError(
                f"fs.read_text() expects a string path, got '{args[0].type_name()}'.",
                span=span,
            )
        path = args[0].value
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            return AdeString(content)
        except FileNotFoundError:
            raise AdeRuntimeError(f"fs.read_text(): file '{path}' does not exist.", span=span)
        except PermissionError:
            raise AdeRuntimeError(f"fs.read_text(): permission denied accessing '{path}'.", span=span)
        except Exception as e:
            raise AdeRuntimeError(f"fs.read_text() error: {e}", span=span)

    def _write_text(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        if not isinstance(args[0], AdeString) or not isinstance(args[1], AdeString):
            raise AdeRuntimeError(
                "fs.write_text() expects path and content strings.",
                span=span,
            )
        path = args[0].value
        content = args[1].value
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return AdeNull()
        except PermissionError:
            raise AdeRuntimeError(f"fs.write_text(): permission denied writing to '{path}'.", span=span)
        except Exception as e:
            raise AdeRuntimeError(f"fs.write_text() error: {e}", span=span)

    def _append_text(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        if not isinstance(args[0], AdeString) or not isinstance(args[1], AdeString):
            raise AdeRuntimeError(
                "fs.append_text() expects path and content strings.",
                span=span,
            )
        path = args[0].value
        content = args[1].value
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(content)
            return AdeNull()
        except PermissionError:
            raise AdeRuntimeError(f"fs.append_text(): permission denied writing to '{path}'.", span=span)
        except Exception as e:
            raise AdeRuntimeError(f"fs.append_text() error: {e}", span=span)

    def _exists(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        if not isinstance(args[0], AdeString):
            raise AdeRuntimeError(
                f"fs.exists() expects a string path, got '{args[0].type_name()}'.",
                span=span,
            )
        return AdeBool(os.path.exists(args[0].value))

    def _is_file(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        if not isinstance(args[0], AdeString):
            raise AdeRuntimeError(
                f"fs.is_file() expects a string path, got '{args[0].type_name()}'.",
                span=span,
            )
        return AdeBool(os.path.isfile(args[0].value))

    def _is_dir(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        if not isinstance(args[0], AdeString):
            raise AdeRuntimeError(
                f"fs.is_dir() expects a string path, got '{args[0].type_name()}'.",
                span=span,
            )
        return AdeBool(os.path.isdir(args[0].value))

    def _list_dir(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        path = "."
        if args and isinstance(args[0], AdeString):
            path = args[0].value
        elif args:
            raise AdeRuntimeError(
                f"fs.list_dir() expects an optional string path, got '{args[0].type_name()}'.",
                span=span,
            )
        try:
            entries = os.listdir(path)
            return AdeList([AdeString(entry) for entry in entries])
        except FileNotFoundError:
            raise AdeRuntimeError(f"fs.list_dir(): directory '{path}' does not exist.", span=span)
        except Exception as e:
            raise AdeRuntimeError(f"fs.list_dir() error: {e}", span=span)

    def _remove(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        if not isinstance(args[0], AdeString):
            raise AdeRuntimeError(
                f"fs.remove() expects a string path, got '{args[0].type_name()}'.",
                span=span,
            )
        path = args[0].value
        for attempt in range(5):
            try:
                if os.path.isdir(path):
                    os.rmdir(path)
                else:
                    os.remove(path)
                return AdeBool(True)
            except PermissionError:
                if attempt < 4:
                    import time
                    time.sleep(0.05)
                    continue
                raise AdeRuntimeError(f"fs.remove(): permission denied removing '{path}'.", span=span)
            except Exception as e:
                raise AdeRuntimeError(f"fs.remove() error: {e}", span=span)

    def _mkdir(interpreter, args: List[AdeValue], span: SourceSpan) -> AdeValue:
        if not isinstance(args[0], AdeString):
            raise AdeRuntimeError(
                f"fs.mkdir() expects a string path, got '{args[0].type_name()}'.",
                span=span,
            )
        path = args[0].value
        try:
            os.makedirs(path, exist_ok=True)
            return AdeBool(True)
        except Exception as e:
            raise AdeRuntimeError(f"fs.mkdir() error: {e}", span=span)

    exports["read_text"] = AdeBuiltinFunction("fs.read_text", 1, _read_text)
    exports["write_text"] = AdeBuiltinFunction("fs.write_text", 2, _write_text)
    exports["append_text"] = AdeBuiltinFunction("fs.append_text", 2, _append_text)
    exports["exists"] = AdeBuiltinFunction("fs.exists", 1, _exists)
    exports["is_file"] = AdeBuiltinFunction("fs.is_file", 1, _is_file)
    exports["is_dir"] = AdeBuiltinFunction("fs.is_dir", 1, _is_dir)
    exports["list_dir"] = AdeBuiltinFunction("fs.list_dir", 0, _list_dir, min_args=0, max_args=1)
    exports["remove"] = AdeBuiltinFunction("fs.remove", 1, _remove)
    exports["mkdir"] = AdeBuiltinFunction("fs.mkdir", 1, _mkdir)

    return AdeModule("fs", exports)
