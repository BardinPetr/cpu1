#!/usr/bin/env python
import json
from argparse import ArgumentParser

from parse import MCASMCompiler, CompiledMC


def mc_compile(text: str) -> CompiledMC:
    comp = MCASMCompiler()
    return comp.compile(text)


if __name__ == "__main__":
    parser = ArgumentParser(description='Microcode ASM parser & compiler')
    parser.add_argument(
        "input_file",
        type=str,
        help="ASM file path"
    )
    parser.add_argument(
        "-p", "--parse",
        action="store_true",
        help="Only parse and print source microcommands as Python objects"
    )
    parser.add_argument(
        "-b", "--bin",
        action="store_true",
        help="Compile print binary encoded instrunctions"
    )
    parser.add_argument(
        "-j", "--json",
        type=str,
        help="Compile and output binary to file"
    )

    args = parser.parse_args()

    text = open(args.input_file, "r").read()
    res = mc_compile(text)

    if args.parse:
        for i, c in enumerate(res.commands):
            print(f"{i:4}: {c}")

    if args.json:
        with open(args.json, "w") as f:
            json.dump(res.compiled, f)

    if args.bin:
        for i in res.compiled:
            print(f"{i:064b}")