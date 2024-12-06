from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional


class TokenType(Enum):
    # Special tokens
    EOF = auto()
    NEWLINE = auto()

    # Literals
    IDENT = auto()
    BOOL = auto()
    TRUE = auto()
    FALSE = auto()
    INT = auto()
    FLOAT = auto()
    STRING = auto()

    # Operators
    ASSIGN = auto()
    PLUS = auto()
    MINUS = auto()
    MULT = auto()
    DIV = auto()
    MOD = auto()
    POW = auto()
    AND = auto()
    OR = auto()
    NOT = auto()
    EQ = auto()
    NOTEQ = auto()
    LT = auto()
    LTEQ = auto()
    GT = auto()
    GTEQ = auto()

    # Punctuation
    COMMA = auto()
    COLON = auto()
    SEMICOLON = auto()
    LPAREN = auto()
    RPAREN = auto()
    LSBRACKET = auto()
    RSBRACKET = auto()
    LCBRACKET = auto()
    RCBRACKET = auto()

    # Keywords
    LET = auto()
    CONST = auto()
    DIM = auto()
    AS = auto()
    IF = auto()
    THEN = auto()
    ELIF = auto()
    ELSE = auto()
    ENDIF = auto()
    SWITCH = auto()
    CASE = auto()
    DEFAULT = auto()
    ENDSWITCH = auto()
    WHILE = auto()
    ENDWHILE = auto()
    DO = auto()
    ENDDO = auto()
    FOR = auto()
    TO = auto()
    STEP = auto()
    ENDFOR = auto()
    BREAK = auto()
    CONTINUE = auto()
    RETURN = auto()
    PRINT = auto()
    INPUT = auto()
    OUTPUT = auto()
    OPEN = auto()
    CLOSE = auto()
    CLASS = auto()
    ENDCLASS = auto()
    FUNCTION = auto()
    ENDFUNCTION = auto()
    PUBLIC = auto()
    PRIVATE = auto()
    STRUCT = auto()
    ENDSTRUCT = auto()

    # Colors
    BLACK = auto()
    WHITE = auto()
    RED = auto()
    ORANGE = auto()
    YELLOW = auto()
    GREEN = auto()
    BLUE = auto()
    INDIGO = auto()
    VIOLET = auto()


# Set of keyword names for quick lookup
KEYWORDS = {token.name for token in TokenType if token.name.isupper()}


@dataclass
class Token:
    token_text: str
    token_type: TokenType
    line_number: int = 0
    line_text: str = ""

    @staticmethod
    def check_if_keyword(token_text: str) -> Optional[TokenType]:
        token_upper = token_text.upper()
        if token_upper in KEYWORDS:
            return TokenType[token_upper]
        return None
