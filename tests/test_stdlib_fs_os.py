"""Automated tests for Ade's standard library modules: fs, os, and io."""

import io
import os
from contextlib import redirect_stdout
from ade.interpreter.interpreter import Interpreter
from ade.lexer.lexer import Lexer
from ade.parser.parser import Parser
from ade.semantic.checker import TypeChecker
from ade.diagnostics.diagnostic import DiagnosticSeverity


def run_source(source: str, file_path: str = "<stdin>") -> str:
    lexer = Lexer(source=source, file_path=file_path)
    tokens = lexer.tokenize()
    parser = Parser(tokens=tokens, source_code=source)
    program = parser.parse()
    out = io.StringIO()
    interpreter = Interpreter(source_code=source, current_file_path=file_path, output_stream=out)
    interpreter.interpret(program)
    return out.getvalue().strip()


def check_source(source: str):
    lexer = Lexer(source=source)
    tokens = lexer.tokenize()
    parser = Parser(tokens=tokens, source_code=source)
    program = parser.parse()
    checker = TypeChecker(source_code=source)
    return checker.check(program)


def test_fs_write_read_append(tmp_path):
    test_file = str(tmp_path / "hello.txt").replace("\\", "/")
    source = f"""
    import fs

    fs.write_text("{test_file}", "Hello from Ade!")
    content = fs.read_text("{test_file}")
    say content

    fs.append_text("{test_file}", " More text.")
    content2 = fs.read_text("{test_file}")
    say content2
    """
    output = run_source(source)
    lines = output.splitlines()
    assert lines[0] == "Hello from Ade!"
    assert lines[1] == "Hello from Ade! More text."


def test_fs_exists_and_file_checks(tmp_path):
    test_file = str(tmp_path / "check.txt").replace("\\", "/")
    nonexistent = str(tmp_path / "missing.txt").replace("\\", "/")
    source = f"""
    import fs

    say fs.exists("{nonexistent}")
    fs.write_text("{test_file}", "exists")
    say fs.exists("{test_file}")
    say fs.is_file("{test_file}")
    say fs.is_dir("{test_file}")
    """
    output = run_source(source)
    lines = output.splitlines()
    assert lines[0] == "false"
    assert lines[1] == "true"
    assert lines[2] == "true"
    assert lines[3] == "false"


def test_fs_mkdir_list_remove(tmp_path):
    test_dir = str(tmp_path / "my_dir").replace("\\", "/")
    test_file = str(tmp_path / "my_dir" / "file.txt").replace("\\", "/")
    source = f"""
    import fs

    fs.mkdir("{test_dir}")
    say fs.is_dir("{test_dir}")

    fs.write_text("{test_file}", "inside dir")
    entries = fs.list_dir("{test_dir}")
    say len(entries)
    say entries[0]

    fs.remove("{test_file}")
    say fs.exists("{test_file}")
    """
    output = run_source(source)
    lines = output.splitlines()
    assert lines[0] == "true"
    assert lines[1] == "1"
    assert lines[2] == "file.txt"
    assert lines[3] == "false"


def test_os_platform_and_cwd():
    source = """
    import os

    plat = os.platform()
    cwd_path = os.cwd()
    say plat
    say len(cwd_path) > 0
    """
    output = run_source(source)
    lines = output.splitlines()
    assert lines[0] in ("windows", "linux", "macos")
    assert lines[1] == "true"


def test_os_env_variables():
    source = """
    import os

    os.set_env("ADE_TEST_VAR", "ade_val_42")
    val = os.get_env("ADE_TEST_VAR", "default")
    say val

    missing = os.get_env("ADE_MISSING_VAR_XYZ", "fallback")
    say missing
    """
    output = run_source(source)
    lines = output.splitlines()
    assert lines[0] == "ade_val_42"
    assert lines[1] == "fallback"


def test_io_print_and_println():
    source = """
    import io

    io.print("A")
    io.print("B")
    io.println("C")
    """
    output = run_source(source)
    assert output == "ABC"


def test_type_check_fs_and_os():
    source = """
    import fs
    import os

    p: text = os.platform()
    working_dir: text = os.cwd()
    is_present: bool = fs.exists("some_file.txt")
    """
    diags = check_source(source)
    errors = [d for d in diags if d.severity == DiagnosticSeverity.ERROR]
    assert len(errors) == 0
