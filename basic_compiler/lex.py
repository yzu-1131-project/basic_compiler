from basic_compiler.token import Token, TokenType


class Lexer:
    def __init__(self, source: str) -> None:
        self._source = source + "\0"
        self._cur_char = ""
        self._cur_pos = -1
        self.next_char()

    def next_char(self) -> None:
        self._cur_pos += 1
        self._cur_char = (
            self._source[self._cur_pos] if self._cur_pos < len(self._source) else "\0"
        )

    def peek(self, offset: int = 1) -> str:
        return (
            self._source[self._cur_pos + offset]
            if self._cur_pos + offset < len(self._source)
            else "\0"
        )

    def get_token(self) -> Token | None:
        self.skip_whitespace()
        self.skip_comment()

        token = None

        if self._cur_char == "+":
            token = Token(self._cur_char, TokenType.PLUS)
        elif self._cur_char == "-":
            token = Token(self._cur_char, TokenType.MINUS)
        elif self._cur_char == "*":
            token = Token(self._cur_char, TokenType.MULT)
        elif self._cur_char == "/":
            token = Token(self._cur_char, TokenType.DIV)
        elif self._cur_char == "%":
            token = Token(self._cur_char, TokenType.MOD)
        elif self._cur_char == "^":
            token = Token(self._cur_char, TokenType.POW)
        elif self._cur_char == ",":
            token = Token(self._cur_char, TokenType.COMMA)
        elif self._cur_char == ":":
            token = Token(self._cur_char, TokenType.COLON)
        elif self._cur_char == ";":
            token = Token(self._cur_char, TokenType.SEMICOLON)
        elif self._cur_char == "(":
            token = Token(self._cur_char, TokenType.LPAREN)
        elif self._cur_char == ")":
            token = Token(self._cur_char, TokenType.RPAREN)
        elif self._cur_char == "[":
            token = Token(self._cur_char, TokenType.LSBRACKET)
        elif self._cur_char == "]":
            token = Token(self._cur_char, TokenType.RSBRACKET)
        elif self._cur_char == "{":
            token = Token(self._cur_char, TokenType.LCBRACKET)
        elif self._cur_char == "}":
            token = Token(self._cur_char, TokenType.RCBRACKET)
        elif self._cur_char == "=":
            if self.peek() == "=":
                token = Token("==", TokenType.EQ)
                self.next_char()
            else:
                token = Token(self._cur_char, TokenType.ASSIGN)
        elif self._cur_char == "<":
            if self.peek() == "=":
                token = Token("<=", TokenType.LTEQ)
                self.next_char()
            else:
                token = Token(self._cur_char, TokenType.LT)
        elif self._cur_char == ">":
            if self.peek() == "=":
                token = Token(">=", TokenType.GTEQ)
                self.next_char()
            else:
                token = Token(self._cur_char, TokenType.GT)
        elif self._cur_char == "!":
            if self.peek() == "=":
                token = Token("!=", TokenType.NOTEQ)
                self.next_char()
            else:
                self.abort(f"Expected !=, got !{self.peek()}")
        elif self._cur_char == '"':
            self.next_char()
            start_pos = self._cur_pos

            while self._cur_char != '"':
                if self._cur_char == "\\":
                    if self.peek() in ['"', "\\"]:
                        # if the string is \", \\, we need to skip the escape character
                        self.next_char()
                self.next_char()

            token = Token(self._source[start_pos : self._cur_pos], TokenType.STRING)
        elif self._cur_char.isdigit():
            start_pos = self._cur_pos
            while self.peek().isdigit():
                self.next_char()
            if self.peek() == ".":
                self.next_char()
                if not self.peek().isdigit():
                    self.abort('Number must have at least one digit after "."')
                while self.peek().isdigit():
                    self.next_char()

                if self.peek() == ".":
                    self.abort('Number must have only one "."')
                token = Token(
                    self._source[start_pos : self._cur_pos + 1], TokenType.FLOAT
                )
            else:
                token = Token(
                    self._source[start_pos : self._cur_pos + 1], TokenType.INT
                )
        elif self._cur_char.isalpha():
            start_pos = self._cur_pos
            while self.peek().isalnum():
                self.next_char()
            token_text = self._source[start_pos : self._cur_pos + 1]
            keyword = Token.check_if_keyword(token_text)
            if keyword is None:
                # if the token is not a keyword, it is an identifier
                token = Token(token_text, TokenType.IDENT)
            else:
                # else, it is a keyword
                token = Token(token_text, keyword)
        elif self._cur_char == "\n":
            token = Token(self._cur_char, TokenType.NEWLINE)
        elif self._cur_char == "\0":
            token = Token("", TokenType.EOF)
        else:
            self.abort(f"Unknown token {self._cur_char}")

        self.next_char()
        return token

    def abort(self, message: str) -> None:
        raise Exception(f"Lexing error. {message}")

    def skip_whitespace(self) -> None:
        while self._cur_char in [" ", "\t", "\r"]:
            self.next_char()

    def skip_comment(self) -> None:
        if self._cur_char == "#":
            while self._cur_char != "\n":
                self.next_char()

                if self._cur_char == "\0":
                    return
