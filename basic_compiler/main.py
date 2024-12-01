from basic_compiler.basic_lex import Lexer
from basic_compiler.basic_parser import Parser

import sys
import logging


def main():
    print("=====Basic Compiler=====")
    print("|    COPYRIGHT 2024    |")
    print("|    Version 1.0.0     |")
    print("|    Author: S.C. Lu   |")
    print("|  All rights reserved |")
    print("========================")

    if len(sys.argv) < 2:
        print("Usage: python -m basic_compiler <filename>")
        return

    filename = sys.argv[1]
    with open(filename, "r") as f:
        source = f.read()

    # Set up logging, format include the source file name and line number
    logging.basicConfig(
        level=logging.DEBUG, format="{%(filename)s:%(lineno)d} %(message)s"
    )

    lexer = Lexer(source)
    parser = Parser(lexer)

    parser.program()
    print("Parsing completed.")


if __name__ == "__main__":
    main()
