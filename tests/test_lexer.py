"""Automated tests for Ade Lexer."""

import pytest
from ade.lexer.lexer import Lexer
from ade.lexer.token import TokenType
from ade.lexer.errors import LexerError


def test_lexer_numbers():
    source = "10 20.5 0 1000"
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    assert len(tokens) == 5  # 4 numbers + EOF
    assert tokens[0].type == TokenType.NUMBER and tokens[0].literal == 10
    assert tokens[1].type == TokenType.NUMBER and tokens[1].literal == 20.5
    assert tokens[2].type == TokenType.NUMBER and tokens[2].literal == 0
    assert tokens[3].type == TokenType.NUMBER and tokens[3].literal == 1000
    assert tokens[4].type == TokenType.EOF


def test_lexer_strings():
    source = '"hello" "world\\nwith\\tnewline" "\\""'
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    assert len(tokens) == 4
    assert tokens[0].type == TokenType.STRING and tokens[0].literal == "hello"
    assert tokens[1].type == TokenType.STRING and tokens[1].literal == "world\nwith\tnewline"
    assert tokens[2].type == TokenType.STRING and tokens[2].literal == '"'


def test_lexer_keywords_and_identifiers():
    source = "function return if else while for in break continue say true false null and or not user_name"
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    expected_types = [
        TokenType.FUNCTION,
        TokenType.RETURN,
        TokenType.IF,
        TokenType.ELSE,
        TokenType.WHILE,
        TokenType.FOR,
        TokenType.IN,
        TokenType.BREAK,
        TokenType.CONTINUE,
        TokenType.SAY,
        TokenType.TRUE,
        TokenType.FALSE,
        TokenType.NULL,
        TokenType.AND,
        TokenType.OR,
        TokenType.NOT,
        TokenType.IDENTIFIER,
        TokenType.EOF,
    ]
    assert [t.type for t in tokens] == expected_types
    assert tokens[-2].lexeme == "user_name"


def test_lexer_operators():
    source = "+ - * / % = == != < <= > >= ."
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    expected_types = [
        TokenType.PLUS,
        TokenType.MINUS,
        TokenType.STAR,
        TokenType.SLASH,
        TokenType.PERCENT,
        TokenType.EQUAL,
        TokenType.EQUAL_EQUAL,
        TokenType.BANG_EQUAL,
        TokenType.LESS,
        TokenType.LESS_EQUAL,
        TokenType.GREATER,
        TokenType.GREATER_EQUAL,
        TokenType.DOT,
        TokenType.EOF,
    ]
    assert [t.type for t in tokens] == expected_types


def test_lexer_delimiters():
    source = "{} () [] , :"
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    expected_types = [
        TokenType.LBRACE,
        TokenType.RBRACE,
        TokenType.LPAREN,
        TokenType.RPAREN,
        TokenType.LBRACKET,
        TokenType.RBRACKET,
        TokenType.COMMA,
        TokenType.COLON,
        TokenType.EOF,
    ]
    assert [t.type for t in tokens] == expected_types


def test_lexer_comments():
    source = """
    # This is a comment
    x = 10 # Inline comment
    # Another comment
    say x
    """
    lexer = Lexer(source)
    tokens = lexer.tokenize()

    lexemes = [t.lexeme for t in tokens if t.type not in (TokenType.NEWLINE, TokenType.EOF)]
    assert lexemes == ["x", "=", "10", "say", "x"]


def test_lexer_source_locations():
    source = "a = 10\nb = 20"
    lexer = Lexer(source, file_path="test.ade")
    tokens = lexer.tokenize()

    # 'a' is on line 1, col 1
    assert tokens[0].span.start.line == 1
    assert tokens[0].span.start.column == 1

    # find 'b'
    b_tok = [t for t in tokens if t.lexeme == "b"][0]
    assert b_tok.span.start.line == 2
    assert b_tok.span.start.column == 1


def test_lexer_unterminated_string():
    source = 'name = "Fortune'
    lexer = Lexer(source)
    with pytest.raises(LexerError) as exc_info:
        lexer.tokenize()
    assert "Unterminated string literal" in exc_info.value.message


def test_lexer_invalid_character():
    source = "x = @ 10"
    lexer = Lexer(source)
    with pytest.raises(LexerError) as exc_info:
        lexer.tokenize()
    assert "Unexpected character '@'" in exc_info.value.message
