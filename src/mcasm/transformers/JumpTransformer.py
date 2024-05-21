from typing import List

from lark import Transformer

from machine.mc import MCInstructionJump
from mcasm.utils import merge_dicts, Location


class JumpInstructionTransformer(Transformer):
    instr_jump = lambda self, x: MCInstructionJump(**merge_dicts(x))

    def jump_cmp(self, val: List[bool]):
        return dict(jmp_cmp_val=val[0])

    def jump_cmp_pos(self, val: List[int]):
        return dict(jmp_cmp_bit=val[0])

    def jump_target(self, val: List[Location]):
        return dict(jmp_target=val[0].pos)
