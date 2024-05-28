from dataclasses import dataclass
from functools import reduce
from typing import List, Tuple

from myhdl import intbv

from compiler.utils.models import ForthCode
from isa.model.instructions import Instr, IPRelImmInstr, AbsImmInstr
from machine.config import INSTR_BITS, INSTR_BYTE
from machine.utils.hdl import SINT16_MIN, SINT16_MAX


@dataclass
class ForthLinkResults:
    mem: List[int | Instr]
    instructions: List[Instr]
    reloc_vars: int
    reloc_funcs: int


def linker(source: ForthCode) -> ForthLinkResults:
    """
    Generates memory layout from variables, and flattened functions and main code.
    Translates relative addresses to absolute.

    Structure:
        - main code (entrypoint is addr=0)
        - functions
        - variables

    """
    funcs_flat = reduce(lambda acc, i: acc + i.code, source.functions, [])

    root_size = len(source.code)
    function_relocate_pos = root_size
    variable_relocate_pos = function_relocate_pos + len(funcs_flat)

    code = []
    for cur_pos, instr in enumerate(source.code + funcs_flat):
        if isinstance(instr, IPRelImmInstr):
            # fix function calls
            instr = instr.relocate(cur_pos, base=function_relocate_pos)
        elif isinstance(instr, AbsImmInstr):
            # fix variable references
            instr = instr.relocate(base=variable_relocate_pos)

        if not (SINT16_MIN <= instr.imm <= SINT16_MAX):
            raise ValueError("Immediate value not fits 16bit signed field")

        code.append(instr)

    out_instr = code[:]

    # allocate variables
    for name, var in source.variables.items():
        contents = var.init_value or []
        code += contents + [0] * (var.size_slots - len(contents))

    return ForthLinkResults(
        mem=code,
        instructions=out_instr,
        reloc_vars=variable_relocate_pos,
        reloc_funcs=function_relocate_pos
    )


def pack_binary(source: List[int | Instr]) -> Tuple[List[intbv], bytearray]:
    """
    Compiles flattened instruction and data list
    :return: representation as list of INSTR_BITS words and as byte array packed as 32 little-endian numbers
    """
    words = [
        intbv(i)[INSTR_BITS:] if isinstance(i, int) else i.pack()
        for i in source
    ]
    as_bytes = reduce(
        lambda acc, i: acc + int(i).to_bytes(length=INSTR_BYTE, byteorder='little'),
        words, bytearray()
    )
    return words, as_bytes


def unpack_binary(source: bytes) -> List[intbv]:
    """Unpacks code from byte array to 32bit values list"""
    if len(source) % INSTR_BYTE != 0:
        raise ValueError("Padding invalid")
    return [
        intbv(int.from_bytes(source[i:i + INSTR_BYTE], byteorder='little'))[INSTR_BITS:]
        for i in range(0, len(source), INSTR_BYTE)
    ]
