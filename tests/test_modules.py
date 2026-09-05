"""Automated tests for Ade Module System and Standard Library."""

import io
import os
import tempfile
from ade.lexer.lexer import Lexer
from ade.parser.parser import Parser
from ade.interpreter.interpreter import Interpreter


def run_code(source: str, file_path: str = "<stdin>") -> str:
    out = io.StringIO()
    tokens = Lexer(source, file_path=file_path).tokenize()
    program = Parser(tokens, source_code=source).parse()
    interpreter = Interpreter(output_stream=out, source_code=source, current_file_path=file_path)
    interpreter.interpret(program)
    return out.getvalue().strip()


def test_import_math():
    source = """
    import math

    say math.sqrt(16)
    say math.min(10, 5)
    say math.max(10, 5)
    say math.pow(2, 4)
    """
    assert run_code(source).splitlines() == ["4", "5", "10", "16"]


def test_from_math_import():
    source = """
    from math import sqrt, pi

    say sqrt(25)
    say pi > 3
    """
    assert run_code(source).splitlines() == ["5", "true"]


def test_import_time():
    source = """
    import time

    t = time.now()
    say t > 0
    """
    assert run_code(source) == "true"


def test_import_json():
    source = """
    import json

    data = { name: "Fortune", level: 5 }
    encoded = json.stringify(data)
    decoded = json.parse(encoded)

    say decoded.name
    say decoded.level
    """
    assert run_code(source).splitlines() == ["Fortune", "5"]


def test_project_local_module_import():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create helper module: utils.ade
        utils_path = os.path.join(tmpdir, "utils.ade")
        with open(utils_path, "w", encoding="utf-8") as f:
            f.write("""
function greet(name) {
    return "Welcome, " + name
}
version = "1.0"
""")

        # Create main script: main.ade
        main_path = os.path.join(tmpdir, "main.ade")
        source = """
import utils
from utils import version

say utils.greet("Fortune")
say "Version: " + version
"""
        with open(main_path, "w", encoding="utf-8") as f:
            f.write(source)

        output = run_code(source, file_path=main_path)
        assert output.splitlines() == ["Welcome, Fortune", "Version: 1.0"]
