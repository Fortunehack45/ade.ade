"""Automated tests for Ade's Gradual & Static Type System and 'ade check' command."""

import io
from contextlib import redirect_stdout, redirect_stderr
from ade.lexer.lexer import Lexer
from ade.parser.parser import Parser
from ade.semantic.checker import TypeChecker
from ade.diagnostics.diagnostic import DiagnosticSeverity
from ade.cli.main import main


def check_source(source: str):
    lexer = Lexer(source=source)
    tokens = lexer.tokenize()
    parser = Parser(tokens=tokens, source_code=source)
    program = parser.parse()
    checker = TypeChecker(source_code=source)
    return checker.check(program)


def test_valid_typed_variables():
    source = """
    name: text = "Fortune"
    age: number = 19
    is_active: bool = true
    empty: null = null
    """
    diags = check_source(source)
    errors = [d for d in diags if d.severity == DiagnosticSeverity.ERROR]
    assert len(errors) == 0


def test_invalid_typed_variable_mismatch():
    source = """
    age: number = "nineteen"
    """
    diags = check_source(source)
    errors = [d for d in diags if d.severity == DiagnosticSeverity.ERROR]
    assert len(errors) == 1
    assert "Type mismatch" in errors[0].message
    assert "number" in errors[0].message
    assert "text" in errors[0].message


def test_valid_function_signature_and_call():
    source = """
    function add(a: number, b: number) -> number {
        return a + b
    }
    result: number = add(10, 20)
    """
    diags = check_source(source)
    errors = [d for d in diags if d.severity == DiagnosticSeverity.ERROR]
    assert len(errors) == 0


def test_invalid_function_return_type():
    source = """
    function get_greeting() -> text {
        return 42
    }
    """
    diags = check_source(source)
    errors = [d for d in diags if d.severity == DiagnosticSeverity.ERROR]
    assert len(errors) == 1
    assert "Return type mismatch" in errors[0].message
    assert "text" in errors[0].message
    assert "number" in errors[0].message


def test_invalid_function_argument_type():
    source = """
    function multiply(x: number, y: number) -> number {
        return x * y
    }
    multiply(5, "not_a_number")
    """
    diags = check_source(source)
    errors = [d for d in diags if d.severity == DiagnosticSeverity.ERROR]
    assert len(errors) == 1
    assert "Argument type mismatch" in errors[0].message
    assert "parameter 'y'" in errors[0].message


def test_function_argument_count_mismatch():
    source = """
    function greet(name: text) -> text {
        return "Hello " + name
    }
    greet("Fortune", 123)
    """
    diags = check_source(source)
    errors = [d for d in diags if d.severity == DiagnosticSeverity.ERROR]
    assert len(errors) == 1
    assert "expected 1 arguments, but got 2" in errors[0].message.lower()


def test_nullable_types():
    # Nullable accepts null and inner type
    source_valid = """
    bio: text? = null
    bio2: text? = "Engineer"
    """
    diags = check_source(source_valid)
    assert len([d for d in diags if d.severity == DiagnosticSeverity.ERROR]) == 0

    source_invalid = """
    bio: text? = 123
    """
    diags_invalid = check_source(source_invalid)
    errors = [d for d in diags_invalid if d.severity == DiagnosticSeverity.ERROR]
    assert len(errors) == 1
    assert "Type mismatch" in errors[0].message


def test_generic_list_type():
    source = """
    scores: list<number> = [95, 88, 100]
    """
    diags = check_source(source)
    assert len([d for d in diags if d.severity == DiagnosticSeverity.ERROR]) == 0


def test_union_types():
    source = """
    id: number | text = 42
    id2: number | text = "ADE-42"
    """
    diags = check_source(source)
    assert len([d for d in diags if d.severity == DiagnosticSeverity.ERROR]) == 0


def test_undefined_variable_diagnostic():
    source = """
    say unknown_variable
    """
    diags = check_source(source)
    errors = [d for d in diags if d.severity == DiagnosticSeverity.ERROR]
    assert len(errors) == 1
    assert "Undefined variable 'unknown_variable'" in errors[0].message


def test_cli_ade_check(tmp_path):
    # Valid file
    valid_file = tmp_path / "valid.ade"
    valid_file.write_text("""
    function square(n: number) -> number {
        return n * n
    }
    val: number = square(5)
    say "Result: {val}"
    """, encoding="utf-8")

    out = io.StringIO()
    with redirect_stdout(out):
        ret = main(["check", str(valid_file)])
    assert ret == 0
    assert "All type checks passed" in out.getvalue()

    # Invalid file
    invalid_file = tmp_path / "invalid.ade"
    invalid_file.write_text("""
    x: number = "mismatched"
    """, encoding="utf-8")

    err = io.StringIO()
    with redirect_stderr(err):
        ret = main(["check", str(invalid_file)])
    assert ret == 1
    assert "Type mismatch" in err.getvalue()
