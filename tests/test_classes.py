"""Automated tests for Object-Oriented Programming (Classes, Methods, Instances)."""

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


def test_basic_class_and_method():
    source = """
    class User {
        name
        age

        function greet() {
            say "Hello, I am {self.name}"
        }
    }

    u = User("Fortune", 19)
    u.greet()
    """
    assert run_code(source) == "Hello, I am Fortune"


def test_class_named_arguments():
    source = """
    class User {
        name
        age

        function info() {
            return "{self.name} is {self.age} years old"
        }
    }

    user = User(
        name: "Fortune",
        age: 19
    )

    say user.info()
    """
    assert run_code(source) == "Fortune is 19 years old"


def test_class_attribute_mutation():
    source = """
    class Counter {
        count

        function increment() {
            self.count = self.count + 1
        }
    }

    c = Counter(0)
    c.increment()
    c.increment()
    say c.count
    """
    assert run_code(source) == "2"


def test_class_with_multiple_methods():
    source = """
    class Calculator {
        value

        function add(n) {
            self.value = self.value + n
            return self
        }

        function multiply(n) {
            self.value = self.value * n
            return self
        }
    }

    calc = Calculator(10)
    calc.add(5)
    calc.multiply(2)
    say calc.value
    """
    assert run_code(source) == "30"
