from typing import List, Optional
from basic_compiler.basic_token import Token, TokenType
from basic_compiler.basic_exceptions import LexerError


class Lexer:
    def __init__(self, sources: List[str]) -> None:
        self._sources = sources
        self._line_number = 0
        self._line_text = sources[0] if sources else ""
        self._cur_pos = -1
        self._cur_char = ""
        self._next_char()

        self._token_map = {
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.MULT,
            "/": TokenType.DIV,
            "%": TokenType.MOD,
            "^": TokenType.POW,
            ",": TokenType.COMMA,
            ":": TokenType.COLON,
            ";": TokenType.SEMICOLON,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "[": TokenType.LSBRACKET,
            "]": TokenType.RSBRACKET,
            "{": TokenType.LCBRACKET,
            "}": TokenType.RCBRACKET,
        }

    def _next_char(self) -> None:
        self._cur_pos += 1
        while self._cur_pos >= len(self._line_text):
            self._line_number += 1
            if self._line_number >= len(self._sources):
                self._cur_char = "\0"
                return
            self._line_text = self._sources[self._line_number]
            self._cur_pos = 0
        self._cur_char = self._line_text[self._cur_pos]

    def _peek(self, offset: int = 1) -> str:
        pos = self._cur_pos + offset
        if pos >= len(self._line_text):
            return "\0"
        return self._line_text[pos]

    def get_token(self) -> Optional[Token]:
        self._skip_whitespace()
        self._skip_comment()

        if self._cur_char == "\0":
            return Token("", TokenType.EOF, self._line_number, self._line_text)
        if self._cur_char == "\n":
            token = Token("\n", TokenType.NEWLINE, self._line_number, self._line_text)
            self._next_char()
            return token
        if self._cur_char in self._token_map:
            token = Token(
                self._cur_char,
                self._token_map[self._cur_char],
                self._line_number,
                self._line_text,
            )
            self._next_char()
            return token

        if self._cur_char in ("=", "<", ">", "!"):
            return self._lex_operator()
        if self._cur_char == '"':
            return self._lex_string()
        if self._cur_char.isdigit():
            return self._lex_number()
        if self._cur_char.isalpha() or self._cur_char == "_":
            return self._lex_identifier()

        self.abort(f"Unknown token: '{self._cur_char}'")
        return None  # Unreachable

    def _lex_operator(self) -> Token:
        char = self._cur_char
        next_char = self._peek()
        token_type = None

        if char == "=" and next_char == "=":
            self._next_char()
            token_type = TokenType.EQ
        elif char == "=":
            token_type = TokenType.ASSIGN
        elif char == "<" and next_char == "=":
            self._next_char()
            token_type = TokenType.LTEQ
        elif char == "<":
            token_type = TokenType.LT
        elif char == ">" and next_char == "=":
            self._next_char()
            token_type = TokenType.GTEQ
        elif char == ">":
            token_type = TokenType.GT
        elif char == "!" and next_char == "=":
            self._next_char()
            token_type = TokenType.NOTEQ
        else:
            self.abort(f"Unexpected character '{char}'")

        token_text = char + (self._cur_char if self._cur_pos > 0 else "")
        token = Token(token_text, token_type, self._line_number, self._line_text)
        self._next_char()
        return token

    def _lex_string(self) -> Token:
        self._next_char()
        start_pos = self._cur_pos
        string_value = ""

        while self._cur_char != '"' and self._cur_char != "\0":
            if self._cur_char == "\\":
                self._next_char()
                escape_chars = {"n": "\n", "t": "\t", "r": "\r", "\\": "\\", '"': '"'}
                string_value += escape_chars.get(self._cur_char, self._cur_char)
            else:
                string_value += self._cur_char
            self._next_char()

        if self._cur_char != '"':
            self.abort("Unterminated string literal")
        self._next_char()
        return Token(string_value, TokenType.STRING, self._line_number, self._line_text)

    def _lex_number(self) -> Token:
        start_pos = self._cur_pos
        has_decimal = False

        while True:
            next_char = self._peek()
            if next_char.isdigit():
                self._next_char()
            elif next_char == "." and not has_decimal:
                has_decimal = True
                self._next_char()
            else:
                break

        number_text = self._line_text[start_pos : self._cur_pos + 1]
        token_type = TokenType.FLOAT if has_decimal else TokenType.INT
        token = Token(number_text, token_type, self._line_number, self._line_text)
        self._next_char()
        return token

    def _lex_identifier(self) -> Token:
        start_pos = self._cur_pos

        while self._peek().isalnum() or self._peek() == "_":
            self._next_char()

        token_text = self._line_text[start_pos : self._cur_pos + 1]
        token_type = Token.check_if_keyword(token_text) or TokenType.IDENT
        token = Token(token_text, token_type, self._line_number, self._line_text)
        self._next_char()
        return token

    def _skip_whitespace(self) -> None:
        while self._cur_char in " \t\r":
            self._next_char()

    def _skip_comment(self) -> None:
        if self._cur_char == "#":
            while self._cur_char not in ("\n", "\0"):
                self._next_char()
            self._next_char()

    def abort(self, message: str) -> None:
        raise LexerError(f"Line {self._line_number + 1}: {message}")
