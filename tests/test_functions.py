"""Automated tests for Ade functions, closures, recursion, and higher-order functions."""

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


def test_basic_function():
    source = """
    function add(a, b) {
        return a + b
    }
    say add(10, 25)
    """
    assert run_code(source) == "35"


def test_early_return():
    source = """
    function check(val) {
        if val < 0 {
            return "negative"
        }
        return "positive"
    }
    say check(-5)
    say check(5)
    """
    assert run_code(source).splitlines() == ["negative", "positive"]


def test_closures():
    source = """
    function make_counter() {
        count = 0
        return function() {
            count = count + 1
            return count
        }
    }

    c = make_counter()
    say c()
    say c()
    say c()
    """
    assert run_code(source).splitlines() == ["1", "2", "3"]


def test_recursion():
    source = """
    function fib(n) {
        if n <= 1 {
            return n
        }
        return fib(n - 1) + fib(n - 2)
    }
    say fib(7)
    """
    assert run_code(source) == "13"


def test_milestone_program():
    """Exact program from Section 46 of the specification."""
    source = """
    name = "Fortune"
    numbers = [1, 2, 3, 4, 5]

    function total(items) {
        result = 0

        for item in items {
            result = result + item
        }

        return result
    }

    say "Hello, " + name
    say total(numbers)
    """
    output = run_code(source).splitlines()
    assert output == ["Hello, Fortune", "15"]
