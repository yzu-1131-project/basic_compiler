import subprocess

from basic_compiler.basic_argparser import parse_args


class Emitter:
    def __init__(self, args: parse_args):
        self._args = args
        self._header = (
            "#include <iostream>\n"
            "#include <string>\n"
            "#include <fstream>\n"
            "using namespace std;\n\n"
        )
        self._code = ""

    def emit(self, code):
        self._code += code

    def emit_line(self, code):
        if code is not None:
            self._code += code + "\n"

    def emit_header(self, code):
        self._header += code + "\n"

    def write_file(self):
        with open(self._args.output, "w") as output_file:
            output_file.write(self._header + self._code)

        if self._args.format:
            subprocess.run(["clang-format", "-i", self._args.output])

        if self._args.compile:
            subprocess.run(
                [
                    "g++",
                    f"{self._args.output}",
                    "-o",
                    self._args.output.replace(".cpp", ""),
                ]
            )

        if self._args.execute:
            subprocess.run([f"./{self._args.output.replace('.cpp', '')}"], shell=True)
