from dataclasses import dataclass
from pprint import pprint
from typing import List

from myhdl import intbv

from compiler.memory import linker, pack_binary
from compiler.translator.utils.models import ForthCode
from isa.model.instructions import Instr
from src.compiler.translator.main import translate_forth


@dataclass
class ForthCompilationArtifact:
    source: str
    translated: ForthCode
    flat: List[int | Instr]
    mem_words: List[intbv]
    mem_binary: bytearray


def compile_forth(text: str) -> ForthCompilationArtifact:
    code = translate_forth(text)
    flat = linker(code)
    words, binary = pack_binary(flat)
    return ForthCompilationArtifact(
        text, code, flat, words, binary
    )
