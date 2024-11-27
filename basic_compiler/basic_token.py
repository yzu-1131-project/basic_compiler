import enum

class TokenType(enum.Enum):
    # Special tokens
    EOF = -1
    NEWLINE = 0

    # Literals
    IDENT = 1
    BOOL = 2
    TRUE = 3
    FALSE = 4
    INT = 5
    FLOAT = 6
    STRING = 7

    # Operators
    ASSIGN = 100
    PLUS = 101
    MINUS = 102
    MULT = 103
    DIV = 104
    MOD = 105
    POW = 106
    AND = 107
    OR = 108
    NOT = 109
    EQ = 110
    NOTEQ = 111
    LT = 112
    LTEQ = 113
    GT = 114
    GTEQ = 115

    # Punctuation
    COMMA = 200
    COLON = 201
    SEMICOLON = 202
    LPAREN = 203
    RPAREN = 204
    LSBRACKET = 205
    RSBRACKET = 206
    LCBRACKET = 207
    RCBRACKET = 208

    # Keywords
    LET = 300
    CONST = 301
    DIM = 302
    AS = 303
    IF = 304
    THEN = 305
    ELIF = 306
    ELSE = 307
    ENDIF = 308
    SWITCH = 309
    CASE = 310
    DEFAULT = 311
    ENDSWITCH = 312
    WHILE = 313
    ENDWHILE = 314
    DO = 315
    ENDDO = 316
    FOR = 317
    TO = 318
    STEP = 319
    ENDFOR = 320
    BREAK = 321
    CONTINUE = 322
    RETURN = 323
    GOTO = 324
    LABEL = 325
    PRINT = 326
    INPUT = 327
    OUTPUT = 328
    OPEN = 329
    CLOSE = 330
    CLASS = 331
    ENDCLASS = 332
    FUNCTION = 333
    ENDFUNCTION = 334
    PUBLIC = 335
    PRIVATE = 336
    STRUCT = 337
    ENDSTRUCT = 338

    # Colors
    BLACK = 400
    WHITE = 401
    RED = 402
    ORANGE = 403
    YELLOW = 404
    GREEN = 405
    BLUE = 406
    INDIGO = 407
    VIOLET = 408


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
    def token_text(self):
        return self._token_text

    @property
    def token_type(self):
        return self._token_type
