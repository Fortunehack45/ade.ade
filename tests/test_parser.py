"""Automated tests for Ade Parser."""

import pytest
from ade.lexer.lexer import Lexer
from ade.parser.parser import Parser
from ade.parser.errors import ParseError
from ade.ast.nodes import (
    Program,
    BinaryExpr,
    NumberLiteral,
    StringLiteral,
    BoolLiteral,
    NullLiteral,
    VarAssignmentStmt,
    SayStmt,
    IfStmt,
    WhileStmt,
    ForStmt,
    FunctionDeclStmt,
    CallExpr,
    ListLiteral,
    MapLiteral,
)


def parse_source(source: str) -> Program:
    tokens = Lexer(source).tokenize()
    return Parser(tokens, source_code=source).parse()


def test_parse_literals():
    source = "42\n\"hello\"\ntrue\nfalse\nnull"
    prog = parse_source(source)
    assert len(prog.statements) == 5


def test_parse_precedence():
    source = "x = 1 + 2 * 3"
    prog = parse_source(source)
    assert len(prog.statements) == 1
    assign = prog.statements[0]
    assert isinstance(assign, VarAssignmentStmt)
    
    # 1 + (2 * 3): top level binary is '+'
    bin_expr = assign.value
    assert isinstance(bin_expr, BinaryExpr)
    assert bin_expr.operator.lexeme == "+"
    assert isinstance(bin_expr.left, NumberLiteral) and bin_expr.left.value == 1
    assert isinstance(bin_expr.right, BinaryExpr)
    assert bin_expr.right.operator.lexeme == "*"


def test_parse_if_else():
    source = """
    if x > 10 {
        say "big"
    } else if x == 10 {
        say "ten"
    } else {
        say "small"
    }
    """
    prog = parse_source(source)
    assert len(prog.statements) == 1
    if_stmt = prog.statements[0]
    assert isinstance(if_stmt, IfStmt)
    assert isinstance(if_stmt.else_branch, IfStmt)
    assert if_stmt.else_branch.else_branch is not None


def test_parse_function_declaration():
    source = """
    function add(a, b) {
        return a + b
    }
    """
    prog = parse_source(source)
    assert len(prog.statements) == 1
    func = prog.statements[0]
    assert isinstance(func, FunctionDeclStmt)
    assert func.name == "add"
    assert func.params == ["a", "b"]
    assert len(func.body.statements) == 1


def test_parse_collections():
    source = """
    items = [1, 2, 3]
    user = { name: "Fortune", "level": 10 }
    """
    prog = parse_source(source)
    assert len(prog.statements) == 2
    assert isinstance(prog.statements[0].value, ListLiteral)
    assert isinstance(prog.statements[1].value, MapLiteral)


def test_parse_missing_paren_error():
    source = "result = add(10, 20"
    with pytest.raises(ParseError) as exc_info:
        parse_source(source)
    assert "expected ')' after function arguments" in exc_info.value.message


def test_parse_missing_brace_error():
    source = "if true say 1"
    with pytest.raises(ParseError) as exc_info:
        parse_source(source)
    assert "expected '{' before block body" in exc_info.value.message
