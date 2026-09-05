"""Lexer for the Ade programming language."""

from typing import List, Optional
from ade.diagnostics.span import SourceLocation, SourceSpan
from ade.lexer.token import Token, TokenType, KEYWORDS
from ade.lexer.errors import LexerError


class Lexer:
    """Scans Ade source text into a stream of tokens."""

    def __init__(self, source: str, file_path: str = "<stdin>"):
        self.source = source
        self.file_path = file_path
        self.length = len(source)
        self.start_idx = 0
        self.current_idx = 0
        self.line = 1
        self.column = 1
        self.start_line = 1
        self.start_column = 1
        self.delimiter_depth = 0  # (), [], {} depth for newline suppression
        self.tokens: List[Token] = []

    def tokenize(self) -> List[Token]:
        """Scan the entire source text and return a list of tokens ending with EOF."""
        while not self._is_at_end():
            self.start_idx = self.current_idx
            self.start_line = self.line
            self.start_column = self.column
            self._scan_token()

        # Add EOF token
        loc = SourceLocation(self.file_path, self.line, self.column, self.current_idx)
        self.tokens.append(
            Token(
                type=TokenType.EOF,
                lexeme="",
                literal=None,
                span=SourceSpan(loc, loc),
            )
        )
        return self.tokens

    def _is_at_end(self) -> bool:
        return self.current_idx >= self.length

    def _advance(self) -> str:
        ch = self.source[self.current_idx]
        self.current_idx += 1
        self.column += 1
        return ch

    def _peek(self) -> str:
        if self._is_at_end():
            return "\0"
        return self.source[self.current_idx]

    def _peek_next(self) -> str:
        if self.current_idx + 1 >= self.length:
            return "\0"
        return self.source[self.current_idx + 1]

    def _match(self, expected: str) -> bool:
        if self._is_at_end():
            return False
        if self.source[self.current_idx] != expected:
            return False
        self.current_idx += 1
        self.column += 1
        return True

    def _make_span(self) -> SourceSpan:
        start_loc = SourceLocation(
            self.file_path, self.start_line, self.start_column, self.start_idx
        )
        end_loc = SourceLocation(
            self.file_path, self.line, self.column, self.current_idx
        )
        return SourceSpan(start_loc, end_loc)

    def _add_token(self, token_type: TokenType, literal: Optional[object] = None) -> None:
        lexeme = self.source[self.start_idx : self.current_idx]
        self.tokens.append(
            Token(type=token_type, lexeme=lexeme, literal=literal, span=self._make_span())
        )

    def _scan_token(self) -> None:
        c = self._advance()

        if c in " \t\r":
            # Ignore horizontal whitespace
            return

        if c == "\n":
            self.line += 1
            self.column = 1
            # Only emit newline if not inside (), [], and previous token was not already a NEWLINE
            if self.delimiter_depth == 0 and self.tokens:
                last_type = self.tokens[-1].type
                if last_type not in (
                    TokenType.NEWLINE,
                    TokenType.LBRACE,
                    TokenType.COMMA,
                    TokenType.COLON,
                    TokenType.EQUAL,
                    TokenType.PLUS,
                    TokenType.MINUS,
                    TokenType.STAR,
                    TokenType.SLASH,
                    TokenType.PERCENT,
                ):
                    self._add_token(TokenType.NEWLINE)
            return

        if c == ";":
            # Treat semicolon as statement terminator
            if self.tokens and self.tokens[-1].type != TokenType.NEWLINE:
                self._add_token(TokenType.NEWLINE)
            return

        if c == "#":
            # Single-line comment: consume until newline or EOF
            while self._peek() != "\n" and not self._is_at_end():
                self._advance()
            return

        # Delimiters
        if c == "(":
            self.delimiter_depth += 1
            self._add_token(TokenType.LPAREN)
            return
        if c == ")":
            if self.delimiter_depth > 0:
                self.delimiter_depth -= 1
            self._add_token(TokenType.RPAREN)
            return
        if c == "[":
            self.delimiter_depth += 1
            self._add_token(TokenType.LBRACKET)
            return
        if c == "]":
            if self.delimiter_depth > 0:
                self.delimiter_depth -= 1
            self._add_token(TokenType.RBRACKET)
            return
        if c == "{":
            self._add_token(TokenType.LBRACE)
            return
        if c == "}":
            self._add_token(TokenType.RBRACE)
            return
        if c == ",":
            self._add_token(TokenType.COMMA)
            return
        if c == ":":
            self._add_token(TokenType.COLON)
            return
        if c == ".":
            self._add_token(TokenType.DOT)
            return

        # Operators
        if c == "+":
            self._add_token(TokenType.PLUS)
            return
        if c == "-":
            self._add_token(TokenType.MINUS)
            return
        if c == "*":
            self._add_token(TokenType.STAR)
            return
        if c == "/":
            self._add_token(TokenType.SLASH)
            return
        if c == "%":
            self._add_token(TokenType.PERCENT)
            return

        if c == "=":
            if self._match("="):
                self._add_token(TokenType.EQUAL_EQUAL)
            else:
                self._add_token(TokenType.EQUAL)
            return

        if c == "!":
            if self._match("="):
                self._add_token(TokenType.BANG_EQUAL)
                return
            else:
                span = self._make_span()
                raise LexerError(
                    message="Unexpected character '!'. Did you mean 'not' or '!='?",
                    span=span,
                    source_code=self.source,
                    hint="In Ade, boolean negation uses the 'not' keyword and inequality uses '!='.",
                    suggested_fix="not"
                )

        if c == "<":
            if self._match("="):
                self._add_token(TokenType.LESS_EQUAL)
            else:
                self._add_token(TokenType.LESS)
            return

        if c == ">":
            if self._match("="):
                self._add_token(TokenType.GREATER_EQUAL)
            else:
                self._add_token(TokenType.GREATER)
            return

        # String literals
        if c == '"':
            self._scan_string()
            return

        # Numbers
        if c.isdigit():
            self._scan_number()
            return

        # Identifiers and keywords
        if c.isalpha() or c == "_":
            self._scan_identifier()
            return

        # Unrecognized character
        span = self._make_span()
        raise LexerError(
            message=f"Unexpected character '{c}'.",
            span=span,
            source_code=self.source,
            hint="Check for invalid characters or unsupported symbols."
        )

    def _scan_string(self) -> None:
        chars: List[str] = []
        while self._peek() != '"' and not self._is_at_end():
            if self._peek() == "\n":
                self.line += 1
                self.column = 1
                chars.append(self._advance())
            elif self._peek() == "\\":
                self._advance()  # Skip backslash
                if self._is_at_end():
                    break
                escape_char = self._advance()
                if escape_char == "n":
                    chars.append("\n")
                elif escape_char == "t":
                    chars.append("\t")
                elif escape_char == '"':
                    chars.append('"')
                elif escape_char == "\\":
                    chars.append("\\")
                else:
                    chars.append("\\" + escape_char)
            else:
                chars.append(self._advance())

        if self._is_at_end():
            span = self._make_span()
            raise LexerError(
                message="Unterminated string literal.",
                span=span,
                source_code=self.source,
                hint="Strings in Ade must be closed with a matching double quote '\"'.",
                suggested_fix=self.source[self.start_idx : self.current_idx] + '"'
            )

        # Closing quote
        self._advance()
        value = "".join(chars)
        self._add_token(TokenType.STRING, literal=value)

    def _scan_number(self) -> None:
        while self._peek().isdigit():
            self._advance()

        is_decimal = False
        if self._peek() == "." and self._peek_next().isdigit():
            is_decimal = True
            self._advance()  # consume '.'
            while self._peek().isdigit():
                self._advance()

        lexeme = self.source[self.start_idx : self.current_idx]
        literal_val = float(lexeme) if is_decimal else int(lexeme)
        self._add_token(TokenType.NUMBER, literal=literal_val)

    def _scan_identifier(self) -> None:
        while self._peek().isalnum() or self._peek() == "_":
            self._advance()

        lexeme = self.source[self.start_idx : self.current_idx]
        token_type = KEYWORDS.get(lexeme, TokenType.IDENTIFIER)
        
        literal_val = None
        if token_type == TokenType.TRUE:
            literal_val = True
        elif token_type == TokenType.FALSE:
            literal_val = False
        elif token_type == TokenType.NULL:
            literal_val = None

        self._add_token(token_type, literal=literal_val)
