import sys
import logging
from basic_compiler.basic_argparser import parse_args
from basic_compiler.basic_lex import Lexer
from basic_compiler.basic_parser import Parser
from basic_compiler.basic_emitter import Emitter
from basic_compiler.basic_exceptions import (
    LexerError,
    TokenError,
    ParserError,
    SymbolTableError,
)


def main():
    args = parse_args(sys.argv[1:])
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO, format="%(message)s"
    )

    header = (
        "=====Basic Compiler=====\n"
        "|    COPYRIGHT 2024    |\n"
        "|    Version 1.0.0     |\n"
        "|    Author: S.C. Lu   |\n"
        "|  All rights reserved |\n"
        "========================"
    )
    logging.info(header)

    # try:
    with open(args.input, "r") as f:
        source = f.readlines()

    try:
        lexer = Lexer(source)
        emitter = Emitter(args)
        parser = Parser(lexer, emitter)
        parser.program()
    except (LexerError, TokenError, ParserError, SymbolTableError) as e:
        logging.error(f"Compilation error:\n {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error:\n {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
