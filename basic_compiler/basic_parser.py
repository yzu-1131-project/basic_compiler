import logging
from typing import Optional

from basic_compiler.basic_emitter import Emitter
from basic_compiler.basic_exceptions import ParserError
from basic_compiler.basic_lex import Lexer
from basic_compiler.basic_symbol_set import SymbolTable
from basic_compiler.basic_token import Token, TokenType


class Parser:
    def __init__(self, lexer: Lexer, emitter: Emitter = None):
        self._lexer = lexer
        self._emitter = emitter

        self._symbol_table = SymbolTable()

        self._normal_tokens_map = {
            # decisions
            TokenType.IF: self.if_stmt,
            TokenType.SWITCH: self.switch_stmt,
            # loops
            TokenType.WHILE: self.while_stmt,
            TokenType.DO: self.do_stmt,
            TokenType.FOR: self.for_stmt,
            # io
            TokenType.INPUT: self.input_stmt,
            TokenType.PRINT: self.print_stmt,
            TokenType.OPEN: self.open_stmt,
            TokenType.CLOSE: self.close_stmt,
            # jumps
            TokenType.BREAK: self.break_stmt,
            TokenType.CONTINUE: self.continue_stmt,
            TokenType.RETURN: self.return_stmt,
            # TokenType.IDENT: self.function_call
        }

        self._type_tokens = {
            TokenType.BOOL,
            TokenType.INT,
            TokenType.FLOAT,
            TokenType.STRING,
            TokenType.IDENT,
        }

        self._color_tokens = {
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

        self._declaration_tokens = {TokenType.LET, TokenType.DIM, TokenType.CONST}

        self._current_token = None
        self._peek_token = None
        self.next_token()
        self.next_token()

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

        self._emitter.write_file()

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
            self.abort(f"Invalid statement at {self._current_token.token_text}"
                       f" {self._current_token.line_number}: {self._current_token.line_text}")

    def class_stmt(self) -> None:
        """
        class_stmt ->
            "CLASS" ident nl
            { ( "PUBLIC" | "PRIVATE" ) nl
            func_stmt | declaration_stmt }
            "ENDCLASS" nl
        """
        logging.debug("STMT-CLASS")

        self.next_token()
        class_name = self._current_token.token_text
        self._symbol_table.insert(self._current_token)
        self.match(TokenType.IDENT)
        self._emitter.emit_line(f"class {class_name} {{")
        self.nl()

        while not self.check_token(TokenType.ENDCLASS):
            access_modifier = "private"
            if self.check_token(TokenType.PUBLIC) or self.check_token(
                TokenType.PRIVATE
            ):
                access_modifier = self._current_token.token_text.lower()
                self.next_token()
                self.nl()
            self._emitter.emit_line(f"{access_modifier}:")

            if self.check_token(TokenType.FUNCTION):
                self.func_stmt()
            elif self.is_declaration_stmt(self._current_token.token_type):
                self.declaration_stmt()
            else:
                self.abort(
                    f"Invalid statement in class at {self._current_token.token_text}"
                    f" {self._current_token.line_number}: {self._current_token.line_text}"
                )

        self.match(TokenType.ENDCLASS)
        self.nl()
        self._emitter.emit_line("};")

    def func_stmt(self) -> None:
        """
        func_stmt ->
            "FUNCTION" ident "(" [ param_list ] ")" [ "AS" type ] nl
            { normal_stmt | declaration_stmt }
            "ENDFUNCTION" nl
        """
        logging.debug("STMT-FUNC")

        self.next_token()
        tmp_func_name = self._current_token.token_text
        if self._symbol_table.get_line_text(tmp_func_name) is None:
            self._symbol_table.insert(self._current_token)
        tmp_func_return_type = "void"
        tmp_param_list = ""
        self.match(TokenType.IDENT)
        self.match(TokenType.LPAREN)

        if not self.check_token(TokenType.RPAREN):
            # Read the parameter list
            tmp_param_list = self.param_list()

        self.match(TokenType.RPAREN)

        if self.check_token(TokenType.AS):
            self.next_token()
            if self.is_type(self._current_token.token_type):
                tmp_func_return_type = self._current_token.token_text
                self.next_token()
            else:
                self.abort(f"Invalid type at {self._current_token.token_text}"
                           f" {self._current_token.line_number}: {self._current_token.line_text}")

        self.nl()
        if (
            self._symbol_table.get_line_text(tmp_func_name) is not None
            and self._symbol_table.get_line_text(tmp_func_name).find("CLASS") != -1
        ):
            self._emitter.emit_line(f"{tmp_func_name} ({tmp_param_list}) {{")
        else:
            self._emitter.emit_line(
                f"{tmp_func_return_type.lower()} {tmp_func_name}({tmp_param_list}) {{"
            )

        while not self.check_token(TokenType.ENDFUNCTION):
            self.normal_or_declaration_stmt()

        self.match(TokenType.ENDFUNCTION)
        self.nl()
        self._emitter.emit_line("}")

    def param_list(self) -> str:
        """
        param_list ->
            expr [AS type] { "," expr (AS type) }
        """
        logging.debug("PARAM-LIST")

        tmp_param_list = ""
        tmp_type = ""
        tmp_expr = self.expr()

        if self.check_token(TokenType.AS):
            self.next_token()
            if self.is_type(self._current_token.token_type):
                tmp_type = self._current_token.token_text
                self.next_token()
            else:
                self.abort(f"Invalid type at {self._current_token.token_text}"
                           f" {self._current_token.line_number}: {self._current_token.line_text}")

        tmp_param_list += f"{tmp_type.lower()} {tmp_expr}"

        if self.check_token(TokenType.COMMA):
            self.next_token()
            tmp_param_list += ", " + self.param_list()

        return tmp_param_list

    def struct_stmt(self) -> None:
        """
        struct_stmt ->
            "STRUCT" ident nl
            { ident "AS" type nl }
            "ENDSTRUCT" nl
        """
        logging.debug("STMT-STRUCT")

        self.next_token()
        self._emitter.emit_line(f"struct {self._current_token.token_text} {{")
        self._symbol_table.insert(self._current_token)
        self.match(TokenType.IDENT)
        self.nl()

        while not self.check_token(TokenType.ENDSTRUCT):
            tmp_ident = self._current_token.token_text
            tmp_type = ""
            self.match(TokenType.IDENT)
            self.match(TokenType.AS)

            if self.is_type(self._current_token.token_type):
                tmp_type = self._current_token.token_text
                self.next_token()
            else:
                self.abort(f"Invalid type at {self._current_token.token_text}"
                           f" {self._current_token.line_number}: {self._current_token.line_text}")

            self._emitter.emit_line(f"{tmp_type.lower()} {tmp_ident};")
            self.nl()

        self.match(TokenType.ENDSTRUCT)
        self.nl()
        self._emitter.emit_line("};")

    def normal_stmt(self) -> None:
        """
        Parse a normal statement.
        """
        logging.debug("STMT-NORMAL")

        if self._current_token.token_type in self._normal_tokens_map:
            self._normal_tokens_map[self._current_token.token_type]()
        elif self._current_token.token_type == TokenType.IDENT:
            if self._symbol_table.find(self._current_token.token_text) is not None:
                tmp_token_text = self._symbol_table.lookup(
                    self._current_token.token_text
                ).line_text
                if (
                    tmp_token_text.find("CLASS") != -1
                    or tmp_token_text.find("FUNCTION") != -1
                    or tmp_token_text.find("STRUCT") != -1
                    or tmp_token_text.find("RETURN") != -1
                ):
                    self.function_call()
                else:
                    self.id_let_stmt()
        else:
            self.abort(f"Invalid statement at {self._current_token.token_text}"
                       f" {self._current_token.line_number}: {self._current_token.line_text}")

    def declaration_stmt(self) -> None:
        """
        declaration_stmt ->
            ident "=" expr nl
            | "LET" ident "AS" type "=" expr nl
            | "DIM" ident "AS" type [ "(" expr ")" ] nl
            | "CONST" ( "LET" | "DIM" ) ident "AS" type [ "(" expr ")" ] "=" expr nl
        """
        logging.debug("STMT-DECLARATION")

        if self.check_token(TokenType.IDENT):
            self.id_let_stmt()
        elif self.check_token(TokenType.LET):
            self.let_stmt()
        elif self.check_token(TokenType.DIM):
            self.dim_stmt()
        elif self.check_token(TokenType.CONST):
            self.const_stmt()
        else:
            self.abort(
                f"Invalid declaration statement at {self._current_token.token_text}"
                f" {self._current_token.line_number}: {self._current_token.line_text}"
            )

    def id_let_stmt(self) -> None:
        """
        ident "=" expr nl
        """
        logging.debug("STMT-ID-LET")

        if self._symbol_table.lookup(self._current_token.token_text):
            self._emitter.emit_line(f"{self._current_token.token_text} = ")
            self.next_token()
            self.match(TokenType.ASSIGN)
            self._emitter.emit_line(self.expr())
            self.nl()
            self._emitter.emit_line(";")
        else:
            self.abort(
                f"Variable {self._current_token.token_text} not declared"
                f" {self._current_token.line_number}: {self._current_token.line_text}"
            )

    def let_stmt(self) -> None:
        """
        "LET" ident "AS" type "=" expr nl
        | LET ident "AS" type(expr) nl
        """
        logging.debug("STMT-LET")

        self.next_token()
        tmp_ident = self._current_token.token_text
        self._symbol_table.insert(self._current_token)

        self.match(TokenType.IDENT)
        self.match(TokenType.AS)

        if self.is_type(self._current_token.token_type):
            tmp_type = self._current_token.token_text
            self.next_token()

            if self.check_token(TokenType.LPAREN):
                self.next_token()
                self._emitter.emit_line(f"{tmp_type.lower()} {tmp_ident} {{")
                self._emitter.emit_line(self.expr())
                self.match(TokenType.RPAREN)
                self._emitter.emit_line("}")
            else:
                self._emitter.emit_line(f"{tmp_type.lower()} {tmp_ident} = ")
                self.match(TokenType.ASSIGN)
                self._emitter.emit_line(self.expr())

        self.nl()
        self._emitter.emit_line(";")

    def dim_stmt(self) -> None:
        """
        "DIM" ident "AS" type [ "(" expr ")" ] nl
        """
        logging.debug("STMT-DIM")

        self.next_token()
        tmp_ident = self._current_token.token_text
        self._symbol_table.insert(self._current_token)
        self.match(TokenType.IDENT)
        self.match(TokenType.AS)

        if self.is_type(self._current_token.token_type):
            tmp_type = self._current_token.token_text
            self._emitter.emit_line(f"{tmp_type.lower()} {tmp_ident} [")
            self.next_token()

        if self.check_token(TokenType.LPAREN):
            self.next_token()
            self._emitter.emit_line(self.expr())
            self.match(TokenType.RPAREN)

        self.nl()
        self._emitter.emit_line("] = {};")

    def const_stmt(self) -> None:
        """
        "CONST" ( "LET" | "DIM" ) ident "AS" type [ "(" expr ")" ] "=" expr nl
        """
        logging.debug("STMT-CONST")

        self._emitter.emit_line("const ")
        self.next_token()
        if self.check_token(TokenType.LET):
            self.let_stmt()
        elif self.check_token(TokenType.DIM):
            self.dim_stmt()
        else:
            self.abort(
                f"Invalid constant statement at {self._current_token.token_text}"
                f" {self._current_token.line_number}: {self._current_token.line_text}"
            )

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
                f" {self._current_token.line_number}: {self._current_token.line_text}"
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
        self._emitter.emit_line("if (")

        self._emitter.emit_line(self.expr())
        self.match(TokenType.THEN)
        self.nl()
        self._emitter.emit_line(") {")

        while not self.check_token(TokenType.ENDIF):
            if self.check_token(TokenType.ELIF):
                self.next_token()
                self._emitter.emit_line("} else if (")

                self._emitter.emit_line(self.expr())
                self._emitter.emit_line(") {")
                self.match(TokenType.THEN)
                self.nl()
            elif self.check_token(TokenType.ELSE):
                self.next_token()
                self.nl()
                self._emitter.emit_line("} else {")
            else:
                self.normal_stmt()

        self.match(TokenType.ENDIF)
        self.nl()
        self._emitter.emit_line("}")

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
        self._emitter.emit_line("switch (")
        self._emitter.emit_line(self.expr())
        self.nl()
        self._emitter.emit_line(") {")

        while not self.check_token(TokenType.ENDSWITCH):
            if self.check_token(TokenType.CASE):
                self.next_token()
                self._emitter.emit_line("case ")
                self._emitter.emit_line(self.expr())
                self.nl()
                self._emitter.emit_line(":")

                while not self.check_token(TokenType.CASE) and not self.check_token(
                    TokenType.DEFAULT
                ):
                    self.normal_stmt()
                    self._emitter.emit_line("break;")
            elif self.check_token(TokenType.DEFAULT):
                self.next_token()
                self.nl()
                self._emitter.emit_line("default:")

                while not self.check_token(TokenType.ENDSWITCH):
                    self.normal_stmt()
            else:
                self.abort(
                    f"Invalid switch statement at {self._current_token.token_text}"
                    f" {self._current_token.line_number}: {self._current_token.line_text}"
                )

        self.match(TokenType.ENDSWITCH)
        self.nl()
        self._emitter.emit_line("}")

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
            self.abort(f"Invalid loop statement at {self._current_token.token_text}"
                       f" {self._current_token.line_number}: {self._current_token.line_text}")

    def while_stmt(self) -> None:
        """
        "WHILE" expr nl { normal_stmt | declaration_stmt } "ENDWHILE" nl
        """
        logging.debug("STMT-WHILE")

        self.next_token()
        self._emitter.emit_line("while (")
        self._emitter.emit_line(self.expr())
        self.nl()
        self._emitter.emit_line(") {")

        while not self.check_token(TokenType.ENDWHILE):
            self.normal_or_declaration_stmt()

        self.match(TokenType.ENDWHILE)
        self.nl()
        self._emitter.emit_line("}")

    def do_stmt(self) -> None:
        """
        "DO" nl { normal_stmt | declaration_stmt } "ENDDO" [ "WHILE" expr ] nl
        """
        logging.debug("STMT-DO")

        self.next_token()
        self.nl()
        self._emitter.emit_line("do {")

        while not self.check_token(TokenType.ENDDO):
            if self.is_normal_stmt(self._current_token.token_type):
                self.normal_stmt()
            elif self.is_declaration_stmt(self._current_token.token_type):
                self.declaration_stmt()
            elif self._symbol_table.equals(
                self._current_token.token_text, TokenType.IDENT
            ):
                self.id_let_stmt()
            else:
                self.abort(
                    f"Invalid statement at {self._current_token.token_text}\n"
                    f" {self._current_token.line_number}: {self._current_token.line_text}"
                )

        self.match(TokenType.ENDDO)

        if self.check_token(TokenType.WHILE):
            self.next_token()
            self._emitter.emit_line("} while (")
            self._emitter.emit_line(self.expr())
            self._emitter.emit_line(");")
        else:
            self._emitter.emit_line("} while (false);")

        self.nl()

    def for_stmt(self) -> None:
        """
        "FOR" ident "=" expr "TO" expr [ "STEP" expr ] nl { normal_stmt | declaration_stmt } "ENDFOR" nl
        """
        logging.debug("STMT-FOR")

        self.next_token()
        tmp_ident = self._current_token.token_text
        self.match(TokenType.IDENT)
        self._emitter.emit_line(f"for ( int {tmp_ident} = ")

        self.match(TokenType.ASSIGN)
        self._emitter.emit_line(self.expr())
        self.match(TokenType.TO)
        self._emitter.emit_line(f"; {tmp_ident} <= ")
        self._emitter.emit_line(self.expr())

        if self.check_token(TokenType.STEP):
            self.next_token()
            self._emitter.emit_line(f"; {tmp_ident} += ")
            self._emitter.emit_line(self.expr())
        else:
            self._emitter.emit_line(f"; {tmp_ident}++")

        self._emitter.emit_line(") {")

        self.nl()

        while not self.check_token(TokenType.ENDFOR):
            self.normal_or_declaration_stmt()

        self.match(TokenType.ENDFOR)
        self.nl()
        self._emitter.emit_line("}")

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
            self.abort(f"Invalid io statement at {self._current_token.token_text}"
                       f" {self._current_token.line_number}: {self._current_token.line_text}")

    def input_stmt(self) -> None:
        """
        "INPUT" ident nl
        """
        logging.debug("STMT-INPUT")

        self.next_token()
        self._emitter.emit_line(f"cin >> {self._current_token.token_text};")
        self.match(TokenType.IDENT)
        self.nl()

    def print_stmt(self) -> None:
        """
        "PRINT" [color] (expr | string) nl
        """
        logging.debug("STMT-PRINT")

        self.next_token()
        tmp_color = None
        if self.is_color(self._current_token.token_type):
            tmp_color = self._current_token.token_text
            self.next_token()

        tmp_expr = self.expr()
        if tmp_expr is not None:
            if tmp_color is not None:
                color_map = {
                    "BLACK": "30",
                    "WHITE": "37",
                    "RED": "31",
                    "ORANGE": "33",
                    "YELLOW": "33",
                    "GREEN": "32",
                    "BLUE": "34",
                    "INDIGO": "36",
                    "VIOLET": "35",
                }
                self._emitter.emit_line(
                    f'cout << "\\033[1;{color_map[tmp_color]}m" << {tmp_expr} << "\\033[0m" << endl;'
                )
            else:
                self._emitter.emit_line(f"cout << {tmp_expr} << endl;")

        self.nl()

    def open_stmt(self) -> None:
        """
        "OPEN" string "FOR" ("INPUT" | "OUTPUT") "AS" ident nl
        """
        logging.debug("STMT-OPEN")

        self.next_token()
        tmp_file_name = self._current_token.token_text
        tmp_file_mode = ""
        self.match(TokenType.STRING)
        self.match(TokenType.FOR)

        if self.check_token(TokenType.INPUT):
            tmp_file_mode = "ios::in"
        elif self.check_token(TokenType.OUTPUT):
            tmp_file_mode = "ios::out"
        else:
            self.abort(
                f"Expected INPUT or OUTPUT, got {self._current_token.token_type}"
                f" {self._current_token.line_number}: {self._current_token.line_text}"
            )
        self.next_token()

        self.match(TokenType.AS)
        tmp_ident = self._current_token.token_text
        self._emitter.emit_line(
            f'fstream {tmp_ident}("{tmp_file_name}", {tmp_file_mode});'
        )
        self.match(TokenType.IDENT)
        self.nl()

    def close_stmt(self) -> None:
        """
        "CLOSE" ident nl
        """
        logging.debug("STMT-CLOSE")

        self.next_token()
        self._emitter.emit_line(f"{self._current_token.token_text}.close();")
        self.match(TokenType.IDENT)
        self.nl()

    def jump_stmt(self) -> None:
        """
        jump_stmt ->
            "BREAK" nl
            | "CONTINUE" nl
            | "RETURN" [ expr ] nl
        """
        logging.debug("STMT-JUMP")

        if self.check_token(TokenType.BREAK):
            self.break_stmt()
        elif self.check_token(TokenType.CONTINUE):
            self.continue_stmt()
        elif self.check_token(TokenType.RETURN):
            self.return_stmt()
        else:
            self.abort(f"Invalid jump statement at {self._current_token.token_text}"
                       f" {self._current_token.line_number}: {self._current_token.line_text}")

    def break_stmt(self) -> None:
        """
        "BREAK" nl
        """
        logging.debug("STMT-BREAK")

        self.next_token()
        self._emitter.emit_line("break;")
        self.nl()

    def continue_stmt(self) -> None:
        """
        "CONTINUE" nl
        """
        logging.debug("STMT-CONTINUE")

        self.next_token()
        self._emitter.emit_line("continue;")
        self.nl()

    def return_stmt(self) -> None:
        """
        "RETURN" nl
        | "RETURN" expr nl
        | "RETURN" function_call nl
        """
        logging.debug("STMT-RETURN")

        self.next_token()
        self._emitter.emit_line("return ")

        if not self.check_token(TokenType.NEWLINE):
            if self.check_token(TokenType.IDENT):
                tmp_line = self._symbol_table.lookup(
                    self._current_token.token_text
                ).line_text
                if (
                    tmp_line.find("CLASS") != -1
                    or tmp_line.find("FUNCTION") != -1
                    or tmp_line.find("STRUCT") != -1
                ):
                    tmp_func_call = self.function_call()
                    if tmp_func_call is not None:
                        self._emitter.emit_line(tmp_func_call)
                else:
                    self._emitter.emit_line(self.expr())

        self.nl()
        self._emitter.emit_line(";")

    def expr(self) -> Optional[str]:
        """
        expr -> logical_expr
        """
        logging.debug("EXPR")

        return self.logical_expr()

    def logical_expr(self) -> Optional[str]:
        """
        logical_expr -> logical_term {"OR" logical_term}
        """
        logging.debug("LOGICAL-EXPR")

        tmp_str = ""
        tmp_logical_term = self.logical_term()
        if tmp_logical_term is not None:
            tmp_str += tmp_logical_term

        while self.check_token(TokenType.OR):
            self.next_token()
            tmp_logical_term = self.logical_term()
            if tmp_logical_term is not None:
                tmp_str += f" || {tmp_logical_term}"

        return tmp_str

    def logical_term(self) -> Optional[str]:
        """
        logical_term -> logical_factor {"AND" logical_factor}
        """
        logging.debug("LOGICAL-TERM")

        tmp_str = ""
        tmp_logical_factor = self.logical_factor()
        if tmp_logical_factor is not None:
            tmp_str += tmp_logical_factor

        while self.check_token(TokenType.AND):
            self.next_token()
            tmp_logical_factor = self.logical_factor()
            if tmp_logical_factor is not None:
                tmp_str += f" && {tmp_logical_factor}"

        return tmp_str

    def logical_factor(self) -> Optional[str]:
        """
        logical_factor -> ["NOT"] comparison
        """
        logging.debug("LOGICAL-FACTOR")

        tmp_str = ""
        if self.check_token(TokenType.NOT):
            tmp_str += "!"
            self.next_token()

        tmp_comparison = self.comparison()
        if tmp_comparison is not None:
            tmp_str += tmp_comparison

        return tmp_str

    def comparison(self) -> Optional[str]:
        """
        arith_expr [("==" | "!=" | "<" | ">" | "<=" | ">=") arith_expr]
        """
        logging.debug("COMPARISON")

        tmp_str = ""
        tmp_arith_expr = self.arith_expr()
        if tmp_arith_expr is not None:
            tmp_str += tmp_arith_expr

        if self.is_cmp_op(self._current_token):
            if self._current_token.token_type == TokenType.GT:
                tmp_str += " > "
            elif self._current_token.token_type == TokenType.LT:
                tmp_str += " < "
            else:
                tmp_str += f" {self._current_token.token_text} "
            self.next_token()

            tmp_arith_expr = self.arith_expr()
            if tmp_arith_expr is not None:
                tmp_str += tmp_arith_expr

        return tmp_str

    def arith_expr(self) -> Optional[str]:
        """
        arith_expr -> arith_term {("+" | "-") arith_term}
        """
        logging.debug("ARITH-EXPR")

        tmp_str = ""
        tmp_arith_term = self.arith_term()
        if tmp_arith_term is not None:
            tmp_str += tmp_arith_term

        while self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
            tmp_str += f" {self._current_token.token_text} "
            self.next_token()

            tmp_arith_term = self.arith_term()
            if tmp_arith_term is not None:
                tmp_str += tmp_arith_term

        return tmp_str

    def arith_term(self) -> Optional[str]:
        """
        arith_term -> arith_factor {("*" | "/") arith_factor}
        """
        logging.debug("ARITH-TERM")

        tmp_str = ""
        tmp_arith_factor = self.arith_factor()
        if tmp_arith_factor is not None:
            tmp_str += tmp_arith_factor

        while self.check_token(TokenType.MULT) or self.check_token(TokenType.DIV):
            tmp_str += f" {self._current_token.token_text} "
            self.next_token()

            tmp_arith_factor = self.arith_factor()
            if tmp_arith_factor is not None:
                tmp_str += tmp_arith_factor

        return tmp_str

    def arith_factor(self) -> Optional[str]:
        """
        arith_factor -> ["+" | "-"] arith_base
        """
        logging.debug("ARITH-FACTOR")

        tmp_str = ""
        if self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
            tmp_str += self._current_token.token_text
            self.next_token()

        tmp_arith_base = self.arith_base()
        if tmp_arith_base is not None:
            tmp_str += tmp_arith_base
        return tmp_str

    def arith_base(self) -> Optional[str]:
        """
        arith_base -> "(" expr ")" | bool | int | float | string | ident
        """
        logging.debug("ARITH-BASE")

        if self.check_token(TokenType.LPAREN):
            self.next_token()
            expr_str = f"({self.expr()})"
            self.match(TokenType.RPAREN)
            return expr_str
        elif self.check_token(TokenType.STRING):
            result = f'"{self._current_token.token_text}"'
            self.next_token()
            return result
        elif (
            self.check_token(TokenType.BOOL)
            or self.check_token(TokenType.INT)
            or self.check_token(TokenType.FLOAT)
            or self.check_token(TokenType.TRUE)
            or self.check_token(TokenType.FALSE)
        ):
            result = self._current_token.token_text
            self.next_token()
            return result
        elif self.check_token(TokenType.IDENT):
            result = self._current_token.token_text
            self.next_token()
            return result

    def function_call(self) -> Optional[str]:
        """
        function_call -> ident "(" [expr {"," expr}] ")" nl
        """
        logging.debug("FUNCTION-CALL")

        # self._emitter.emit_line(f"{self._current_token.token_text}(")
        tmp_str = f"{self._current_token.token_text}("
        self.match(TokenType.IDENT)
        self.match(TokenType.LPAREN)

        if not self.check_token(TokenType.RPAREN):
            tmp_str += self.param_list()

        self.match(TokenType.RPAREN)
        self.nl()
        # self._emitter.emit_line(");")
        tmp_str += ");"

        return tmp_str

    def normal_or_declaration_stmt(self) -> None:
        """
        normal_or_declaration_stmt -> normal_stmt | declaration_stmt
        """
        if self.is_normal_stmt(self._current_token.token_type):
            self.normal_stmt()
        elif self.is_declaration_stmt(self._current_token.token_type):
            self.declaration_stmt()
        elif self._symbol_table.equals(self._current_token.token_text, TokenType.IDENT):
            tmp_line = self._symbol_table.get_line_text(self._current_token.token_text)
            if (
                tmp_line.find("CLASS") != -1
                or tmp_line.find("FUNCTION") != -1
                or tmp_line.find("STRUCT") != -1
            ):
                self._emitter.emit_line(self.function_call())
            else:
                self.id_let_stmt()
        else:
            self.abort(
                f"Invalid statement at {self._current_token.token_text}\n"
                f" {self._current_token.line_number}: {self._current_token.line_text}"
            )

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
            self.abort(
                f"Expected {token_type}, got {self._current_token.token_type}"
                f" {self._current_token.line_number}: {self._current_token.line_text}"
            )
        self.next_token()

    def next_token(self) -> None:
        """
        Advance the current token and the peek token
        """
        self._current_token = self._peek_token
        self._peek_token = self._lexer.get_token()

    def is_normal_stmt(self, token_type: TokenType) -> bool:
        """
        :param token_type: The token type to check
        :return: If the current token is a normal statement
        """
        return token_type in self._normal_tokens_map.keys()

    def is_declaration_stmt(self, token_type: TokenType) -> bool:
        """
        :param token_type: The token type to check
        :return: If the current token is a declaration statement
        """
        return token_type in self._declaration_tokens

    def is_type(self, token_type: TokenType) -> bool:
        """
        type -> "BOOL" | "INT" | "FLOAT" | "STRING" | ident

        :param token_type: The token type to check
        :return: If the current token is a type
        """
        return token_type in self._type_tokens

    def is_color(self, token_type: TokenType) -> bool:
        """
        :param token_type: The token type to check
        :return: If the current token is a color
        """
        return token_type in self._color_tokens

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
