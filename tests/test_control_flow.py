"""Automated tests for Ade control flow (if/else, while, for, break, continue)."""

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


def test_if_else():
    source = """
    x = 15
    if x > 20 {
        say "greater"
    } else if x == 15 {
        say "equal"
    } else {
        say "smaller"
    }
    """
    assert run_code(source) == "equal"


def test_while_loop():
    source = """
    i = 0
    total = 0
    while i < 4 {
        total = total + i
        i = i + 1
    }
    say total
    """
    assert run_code(source) == "6"


def test_for_loop_list():
    source = """
    items = [1, 2, 3, 4]
    sum = 0
    for x in items {
        sum = sum + x
    }
    say sum
    """
    assert run_code(source) == "10"


def test_for_loop_string():
    source = """
    chars = ""
    for ch in "ade" {
        chars = chars + ch + "-"
    }
    say chars
    """
    assert run_code(source) == "a-d-e-"


def test_break_and_continue():
    source = """
    total = 0
    for x in [1, 2, 3, 4, 5, 6] {
        if x == 2 {
            continue
        }
        if x == 5 {
            break
        }
        total = total + x
    }
    say total
    """
    # Sums: 1 + 3 + 4 = 8
    assert run_code(source) == "8"
