import logging

from basic_compiler.basic_exceptions import ParserError
from basic_compiler.basic_lex import Lexer
from basic_compiler.basic_token import Token, TokenType


class Parser:
    def __init__(self, lexer: Lexer):
        self._lexer = lexer

        self.symbol_table = set()
        self.declared_label = set()
        self.gotoed_label = set()

        self.token_method_map = {
            TokenType.IF: self.if_stmt,
            TokenType.SWITCH: self.switch_stmt,
            TokenType.WHILE: self.while_stmt,
            TokenType.DO: self.do_stmt,
            TokenType.FOR: self.for_stmt,
            TokenType.INPUT: self.input_stmt,
            TokenType.PRINT: self.print_stmt,
            TokenType.OPEN: self.open_stmt,
            TokenType.CLOSE: self.close_stmt,
            TokenType.LABEL: self.label_stmt,
            TokenType.GOTO: self.goto_stmt,
            TokenType.BREAK: self.break_stmt,
            TokenType.CONTINUE: self.continue_stmt,
            TokenType.RETURN: self.return_stmt,
        }

        self.type_tokens = {
            TokenType.BOOL,
            TokenType.INT,
            TokenType.FLOAT,
            TokenType.STRING,
            TokenType.IDENT,
        }

        self.color_tokens = {
            TokenType.BLACK,
            TokenType.WHITE,
            TokenType.RED,
            TokenType.ORANGE,
            TokenType.YELLOW,
            TokenType.GREEN,
            TokenType.BLUE,
            TokenType.INDIGO,
            TokenType.VIOLET,
        }

        self.normal_tokens = {
            # decisions
            TokenType.IF,
            TokenType.SWITCH,
            # loops
            TokenType.WHILE,
            TokenType.DO,
            TokenType.FOR,
            # io
            TokenType.INPUT,
            TokenType.PRINT,
            TokenType.OPEN,
            TokenType.CLOSE,
            # jumps
            TokenType.LABEL,
            TokenType.GOTO,
            TokenType.BREAK,
            TokenType.CONTINUE,
            TokenType.RETURN,
        }

        self.declaration_tokens = {TokenType.LET, TokenType.DIM, TokenType.CONST}

        self._current_token = None
        self._peek_token = None
        self.next_token()
        self.next_token()

    def check_token(self, token_type: TokenType) -> bool:
        """
        Check if the current token is of a certain type

        :param: token_type: The token type to check for
        :return: True if the current token is of the specified type, False otherwise
        """
        return token_type == self._current_token.token_type

    def check_peek(self, token_types: TokenType) -> bool:
        """
        Check if the next token is of a certain type

        :param token_types:
        :return: True if the next token is of the specified type, False otherwise
        """
        return self._peek_token.token_type in token_types

    def match(self, token_type: TokenType) -> None:
        """
        Try to match the current token with the specified token type. If not, raise an error

        :param token_type: The token type to match
        """
        if not self.check_token(token_type):
            self.abort(f"Expected {token_type}, got {self._current_token.token_type}")
        self.next_token()

    def next_token(self) -> None:
        """
        Advance the current token and the peek token
        """
        self._current_token = self._peek_token
        self._peek_token = self._lexer.get_token()

    def program(self) -> None:
        """
        program -> {stmt}
        """
        logging.debug("PROGRAM")

        while self.check_token(TokenType.NEWLINE):
            # Skip any leading newlines
            self.next_token()

        while not self.check_token(TokenType.EOF):
            # Parse all the stmts
            self.stmt()

        for label in self.gotoed_label:
            if label not in self.declared_label:
                self.abort(f"Attempting to GOTO undeclared label {label}")

    def stmt(self) -> None:
        """
        stmt ->
            class_stmt
            | func_stmt
            | struct_stmt
            | normal_stmt
            | declaration_stmt
        """
        logging.debug("STMT")

        if self.check_token(TokenType.CLASS):
            self.class_stmt()
        elif self.check_token(TokenType.FUNCTION):
            self.func_stmt()
        elif self.check_token(TokenType.STRUCT):
            self.struct_stmt()
        elif self.is_normal_stmt(self._current_token.token_type):
            self.normal_stmt()
        elif self.is_declaration_stmt(self._current_token.token_type):
            self.declaration_stmt()
        else:
            self.abort(f"Invalid statement at {self._current_token.token_text}")

    def class_stmt(self) -> None:
        """
        class_stmt ->
            "CLASS" ident nl
            ( "PUBLIC" | "PRIVATE" ) nl
            { func_stmt | declaration_stmt }
            "ENDCLASS" nl
        """
        logging.debug("STMT-CLASS")

        self.next_token()
        self.match(TokenType.IDENT)
        self.nl()

        if self.check_token(TokenType.PUBLIC) or self.check_token(TokenType.PRIVATE):
            self.next_token()
            self.nl()
        else:
            # Default to private
            pass

        while not self.check_token(TokenType.ENDCLASS):
            if self.check_token(TokenType.FUNCTION):
                self.func_stmt()
            else:
                self.declaration_stmt()

        self.match(TokenType.ENDCLASS)
        self.nl()

    def func_stmt(self) -> None:
        """
        func_stmt ->
            "FUNCTION" ident "(" [ param_list ] ")" [ "AS" type ] nl
            { normal_stmt | declaration_stmt }
            "ENDFUNCTION" nl
        """
        logging.debug("STMT-FUNC")

        self.next_token()
        self.match(TokenType.IDENT)
        self.match(TokenType.LPAREN)

        if not self.check_token(TokenType.RPAREN):
            # Read the parameter list
            # Since it may be empty, we need to check if the next token is a RPAREN
            self.param_list()

        self.match(TokenType.RPAREN)

        if self.check_token(TokenType.AS):
            self.next_token()
            if self.is_type(self._current_token.token_type):
                self.next_token()
            else:
                self.abort(f"Invalid type at {self._current_token.token_text}")

        self.nl()

        while not self.check_token(TokenType.ENDFUNCTION):
            if self.is_normal_stmt(self._current_token.token_type):
                self.normal_stmt()
            elif self.is_declaration_stmt(self._current_token.token_type):
                self.declaration_stmt()
            else:
                self.abort(f"Invalid statement at {self._current_token.token_text}")

        self.match(TokenType.ENDFUNCTION)
        self.nl()

    def param_list(self) -> None:
        """
        param_list ->
            ident "AS" type { "," ident "AS" type }
        """
        logging.debug("PARAM-LIST")

        self.match(TokenType.IDENT)
        self.match(TokenType.AS)

        if self.is_type(self._current_token.token_type):
            self.next_token()

        while self.check_token(TokenType.COMMA):
            self.next_token()
            self.match(TokenType.IDENT)
            self.match(TokenType.AS)

            if self.is_type(self._current_token.token_type):
                self.next_token()
            else:
                self.abort(f"Invalid type at {self._current_token.token_text}")

    def struct_stmt(self) -> None:
        """
        struct_stmt ->
            "STRUCT" ident nl
            { ident "AS" type nl }
            "ENDSTRUCT" nl
        """
        logging.debug("STMT-STRUCT")

        self.next_token()
        self.match(TokenType.IDENT)
        self.nl()

        while not self.check_token(TokenType.ENDSTRUCT):
            self.match(TokenType.IDENT)
            self.match(TokenType.AS)

            if self.is_type(self._current_token.token_type):
                self.next_token()
            else:
                self.abort(f"Invalid type at {self._current_token.token_text}")

            self.nl()

        self.match(TokenType.ENDSTRUCT)
        self.nl()

    def normal_stmt(self) -> None:
        """
        Parse a normal statement.
        """
        logging.debug("STMT-NORMAL")

        if self._current_token.token_type in self.token_method_map:
            self.token_method_map[self._current_token.token_type]()
        else:
            self.abort(f"Invalid statement at {self._current_token.token_text}")

    def declaration_stmt(self) -> None:
        """
        declaration_stmt ->
            "LET" ident "AS" type "=" expr nl
            | "DIM" ident "AS" type [ "(" expr ")" ] nl
            | "CONST" ( "LET" | "DIM" ) ident "AS" type [ "(" expr ")" ] "=" expr nl
        """
        logging.debug("STMT-DECLARATION")

        if self.check_token(TokenType.LET):
            self.let_stmt()
        elif self.check_token(TokenType.DIM):
            self.dim_stmt()
        elif self.check_token(TokenType.CONST):
            self.const_stmt()
        else:
            self.abort(
                f"Invalid declaration statement at {self._current_token.token_text}"
            )

    def let_stmt(self) -> None:
        """
        "LET" ident "AS" type "=" expr nl
        """
        logging.debug("STMT-LET")

        self.next_token()
        self.match(TokenType.IDENT)
        self.match(TokenType.AS)

        if self.is_type(self._current_token.token_type):
            self.next_token()

        self.match(TokenType.ASSIGN)
        self.expr()
        self.nl()

    def dim_stmt(self) -> None:
        """
        "DIM" ident "AS" type [ "(" expr ")" ] nl
        """
        logging.debug("STMT-DIM")

        self.next_token()
        self.match(TokenType.IDENT)
        self.match(TokenType.AS)

        if self.is_type(self._current_token.token_type):
            self.next_token()

        if self.check_token(TokenType.LPAREN):
            self.next_token()
            self.expr()
            self.match(TokenType.RPAREN)

        self.nl()

    def const_stmt(self) -> None:
        """
        "CONST" ( "LET" | "DIM" ) ident "AS" type [ "(" expr ")" ] "=" expr nl
        """
        logging.debug("STMT-CONST")

        self.next_token()

        if self.check_token(TokenType.LET) or self.check_token(TokenType.DIM):
            self.next_token()
        else:
            self.abort(
                f"Invalid constant statement at {self._current_token.token_text}"
            )

        self.match(TokenType.IDENT)
        self.match(TokenType.AS)

        if self.is_type(self._current_token.token_type):
            self.next_token()

        if self.check_token(TokenType.LPAREN):
            self.next_token()
            self.expr()
            self.match(TokenType.RPAREN)

        self.match(TokenType.ASSIGN)
        self.expr()
        self.nl()

    def decision_stmt(self) -> None:
        """
        decision_stmt ->
            if_stmt
            | switch_stmt
        """
        if self.check_token(TokenType.IF):
            self.if_stmt()
        elif self.check_token(TokenType.SWITCH):
            self.switch_stmt()
        else:
            self.abort(
                f"Invalid decision statement at {self._current_token.token_text}"
            )

    def if_stmt(self) -> None:
        """
        if_stmt ->
            "IF" expr "THEN" nl
            { normal_stmt }
            { "ELIF" expr "THEN" nl { normal_stmt } }
            [ "ELSE" nl { normal_stmt } ]
            "ENDIF" nl
        """
        logging.debug("STMT-IF")

        self.next_token()
        self.expr()
        self.match(TokenType.THEN)
        self.nl()

        while not self.check_token(TokenType.ENDIF):
            if self.check_token(TokenType.ELIF):
                self.next_token()
                self.expr()
                self.match(TokenType.THEN)
                self.nl()
            elif self.check_token(TokenType.ELSE):
                self.next_token()
                self.nl()
            else:
                self.normal_stmt()

        self.match(TokenType.ENDIF)
        self.nl()

    def switch_stmt(self) -> None:
        """
        switch_stmt ->
            "SWITCH" expr nl
            { "CASE" expr nl { normal_stmt } }
            [ "DEFAULT" nl { normal_stmt } ]
            "ENDSWITCH" nl
        """
        logging.debug("STMT-SWITCH")

        self.next_token()
        self.expr()
        self.nl()

        while not self.check_token(TokenType.ENDSWITCH):
            if self.check_token(TokenType.CASE):
                self.next_token()
                self.expr()
                self.nl()

                while not self.check_token(TokenType.CASE) and not self.check_token(
                    TokenType.DEFAULT
                ):
                    self.normal_stmt()
            elif self.check_token(TokenType.DEFAULT):
                self.next_token()
                self.nl()

                while not self.check_token(TokenType.ENDSWITCH):
                    self.normal_stmt()
            else:
                self.abort(
                    f"Invalid switch statement at {self._current_token.token_text}"
                )

        self.match(TokenType.ENDSWITCH)
        self.nl()

    def loop_stmt(self) -> None:
        """
        loop_stmt ->
            "WHILE" expr nl { normal_stmt |  declaration_stmt } "ENDWHILE" nl
            | "DO" nl { normal_stmt | declaration_stmt } "ENDDO" [ "WHILE" expr ] nl
            | "FOR" ident "AS" type "=" expr "TO" expr [ "STEP" expr ] nl { normal_stmt | declaration_stmt } "ENDFOR" nl
        """
        if self.check_token(TokenType.WHILE):
            self.while_stmt()
        elif self.check_token(TokenType.DO):
            self.do_stmt()
        elif self.check_token(TokenType.FOR):
            self.for_stmt()
        else:
            self.abort(f"Invalid loop statement at {self._current_token.token_text}")

    def while_stmt(self) -> None:
        """
        "WHILE" expr nl { normal_stmt | declaration_stmt } "ENDWHILE" nl
        """
        logging.debug("STMT-WHILE")

        self.next_token()
        self.expr()
        self.nl()

        while not self.check_token(TokenType.ENDWHILE):
            if self.is_normal_stmt(self._current_token.token_type):
                self.normal_stmt()
            elif self.is_declaration_stmt(self._current_token.token_type):
                self.declaration_stmt()
            else:
                self.abort(f"Invalid statement at {self._current_token.token_text}")

        self.match(TokenType.ENDWHILE)
        self.nl()

    def do_stmt(self) -> None:
        """
        "DO" nl { normal_stmt | declaration_stmt } "ENDDO" [ "WHILE" expr ] nl
        """
        logging.debug("STMT-DO")

        self.next_token()
        self.nl()

        while not self.check_token(TokenType.ENDDO):
            if self.is_normal_stmt(self._current_token.token_type):
                self.normal_stmt()
            elif self.is_declaration_stmt(self._current_token.token_type):
                self.declaration_stmt()
            else:
                self.abort(f"Invalid statement at {self._current_token.token_text}")

        self.match(TokenType.ENDDO)

        if self.check_token(TokenType.WHILE):
            self.next_token()
            self.expr()

        self.nl()

    def for_stmt(self) -> None:
        """
        "FOR" ident "AS" type "=" expr "TO" expr [ "STEP" expr ] nl { normal_stmt | declaration_stmt } "ENDFOR" nl
        """
        logging.debug("STMT-FOR")

        self.next_token()
        self.match(TokenType.IDENT)
        self.match(TokenType.AS)

        if self.is_type(self._current_token.token_type):
            self.next_token()

        self.match(TokenType.ASSIGN)
        self.expr()
        self.match(TokenType.TO)
        self.expr()

        if self.check_token(TokenType.STEP):
            self.next_token()
            self.expr()

        self.nl()

        while not self.check_token(TokenType.ENDFOR):
            if self.is_normal_stmt(self._current_token.token_type):
                self.normal_stmt()
            elif self.is_declaration_stmt(self._current_token.token_type):
                self.declaration_stmt()
            else:
                self.abort(f"Invalid statement at {self._current_token.token_text}")

        self.match(TokenType.ENDFOR)
        self.nl()

    def io_stmt(self) -> None:
        """
        io_stmt ->
            "INPUT" ident nl
            | "PRINT" [ color ] ( expr | string ) nl
            | "OPEN" string "FOR" ( "INPUT" | "OUTPUT" ) "AS" ident nl
            | "CLOSE" ident nl
        """
        logging.debug("STMT-IO")

        if self.check_token(TokenType.INPUT):
            self.input_stmt()
        elif self.check_token(TokenType.PRINT):
            self.print_stmt()
        elif self.check_token(TokenType.OPEN):
            self.open_stmt()
        elif self.check_token(TokenType.CLOSE):
            self.close_stmt()
        else:
            self.abort(f"Invalid io statement at {self._current_token.token_text}")

    def input_stmt(self) -> None:
        """
        "INPUT" ident nl
        """
        logging.debug("STMT-INPUT")

        self.next_token()
        self.match(TokenType.IDENT)
        self.nl()

    def print_stmt(self) -> None:
        """
        "PRINT" [color] (expr | string) nl
        """
        logging.debug("STMT-PRINT")

        self.next_token()

        if self.is_color(self._current_token.token_type):
            self.next_token()

        if self.check_token(TokenType.STRING):
            self.next_token()
        else:
            self.expr()

        self.nl()

    def open_stmt(self) -> None:
        """
        "OPEN" string "FOR" ("INPUT" | "OUTPUT") "AS" ident nl
        """
        logging.debug("STMT-OPEN")

        self.next_token()
        self.match(TokenType.STRING)
        self.match(TokenType.FOR)

        if self.check_token(TokenType.INPUT) or self.check_token(TokenType.OUTPUT):
            self.next_token()
        else:
            self.abort(
                f"Expected INPUT or OUTPUT, got {self._current_token.token_type}"
            )

        self.match(TokenType.AS)
        self.match(TokenType.IDENT)
        self.nl()

    def close_stmt(self) -> None:
        """
        "CLOSE" ident nl
        """
        logging.debug("STMT-CLOSE")

        self.next_token()
        self.match(TokenType.IDENT)
        self.nl()

    def jump_stmt(self) -> None:
        """
        jump_stmt ->
            "LABEL" ident nl
            | "GOTO" ident nl
            | "BREAK" nl
            | "CONTINUE" nl
            | "RETURN" [ expr ] nl
        """
        logging.debug("STMT-JUMP")

        if self.check_token(TokenType.LABEL):
            self.label_stmt()
        elif self.check_token(TokenType.GOTO):
            self.goto_stmt()
        elif self.check_token(TokenType.BREAK):
            self.break_stmt()
        elif self.check_token(TokenType.CONTINUE):
            self.continue_stmt()
        elif self.check_token(TokenType.RETURN):
            self.return_stmt()
        else:
            self.abort(f"Invalid jump statement at {self._current_token.token_text}")

    def label_stmt(self) -> None:
        """
        "LABEL" ident nl
        """
        logging.debug("STMT-LABEL")

        self.next_token()
        self.match(TokenType.IDENT)
        self.nl()

        self.declared_label.add(self._current_token.token_text)

    def goto_stmt(self) -> None:
        """
        "GOTO" ident nl
        """
        logging.debug("STMT-GOTO")

        self.next_token()
        self.match(TokenType.IDENT)
        self.nl()

        self.gotoed_label.add(self._current_token.token_text)

    def break_stmt(self) -> None:
        """
        "BREAK" nl
        """
        logging.debug("STMT-BREAK")

        self.next_token()
        self.nl()

    def continue_stmt(self) -> None:
        """
        "CONTINUE" nl
        """
        logging.debug("STMT-CONTINUE")

        self.next_token()
        self.nl()

    def return_stmt(self) -> None:
        """
        "RETURN" [ expr ] nl
        """
        logging.debug("STMT-RETURN")

        self.next_token()

        if not self.check_token(TokenType.NEWLINE):
            self.expr()

        self.nl()

    def expr(self) -> None:
        """
        expr -> logical_expr
        """
        logging.debug("EXPR")

        self.logical_expr()

    def logical_expr(self) -> None:
        """
        logical_expr -> logical_term {"OR" logical_term}
        """
        logging.debug("LOGICAL-EXPR")

        self.logical_term()

        while self.check_token(TokenType.OR):
            self.next_token()
            self.logical_term()

    def logical_term(self) -> None:
        """
        logical_term -> logical_factor {"AND" logical_factor}
        """
        logging.debug("LOGICAL-TERM")

        self.logical_factor()

        while self.check_token(TokenType.AND):
            self.next_token()
            self.logical_factor()

    def logical_factor(self) -> None:
        """
        logical_factor -> ["NOT"] comparison
        """
        logging.debug("LOGICAL-FACTOR")

        if self.check_token(TokenType.NOT):
            self.next_token()

        self.comparison()

    def comparison(self) -> None:
        """
        arith_expr [("==" | "!=" | "<" | ">" | "<=" | ">=") arith_expr]
        """
        logging.debug("COMPARISON")

        self.arith_expr()

        if self.is_cmp_op(self._current_token):
            self.next_token()
            self.arith_expr()

    def arith_expr(self) -> None:
        """
        arith_expr -> arith_term {("+" | "-") arith_term}
        """
        logging.debug("ARITH-EXPR")

        self.arith_term()

        while self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
            self.next_token()
            self.arith_term()

    def arith_term(self) -> None:
        """
        arith_term -> arith_factor {("*" | "/") arith_factor}
        """
        logging.debug("ARITH-TERM")

        self.arith_factor()

        while self.check_token(TokenType.MULT) or self.check_token(TokenType.DIV):
            self.next_token()
            self.arith_factor()

    def arith_factor(self) -> None:
        """
        arith_factor -> ["+" | "-"] arith_base
        """
        logging.debug("ARITH-FACTOR")

        if self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
            self.next_token()

        self.arith_base()

    def arith_base(self) -> None:
        """
        arith_base -> "(" expr ")" | bool | int | float | string | ident | function_call
        """
        logging.debug("ARITH-BASE")

        if self.check_token(TokenType.LPAREN):
            self.next_token()
            self.expr()
            self.match(TokenType.RPAREN)
        elif (
            self.check_token(TokenType.BOOL)
            or self.check_token(TokenType.INT)
            or self.check_token(TokenType.FLOAT)
            or self.check_token(TokenType.STRING)
            or self.check_token(TokenType.IDENT)
            or self.check_token(TokenType.TRUE)
            or self.check_token(TokenType.FALSE)
        ):
            self.next_token()
        else:
            self.function_call()

    def function_call(self) -> None:
        """
        function_call -> ident "(" [expr {"," expr}] ")"
        """
        logging.debug("FUNCTION-CALL")

        self.match(TokenType.IDENT)
        self.match(TokenType.LPAREN)

        if not self.check_token(TokenType.RPAREN):
            self.expr()

            while self.check_token(TokenType.COMMA):
                self.next_token()
                self.expr()

        self.match(TokenType.RPAREN)

    def is_normal_stmt(self, token_type: TokenType) -> bool:
        """
        :param token_type: The token type to check
        :return: If the current token is a normal statement
        """
        return token_type in self.normal_tokens

    def is_declaration_stmt(self, token_type: TokenType) -> bool:
        """
        :param token_type: The token type to check
        :return: If the current token is a declaration statement
        """
        return token_type in self.declaration_tokens

    def is_type(self, token_type: TokenType) -> bool:
        """
        type -> "BOOL" | "INT" | "FLOAT" | "STRING" | ident

        :param token_type: The token type to check
        :return: If the current token is a type
        """
        return token_type in self.type_tokens

    def is_color(self, token_type: TokenType) -> bool:
        """
        :param token_type: The token type to check
        :return: If the current token is a color
        """
        return token_type in self.color_tokens

    def nl(self) -> None:
        """
        nl -> ("\n" | "\r\n")+
        """
        logging.debug("NL")

        while self.check_token(TokenType.NEWLINE):
            self.next_token()

    @staticmethod
    def is_cmp_op(token: Token) -> bool:
        return token.token_type in [
            TokenType.EQ,
            TokenType.NOTEQ,
            TokenType.GT,
            TokenType.GTEQ,
            TokenType.LT,
            TokenType.LTEQ,
        ]

    @staticmethod
    def abort(message: str):
        raise ParserError(message)
