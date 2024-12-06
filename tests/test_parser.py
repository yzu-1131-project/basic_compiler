# import logging
# import io
# import sys
# import unittest
#
# from basic_compiler.basic_lex import Lexer
# from basic_compiler.basic_parser import Parser
#
#
# class MyTestCase(unittest.TestCase):
#     @staticmethod
#     def remove_logging_handlers(log_msg: str) -> str:
#         if log_msg.startswith("DEBUG:root:"):
#             return log_msg[len("DEBUG:root:") :]
#         return log_msg
#
#     def helper(self, source: str, exp_ans: list):
#         log_stream = io.StringIO()
#         for handler in logging.root.handlers[:]:
#             logging.root.removeHandler(handler)
#         logging.basicConfig(stream=log_stream, level=logging.DEBUG)
#         lexer = Lexer(source)
#         parser = Parser(lexer)
#         parser.program()
#
#         # self.assertEqual(log_stream.getvalue(), exp_ans)
#         # for line in log_stream.getvalue().splitlines():
#         #     self.assertEqual(self.remove_logging_handlers(line), exp_ans)
#         self.assertEqual(len(log_stream.getvalue().splitlines()), len(exp_ans))
#         for line, exp in zip(log_stream.getvalue().splitlines(), exp_ans):
#             self.assertEqual(self.remove_logging_handlers(line), exp)
#
#     def test_stmt(self):
#         test_cases = [
#             (
#                 "PRINT 1\n",
#                 [
#                     "PROGRAM",
#                     "STMT",
#                     "STMT-NORMAL",
#                     "STMT-PRINT",
#                     "EXPR",
#                     "LOGICAL-EXPR",
#                     "LOGICAL-TERM",
#                     "LOGICAL-FACTOR",
#                     "COMPARISON",
#                     "ARITH-EXPR",
#                     "ARITH-TERM",
#                     "ARITH-FACTOR",
#                     "ARITH-BASE",
#                     "NL",
#                 ],
#             ),
#             # Add more test cases here if needed
#         ]
#         for source, exp_ans in test_cases:
#             with self.subTest(source=source, exp_ans=exp_ans):
#                 self.helper(source, exp_ans)
#
#
# if __name__ == "__main__":
#     unittest.main()
