import argparse


def parse_args(argv: list):
    parser = argparse.ArgumentParser(
        description="Compiler for a basic language",
        epilog="For more information, visit the documentation.",
    )
    parser.add_argument(
        "-i", "--input", help="The source file to compile", required=True
    )
    parser.add_argument("-o", "--output", help="The output file", default="out.cpp")
    parser.add_argument(
        "-O",
        "--opt",
        help="Optimization level (0-3)",
        type=int,
        choices=range(0, 4),
        default=0,
    )
    parser.add_argument("--compile", help="Compile the output", action="store_true")
    parser.add_argument("--execute", help="Execute the output", action="store_true")
    parser.add_argument("--format", help="Format the output", action="store_true")
    parser.add_argument(
        "-v", "--verbose", help="Increase output verbosity", action="store_true"
    )
    parser.add_argument(
        "-V", "--version", action="version", version="basic_compiler 1.0.0"
    )

    return parser.parse_args(argv)
