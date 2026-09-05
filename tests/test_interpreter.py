"""Automated tests for Ade Interpreter and basic evaluations."""

import io
import pytest
from ade.lexer.lexer import Lexer
from ade.parser.parser import Parser
from ade.interpreter.interpreter import Interpreter
from ade.interpreter.errors import AdeRuntimeError


def run_code(source: str) -> str:
    """Run Ade source code and return captured stdout string."""
    out = io.StringIO()
    tokens = Lexer(source).tokenize()
    program = Parser(tokens, source_code=source).parse()
    interpreter = Interpreter(output_stream=out, source_code=source)
    interpreter.interpret(program)
    return out.getvalue().strip()


def test_say_hello():
    output = run_code('say "Hello, World!"')
    assert output == "Hello, World!"


def test_variables_and_arithmetic():
    source = """
    a = 10
    b = 20
    c = a + b
    say c
    """
    output = run_code(source)
    assert output == "30"


def test_string_concatenation():
    source = """
    name = "Fortune"
    say "Hello, " + name
    """
    output = run_code(source)
    assert output == "Hello, Fortune"


def test_arithmetic_operations():
    source = """
    say 10 + 5
    say 10 - 4
    say 6 * 7
    say 20 / 4
    say 17 % 5
    """
    output = run_code(source).splitlines()
    assert output == ["15", "6", "42", "5", "2"]


def test_comparisons():
    source = """
    say 10 > 5
    say 5 <= 5
    say 10 == 10
    say 10 != 5
    say not false
    """
    output = run_code(source).splitlines()
    assert output == ["true", "true", "true", "true", "true"]


def test_undefined_variable():
    source = "say undefined_var"
    with pytest.raises(AdeRuntimeError) as exc_info:
        run_code(source)
    assert "Undefined variable 'undefined_var'" in exc_info.value.message


def test_division_by_zero():
    source = "say 10 / 0"
    with pytest.raises(AdeRuntimeError) as exc_info:
        run_code(source)
    assert "Division by zero" in exc_info.value.message
