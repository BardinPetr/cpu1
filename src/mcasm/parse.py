from dataclasses import dataclass
from functools import reduce
from typing import List, Dict

from lark import Lark, Transformer, v_args, Token, Tree

from src.machine import arch
from src.machine.mc.mc import MCInstructionExec, MCInstructionJump, MCInstruction
from src.mcasm.grammar import load_grammar
from src.mcasm.utils import gen_jump, Location, merge_dicts, gen_line, gen_tree


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

    def block(self, val: List[Token]):
        return val

    BINARY = lambda self, x: int(x, 2)
    HEXNUMBER = lambda self, x: int(x, 16)
    BINNUMBER = lambda self, x: int(x, 2)
    NUMBER = int


class LocationResolver(Transformer):

    def __init__(self):
        super().__init__()
        self.labels: Dict[str, int] = {}

    @v_args(tree=True)
    def start(self, lines: Tree):
        pos = 0

        lines.children = lines.children[0]  # remove top block_content

        for line in lines.children:
            label = next(line.find_data('label'), None)
            if label is not None:
                loc: Location = label.children[0]
                self.labels[loc.name] = pos
                loc.pos = pos
            else:
                pos += 1

        for i in lines.find_data("jump_target"):
            loc: Location = i.children[0]
            if loc.pos is not None: continue
            if loc.name not in self.labels:
                raise RuntimeError(f"Unable to resolve location {loc}")

            loc.pos = self.labels[loc.name]

        lines.children = [i for i in lines.children if i.children[0].data != 'label']
        return lines


class ControlInstructionTransformer(Transformer):
    """Here we are translating asm each line into arguments of MCInstruction """
    instr_exec = lambda self, x: MCInstructionExec(**merge_dicts(x))

    """ALU control section"""
    exec_alu_compute = lambda self, x: merge_dicts(x)
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
            "bus_c_out_ctrl":                   arch.BusOutCtrl.encode_from_names([f"{stack_name.upper()}S"])
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


class LangTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self._if_id = 0

    def block_content(self, tree: List[Tree]):
        return reduce(
            lambda acc, cur: acc + (line.children if (line := cur.children[0]).data == 'block' else [cur]),
            tree, []
        )

    @v_args(inline=True)
    def if_check(self, alu, pos, cmp):
        return dict(alu=alu, cmp_pos=pos, cmp_val=cmp)

    @v_args(inline=True)
    def instr_if(self, check: Dict, true_branch_block, false_branch_block):
        base_label = f"__if_{self._if_id}"
        true_label = Location(name=f"{base_label}_on_true")
        end_loc = Location(name=f"{base_label}_end")
        self._if_id += 1

        jump_instr = gen_jump(
            **check,
            target=true_label  # jump if TRUE!
        )
        false_exit_instr = gen_jump(
            target=end_loc
        )
        return gen_tree(
            "block",
            [
                gen_line(jump_instr),
                *false_branch_block,
                gen_line(false_exit_instr),
                gen_line(label=true_label),
                *true_branch_block,
                gen_line(label=end_loc)
            ]
        )


class SwitchTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self._switch_id = 0


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
        return CompiledMC(lines, {})


class MCASMCompiler:

    def __init__(self):
        self._lark = Lark(load_grammar())
        self._location_resolver = LocationResolver()
        self._transform = (
                TypeTransformer() *
                LangTransformer() *
                # SwitchTransformer() *
                self._location_resolver *
                ControlInstructionTransformer() *
                JumpInstructionTransformer() *
                CodeTransformer()
        )

    def compile(self, text: str) -> CompiledMC:
        ast = self._lark.parse(text)
        info: CompiledMC = self._transform.transform(ast)
        info.labels = self._location_resolver.labels
        return info


def mc_compile(text: str) -> CompiledMC:
    comp = MCASMCompiler()
    return comp.compile(text)
