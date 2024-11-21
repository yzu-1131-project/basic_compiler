import unittest

from basic_compiler.lex import Lexer
from basic_compiler.token import TokenType


class TestLexer(unittest.TestCase):
    def check_lexer(self, source: str, exp_ans: list):
        lexer = Lexer(source)
        token = lexer.get_token()
        count_ans = 0

        while token.token_type != TokenType.EOF and count_ans < len(exp_ans):
            self.assertEqual(token.token_type, exp_ans[count_ans])
            count_ans += 1
            token = lexer.get_token()

        # Check the EOF token
        self.assertEqual(token.token_type, TokenType.EOF)
        self.assertEqual(count_ans, len(exp_ans) - 1)

    def check_lex_error(self, source: str, exp_err: str):
        lexer = Lexer(source)

        with self.assertRaises(Exception) as context:
            lexer.get_token()

        self.assertTrue(exp_err in str(context.exception))

    def test_lex(self):
        self.check_lexer(
            "LET x = 5",
            [
                TokenType.LET,
                TokenType.IDENT,
                TokenType.ASSIGN,
                TokenType.INT,
                TokenType.EOF,
            ],
        )

        self.check_lexer(
            """IF x > 5 THEN
            PRINT x
            ELSE
            PRINT 5.5""",
            [
                TokenType.IF,
                TokenType.IDENT,
                TokenType.GT,
                TokenType.INT,
                TokenType.THEN,
                TokenType.NEWLINE,
                TokenType.PRINT,
                TokenType.IDENT,
                TokenType.NEWLINE,
                TokenType.ELSE,
                TokenType.NEWLINE,
                TokenType.PRINT,
                TokenType.FLOAT,
                TokenType.EOF,
            ],
        )

        self.check_lexer("# This is comment", [TokenType.EOF])

        self.check_lexer(
            """LET x = 2 ^ 5 - 3 * 7
        CONST y = 10 % 3 + 3 / x
        DIM z AS STRING""",
            [
                TokenType.LET,
                TokenType.IDENT,
                TokenType.ASSIGN,
                TokenType.INT,
                TokenType.POW,
                TokenType.INT,
                TokenType.MINUS,
                TokenType.INT,
                TokenType.MULT,
                TokenType.INT,
                TokenType.NEWLINE,
                TokenType.CONST,
                TokenType.IDENT,
                TokenType.ASSIGN,
                TokenType.INT,
                TokenType.MOD,
                TokenType.INT,
                TokenType.PLUS,
                TokenType.INT,
                TokenType.DIV,
                TokenType.IDENT,
                TokenType.NEWLINE,
                TokenType.DIM,
                TokenType.IDENT,
                TokenType.AS,
                TokenType.STRING,
                TokenType.EOF,
            ],
        )

        self.check_lexer(
            "{[()]}:;,",
            [
                TokenType.LCBRACKET,
                TokenType.LSBRACKET,
                TokenType.LPAREN,
                TokenType.RPAREN,
                TokenType.RSBRACKET,
                TokenType.RCBRACKET,
                TokenType.COLON,
                TokenType.SEMICOLON,
                TokenType.COMMA,
                TokenType.EOF,
            ],
        )

        self.check_lexer(
            "a < 5, b <= 10, c > 7, d >= 1, e == 5, f != 1",
            [
                TokenType.IDENT,
                TokenType.LT,
                TokenType.INT,
                TokenType.COMMA,
                TokenType.IDENT,
                TokenType.LTEQ,
                TokenType.INT,
                TokenType.COMMA,
                TokenType.IDENT,
                TokenType.GT,
                TokenType.INT,
                TokenType.COMMA,
                TokenType.IDENT,
                TokenType.GTEQ,
                TokenType.INT,
                TokenType.COMMA,
                TokenType.IDENT,
                TokenType.EQ,
                TokenType.INT,
                TokenType.COMMA,
                TokenType.IDENT,
                TokenType.NOTEQ,
                TokenType.INT,
                TokenType.EOF,
            ],
        )

        # This is PRINT "Hello \"John\""
        self.check_lexer(
            'PRINT "Hello \\"John\\""',
            [TokenType.PRINT, TokenType.STRING, TokenType.EOF],
        )

    def test_lex_error(self):
        self.check_lex_error("!2", "Expected !=, got !2")
        self.check_lex_error("2.", 'Number must have at least one digit after "."')
        self.check_lex_error("2.2.2", 'Number must have only one "."')
