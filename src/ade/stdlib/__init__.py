"""Ade Standard Library Registry."""

from typing import Dict, Optional
from ade.runtime.value import AdeModule
from ade.stdlib.math_module import create_math_module
from ade.stdlib.time_module import create_time_module
from ade.stdlib.json_module import create_json_module
from ade.stdlib.fs_module import create_fs_module
from ade.stdlib.os_module import create_os_module
from ade.stdlib.io_module import create_io_module
from ade.stdlib.language_module import create_language_module

_STDLIB_MODULES: Dict[str, AdeModule] = {}


def get_stdlib_module(name: str) -> Optional[AdeModule]:
    """Retrieve or initialize a built-in Ade standard library module."""
    if name in _STDLIB_MODULES:
        return _STDLIB_MODULES[name]

    if name == "math":
        mod = create_math_module()
        _STDLIB_MODULES[name] = mod
        return mod

    if name == "time":
        mod = create_time_module()
        _STDLIB_MODULES[name] = mod
        return mod

    if name == "json":
        mod = create_json_module()
        _STDLIB_MODULES[name] = mod
        return mod

    if name == "fs":
        mod = create_fs_module()
        _STDLIB_MODULES[name] = mod
        return mod

    if name == "os":
        mod = create_os_module()
        _STDLIB_MODULES[name] = mod
        return mod

    if name == "io":
        mod = create_io_module()
        _STDLIB_MODULES[name] = mod
        return mod

    if name == "language":
        mod = create_language_module()
        _STDLIB_MODULES[name] = mod
        return mod

    return None
