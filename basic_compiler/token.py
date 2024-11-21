import enum


class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    BOOL = 1
    INT = 2
    FLOAT = 3
    IDENT = 4
    STRING = 5
    # Keywords.
    LABEL = 101
    GOTO = 102
    PRINT = 103
    INPUT = 104
    LET = 105
    CONST = 106
    DIM = 107
    AS = 108
    IF = 109
    THEN = 110
    ELIF = 111
    ELSE = 112
    ENDIF = 113
    SWITCH = 114
    CASE = 115
    DEFAULT = 116
    SEND = 117
    WHILE = 118
    REPEAT = 119
    WEND = 120
    FOR = 121
    TO = 122
    STEP = 123
    # Operators.
    ASSIGN = 201
    PLUS = 202
    MINUS = 203
    MULT = 204
    DIV = 205
    MOD = 206
    POW = 207
    AND = 208
    OR = 209
    NOT = 210
    TRUE = 211
    FALSE = 212
    # Comparison operators.
    EQ = 251
    NOTEQ = 252
    LT = 253
    LTEQ = 254
    GT = 255
    GTEQ = 256
    # Delimiters.
    COMMA = 301
    COLON = 302
    SEMICOLON = 303
    LPAREN = 304
    RPAREN = 305
    LSBRACKET = 306
    RSBRACKET = 307
    LCBRACKET = 308
    RCBRACKET = 309
    # Colors.
    RED = 401
    ORANGE = 402
    YELLOW = 403
    GREEN = 404
    BLUE = 405
    INDIGO = 406
    VIOLET = 407


class Token:
    def __init__(self, token_text: str, token_type: TokenType):
        self._token_text = token_text
        self._token_type = token_type

    @staticmethod
    def check_if_keyword(token_text: str) -> TokenType | None:
        for token_type in TokenType:
            if token_type.name == token_text:
                return token_type

        return None

    @property
    def token_type(self):
        return self._token_type
