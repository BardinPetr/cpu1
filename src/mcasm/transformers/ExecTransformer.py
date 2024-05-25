from typing import List

from lark import Transformer, Token

from mcasm.utils import merge_dicts
from src.machine import arch
from src.machine.mc.mcinstr import MCInstructionExec


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
        cmd_name = vals[0].upper()
        stack_cmd = arch.StackCtrl.encode_from_names([cmd_name])
        res = {f"stack_{stack_name.lower()}_ctrl": stack_cmd}
        if cmd_name not in ["POP", "NONE"]:
            res["bus_c_out_ctrl"] = arch.BusOutCtrl.encode_from_names([f"{stack_name.upper()}S"])
        return res

    """IO control"""
    exec_mem = lambda self, x: dict(mem_ctrl=arch.MemCtrl.WR)
