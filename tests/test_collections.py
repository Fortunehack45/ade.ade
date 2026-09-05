"""Automated tests for Ade collections (Lists and Maps)."""

import io
import pytest
from ade.lexer.lexer import Lexer
from ade.parser.parser import Parser
from ade.interpreter.interpreter import Interpreter
from ade.interpreter.errors import AdeRuntimeError


def run_code(source: str) -> str:
    out = io.StringIO()
    tokens = Lexer(source).tokenize()
    program = Parser(tokens, source_code=source).parse()
    interpreter = Interpreter(output_stream=out, source_code=source)
    interpreter.interpret(program)
    return out.getvalue().strip()


def test_list_operations():
    source = """
    nums = [10, 20, 30]
    say len(nums)
    say nums[0]
    say nums[2]
    nums[1] = 99
    say nums[1]
    """
    assert run_code(source).splitlines() == ["3", "10", "30", "99"]


def test_map_operations():
    source = """
    user = {
        name: "Fortune",
        role: "Engineer",
        score: 100
    }
    say user.name
    say user["role"]
    user.score = 150
    say user.score
    user["city"] = "Lagos"
    say user.city
    """
    assert run_code(source).splitlines() == ["Fortune", "Engineer", "150", "Lagos"]


def test_nested_collections():
    source = """
    data = {
        users: [
            { name: "Alice", age: 25 },
            { name: "Bob", age: 30 }
        ]
    }
    say data.users[0].name
    say data.users[1].age
    """
    assert run_code(source).splitlines() == ["Alice", "30"]


def test_list_index_out_of_range():
    source = """
    items = [1, 2]
    say items[5]
    """
    with pytest.raises(AdeRuntimeError) as exc_info:
        run_code(source)
    assert "List index out of range" in exc_info.value.message
