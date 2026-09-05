"""Automated test suite for Ade Language-Building Platform (ade.language)."""

import pytest
from ade.language.engine import LanguageEngine
from ade.language.tokens import DSLLexerError
from ade.language.parser import DSLParseError
from ade.language.evaluator import DSLEvaluationError
from ade.interpreter.interpreter import Interpreter
from ade.lexer.lexer import Lexer
from ade.parser.parser import Parser


def test_dsl_lexer():
    """Test custom tokenization with rules, keywords, and whitespace ignoring."""
    engine = LanguageEngine("TestLang")
    engine.token("NUMBER", r"\d+(\.\d+)?", converter=float)
    engine.token("PLUS", r"\+")
    engine.token("STAR", r"\*")
    engine.ignore(r"\s+")

    tokens = engine.tokenize("42 + 3.14 * 10")
    assert len(tokens) == 6  # 42, +, 3.14, *, 10, EOF
    assert tokens[0].type == "NUMBER"
    assert tokens[0].value == 42.0
    assert tokens[1].type == "PLUS"
    assert tokens[2].type == "NUMBER"
    assert tokens[2].value == 3.14
    assert tokens[3].type == "STAR"
    assert tokens[4].type == "NUMBER"
    assert tokens[4].value == 10.0
    assert tokens[5].type == "EOF"


def test_dsl_parser_precedence():
    """Test Pratt operator precedence handling."""
    engine = LanguageEngine("Calc")
    engine.token("NUMBER", r"\d+", converter=int)
    engine.token("PLUS", r"\+")
    engine.token("STAR", r"\*")
    engine.token("LPAREN", r"\(")
    engine.token("RPAREN", r"\)")
    engine.ignore(r"\s+")

    engine.literal("NUMBER")
    engine.infix("PLUS", precedence=10, node_type="add")
    engine.infix("STAR", precedence=20, node_type="mul")
    engine.group("LPAREN", "RPAREN")

    # 2 + 3 * 4 -> add(2, mul(3, 4))
    ast1 = engine.parse("2 + 3 * 4")
    assert ast1.type == "program"
    root_expr = ast1.children[0]
    assert root_expr.type == "add"
    assert root_expr.children[0].type == "number"
    assert root_expr.children[0].value == 2
    assert root_expr.children[1].type == "mul"
    assert root_expr.children[1].children[0].value == 3
    assert root_expr.children[1].children[1].value == 4

    # (2 + 3) * 4 -> mul(add(2, 3), 4)
    ast2 = engine.parse("(2 + 3) * 4")
    root_expr2 = ast2.children[0]
    assert root_expr2.type == "mul"
    assert root_expr2.children[0].type == "add"
    assert root_expr2.children[1].value == 4


def test_dsl_ast_helpers():
    """Test DSLNode navigation, pretty printing, and serialization."""
    engine = LanguageEngine("Test")
    engine.token("NUMBER", r"\d+", converter=int)
    engine.token("PLUS", r"\+")
    engine.ignore(r"\s+")
    engine.literal("NUMBER")
    engine.infix("PLUS", 10, "add")

    ast = engine.parse("10 + 20")
    expr = ast.children[0]
    assert expr.child(0).value == 10
    assert expr.child(1).value == 20

    with pytest.raises(IndexError):
        expr.child(5)

    tree_str = expr.pretty()
    assert "(add" in tree_str
    assert "val='+'" in tree_str

    data = expr.to_dict()
    assert data["type"] == "add"
    assert len(data["children"]) == 2


def test_dsl_evaluator_python():
    """Test evaluating a custom DSL directly from Python."""
    engine = LanguageEngine("Calc")
    engine.token("NUMBER", r"\d+", converter=int)
    engine.token("PLUS", r"\+")
    engine.token("MINUS", r"-")
    engine.token("STAR", r"\*")
    engine.token("SLASH", r"/")
    engine.token("LPAREN", r"\(")
    engine.token("RPAREN", r"\)")
    engine.ignore(r"\s+")

    engine.literal("NUMBER")
    engine.binary_op("PLUS", 10, "add", lambda a, b: a + b)
    engine.binary_op("MINUS", 10, "sub", lambda a, b: a - b)
    engine.binary_op("STAR", 20, "mul", lambda a, b: a * b)
    engine.binary_op("SLASH", 20, "div", lambda a, b: a / b)
    engine.group("LPAREN", "RPAREN")

    result = engine.execute("10 + 5 * (4 - 2)")
    assert result == 20


def test_dsl_in_ade_calculator():
    """Test defining and executing a custom DSL completely inside an Ade program."""
    code = """
import language

calc = language.create("Calculator")
calc.token("NUMBER", "\\\\d+", false)
calc.token("PLUS", "\\\\+", false)
calc.token("STAR", "\\\\*", false)
calc.token("LPAREN", "\\\\(", false)
calc.token("RPAREN", "\\\\)", false)
calc.ignore("\\\\s+")

calc.literal("NUMBER")
calc.group("LPAREN", "RPAREN")

function do_add(a, b) {
    return a + b
}

function do_mul(a, b) {
    return a * b
}

calc.binary_op("PLUS", 10, "add", do_add)
calc.binary_op("STAR", 20, "mul", do_mul)

res1 = calc.execute("3 + 4 * 5")
res2 = calc.execute("(3 + 4) * 5")
"""
    lexer = Lexer(source=code, file_path="<test>")
    tokens = lexer.tokenize()
    parser = Parser(tokens=tokens, source_code=code)
    program = parser.parse()

    interp = Interpreter(source_code=code)
    interp.interpret(program)

    assert interp.environment.get("res1").value == 23
    assert interp.environment.get("res2").value == 35


def test_dsl_error_diagnostics():
    """Test that custom DSL syntax and lexical errors provide clear diagnostics."""
    engine = LanguageEngine("Test")
    engine.token("NUMBER", r"\d+")
    engine.ignore(r"\s+")

    # Lexer error on unknown character '@'
    with pytest.raises(DSLLexerError) as exc_info:
        engine.tokenize("123 @ 456")
    assert "Unexpected or unrecognized character '@'" in exc_info.value.diagnostic.message

    # Parser error on unexpected token
    engine.token("STAR", r"\*")
    engine.literal("NUMBER")
    engine.infix("STAR", 10, "mul")

    with pytest.raises(DSLParseError) as exc_info:
        engine.parse("* 42")
    assert "Unexpected token '*'" in exc_info.value.diagnostic.message


def test_dsl_cli_execution(tmp_path):
    """Test executing a DSL via the 'ade dsl <spec.ade> <input.dsl>' command."""
    import io
    from contextlib import redirect_stdout
    from ade.cli.main import main

    spec_file = tmp_path / "math_spec.ade"
    spec_file.write_text(
        """
import language

calc = language.create("MathDSL")
calc.token("NUMBER", "\\\\d+", false)
calc.token("PLUS", "\\\\+", false)
calc.token("STAR", "\\\\*", false)
calc.ignore("\\\\s+")

calc.literal("NUMBER")
calc.binary_op("PLUS", 10, "add", function(a, b) { return a + b })
calc.binary_op("STAR", 20, "mul", function(a, b) { return a * b })
""",
        encoding="utf-8",
    )

    dsl_file = tmp_path / "calc_input.dsl"
    dsl_file.write_text("10 + 20 * 3", encoding="utf-8")

    out = io.StringIO()
    with redirect_stdout(out):
        ret = main(["dsl", str(spec_file), str(dsl_file)])

    assert ret == 0
    assert "70" in out.getvalue()
