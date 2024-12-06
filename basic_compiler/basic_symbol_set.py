from basic_compiler.basic_token import Token, TokenType
from basic_compiler.basic_exceptions import SymbolTableError
from typing import Optional


class SymbolTable:
    def __init__(self):
        self._symbols = {}

    def insert(self, token: Token) -> None:
        name = token.token_text
        if name in self._symbols:
            raise SymbolTableError(
                f"{token.line_number + 1}: {token.line_text}\nVariable '{name}' already declared."
            )
        self._symbols[name] = token

    def lookup(self, name: str) -> Token:
        if name not in self._symbols:
            raise SymbolTableError(f"Variable '{name}' not declared.")
        return self._symbols[name]

    def find(self, name: str) -> Optional[Token]:
        return self._symbols.get(name)

    def equals(self, name: str, token_type: TokenType) -> bool:
        token = self._symbols.get(name)
        return token.token_type == token_type if token else False

    def get_line_text(self, name: str) -> Optional[str]:
        token = self._symbols.get(name)
        return token.line_text if token else None

    def __repr__(self):
        return repr(self._symbols)
