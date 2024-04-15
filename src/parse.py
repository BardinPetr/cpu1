from enum import IntEnum
from functools import reduce
from pprint import pprint
from typing import List, Dict, Optional

from lark import Lark, Transformer, v_args, Token

from machine import arch
from machine.mc.mc import MCInstruction, MCInstructionJump
from machine.utils.enums import CtrlEnum


def merge_dicts(x: List[Dict]) -> Dict:
    return reduce(lambda acc, i: {**acc, **i}, x, {})


class Location:

    def __init__(self, name: str = None, pos: Optional[int] = None):
        self.name = name
        self.pos = pos

    def __repr__(self):
        return f"L<{self.name}@{self.pos if self.pos is not None else 'UNDEF'}>"

    def __str__(self):
        return self.__repr__()


class TypeTransformer(Transformer):

    def LOC(self, val):
        vals = str(val)
        if vals.startswith("0x"):
            return Location(pos=int(val, 16))
        if vals.isdecimal() or vals.startswith("-"):
            return Location(pos=int(val))
        return self.ID(val)

    def ID(self, val):
        return Location(name=str(val))

    HEXNUMBER = lambda self, x: int(x, 16)
    BINNUMBER = bool
    NUMBER = int


"""Here we are translating asm each line into arguments of MCInstruction """


class ControlInstructionTransformer(Transformer):
    instr_exec = lambda self, x: MCInstruction(**merge_dicts(x))

    """ALU control section"""
    exec_alu = lambda self, x: merge_dicts(x)
    alu_ctrl = lambda self, x: dict(alu_ctrl=arch.ALUCtrl.encode_from_names(x))
    alu_op_a = lambda self, x: dict(bus_a_in_ctrl=x[0][0], alu_port_a_ctrl=x[0][1])
    alu_op_b = lambda self, x: dict(bus_b_in_ctrl=x[0][0], alu_port_b_ctrl=x[0][1])
    alu_op_c = lambda self, x: dict(bus_c_out_ctrl=arch.BusOutCtrl.encode_from_names(x))

    def alu_op(self, val: List[Token]):
        return arch.BusInCtrl.encode_from_names(val[0:1]), \
            arch.ALUPortCtrl.encode_from_names(val[1:])

    def exec_alu_flags(self, vals: List[Token]):
        enum = arch.ALUFlagCtrl.encode_from_names(
            ["SET" + i.value for i in vals]
        )
        return dict(alu_flag_ctrl=enum)

    """IO control"""
    exec_mem = lambda self, x: dict(mem_ctrl=arch.MemCtrl.WR)


class JumpInstructionTransformer(Transformer):
    instr_jump = lambda self, x: MCInstructionJump(**merge_dicts(x))

    def jump_cmp(self, val: List[bool]):
        return dict(jmp_cmp_val=val[0])

    def jump_cmp_pos(self, val: List[int]):
        return dict(jmp_cmp_bit=val[0])

    def jump_target(self, val: List[Location]):
        return dict(jmp_target=val[0].pos)


class CodeTransformer(Transformer):

    def line(self, line: Token):
        return line[0]


class BinaryTransformer(Transformer):

    def start(self, lines: List[MCInstruction]):
        return [i.compile() for i in lines]


txt = """
(RF_IP(NOT) PASSA IGNORE(INC)) -> PS, set(Z N C V) store;
(RF_IP PASSA IGNORE(INC NOT)) -> PS, set(Z N C V) store;
(RF_IP PASSA) -> PS set(Z,N,C,V) store;
(PASSA) -> PS set(V);
(PASSA) set(V);
(ZERO);
jump 0x3324;
JmP 324;
jump label;
if (RF_IP PASSA)[10] == 0 jump label;
"""

grammar = open("uasm.lark", "r").read()
l = Lark(grammar)
ast = l.parse(txt)
ast = TypeTransformer().transform(ast)
ast = ControlInstructionTransformer().transform(ast)
ast = JumpInstructionTransformer().transform(ast)

try:
    print(ast.pretty())
except:
    pprint(ast)

exit(0)
code = CodeTransformer().transform(ast)
out = BinaryTransformer().transform(code)
print(code.pretty())
print(out)
