from dataclasses import dataclass
from functools import reduce
from typing import List, Dict, Optional

from lark import Lark, Transformer, v_args, Token, Tree
from machine import arch
from machine.mc.mc import MCInstruction, MCInstructionJump

from mcasm.grammar import load_grammar


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


class LocationResolver(Transformer):

    @v_args(tree=True)
    def start(self, lines: Tree):
        labels = dict()
        for pos, line in enumerate(lines.children):
            label = next(line.find_data('label'), None)
            if label is not None:
                loc: Location = label.children[0]
                labels[loc.name] = pos
                loc.pos = pos

        for i in lines.find_data("jump_target"):
            loc: Location = i.children[0]
            if loc.pos is not None: continue
            if loc.name not in labels:
                raise RuntimeError(f"Unable to resolve location {loc}")

            loc.pos = labels[loc.name]

        return lines


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

    def exec_stack(self, vals: List[Token]):
        stack_name = vals[1]
        stack_cmd = arch.StackCtrl.encode_from_names([vals[0].upper()])
        return {
            f"stack_{stack_name.lower()}_ctrl": stack_cmd,
            "bus_c_out_ctrl":                   arch.BusOutCtrl.encode_from_names([f"{stack_name.upper()}_TOS"])
        }

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


@dataclass
class CompiledMC:
    commands: List[MCInstruction]
    labels: Dict[str, int]

    def __post_init__(self):
        self.compiled = [i.compile() for i in self.commands]


class CodeTransformer(Transformer):

    def line(self, line: List[Token]):
        return line[-1]

    def start(self, lines):
        return CompiledMC(
            lines,
            {}
        )


class MCASMCompiler:

    def __init__(self):
        self._lark = Lark(load_grammar())
        self._transform = (
                TypeTransformer() *
                LocationResolver() *
                ControlInstructionTransformer() *
                JumpInstructionTransformer() *
                CodeTransformer()
        )

    def compile(self, text: str) -> CompiledMC:
        ast = self._lark.parse(text)
        ast = self._transform.transform(ast)
        return ast


def mc_compile(text: str) -> CompiledMC:
    comp = MCASMCompiler()
    return comp.compile(text)
