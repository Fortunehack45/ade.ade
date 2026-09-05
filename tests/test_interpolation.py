"""Automated tests for string interpolation in Ade."""

import io
from ade.lexer.lexer import Lexer
from ade.parser.parser import Parser
from ade.interpreter.interpreter import Interpreter


def run_code(source: str) -> str:
    out = io.StringIO()
    tokens = Lexer(source).tokenize()
    program = Parser(tokens, source_code=source).parse()
    interpreter = Interpreter(output_stream=out, source_code=source)
    interpreter.interpret(program)
    return out.getvalue().strip()


def test_simple_string_interpolation():
    source = """
    name = "Fortune"
    say "Hello {name}"
    """
    assert run_code(source) == "Hello Fortune"


def test_expression_string_interpolation():
    source = """
    a = 10
    b = 20
    say "Result: {a + b}"
    """
    assert run_code(source) == "Result: 30"


def test_multiple_interpolations():
    source = """
    first = "Ade"
    second = "Language"
    say "{first} is a {second}!"
    """
    assert run_code(source) == "Ade is a Language!"


def test_member_access_interpolation():
    source = """
    user = { name: "Fortune", level: 99 }
    say "User {user.name} is level {user.level}"
    """
    assert run_code(source) == "User Fortune is level 99"
