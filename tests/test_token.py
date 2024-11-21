import unittest

from basic_compiler.token import Token, TokenType

class test_token(unittest.TestCase):
    def test_keyword(self):
        token1 = Token('IF', TokenType.IF)
        token2 = Token('x', TokenType.IDENT)
        token3 = Token('3', TokenType.INT)
        token4 = Token('3.14', TokenType.FLOAT)

        self.assertEqual(token1.token_type, TokenType.IF)
        self.assertEqual(token2.token_type, TokenType.IDENT)
        self.assertEqual(token3.token_type, TokenType.INT)
        self.assertEqual(token4.token_type, TokenType.FLOAT)