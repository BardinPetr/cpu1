#!/usr/bin/env python

from argparse import ArgumentParser
from dataclasses import dataclass
from typing import List

from myhdl import intbv

from compiler.memory import linker, pack_binary, ForthLinkResults
from compiler.translator.utils.models import ForthCode
from isa.model.instructions import Instr
from machine.config import INSTR_BYTE
from src.compiler.translator.main import translate_forth


@dataclass
class ForthCompilationArtifact:
    source: str
    translated: ForthCode
    flat: List[int | Instr]
    linker_output: ForthLinkResults
    mem_words: List[intbv]
    mem_binary: bytearray


def compile_forth(text: str) -> ForthCompilationArtifact:
    code = translate_forth(text)
    link_res = linker(code)
    words, binary = pack_binary(link_res.mem)
    return ForthCompilationArtifact(
        text, code, link_res.mem, link_res, words, binary
    )


if __name__ == "__main__":
    parser = ArgumentParser(description='Forth parser & compiler')
    parser.add_argument(
        "input_file",
        type=str,
        help="Forth file path"
    )
    parser.add_argument(
        "output_file",
        type=str,
        help="Output file for compiled binary"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print out detailed information on compilation process and precompiled non-binary code"
    )

    args = parser.parse_args()

    text = open(args.input_file, "r").read()

    res = compile_forth(text)

    with open(args.output_file, "wb") as f:
        f.write(res.mem_binary)

    if args.verbose:
        loc = text.count('\n')
        icnt = len(res.linker_output.instructions)
        print(f"""
        LoC: {loc}
        Compiled binary size: {len(res.mem_binary)} bytes
        Compiled instructions: {icnt} count, {icnt * INSTR_BYTE} bytes 
        """)

        print("-" * 20)
        print("MEM")
        print("\n".join([
            f"{pos:03x}h: " + (f"{i:08x}h" if isinstance(i, int) else str(i))
            for pos, i in enumerate(res.flat)
        ]))

        print("-" * 20)
        print("VARS")
        print("\n".join([
            f"#{pos:<2d}: '{i.name}' at {i.loc + res.linker_output.reloc_vars} of {i.size_slots} slots"
            for pos, i in enumerate(res.translated.variables.values())
        ]))
