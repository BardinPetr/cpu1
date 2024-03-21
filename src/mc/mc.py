from dataclasses import dataclass

from src.components.ALU import *
from src.mc.mcisa import *


@dataclass
class MCInstruction:
    instr_type: MCType
    alu_ctrl: ALUCtrl
    alu_flag_ctrl: ALUFlagCtrl
    alu_port_a_ctrl: ALUPortCtrl
    alu_port_b_ctrl: ALUPortCtrl

    def compile(self) -> int:
        res = intbv(0)[MC_INSTR_SZ:]
        MCALUCtrl.put(res, self.alu_ctrl)
        MCALUPortACtrl.put(res, self.alu_port_a_ctrl)
        MCALUPortBCtrl.put(res, self.alu_port_b_ctrl)
        MCALUFlagCtrl.put(res, self.alu_flag_ctrl)
        MCLType.put(res, self.instr_type)
        return int(res)

    @staticmethod
    def decompile(data: intbv | bytes) -> 'MCInstruction':
        if isinstance(data, bytes):
            data = intbv(int.from_bytes(data, byteorder='little'))
        return MCInstruction()


@dataclass
class MCInstructionJump(MCInstruction):
    jmp_cmp_reg: int
    jmp_cmp_bit: int
    jmp_cmp_val: bool
    jmp_target: int

    def compile(self) -> int:
        res = intbv(super().compile())
        MCLJmpCmpReg.put(res, self.jmp_cmp_reg)
        MCLJmpCmpBit.put(res, self.jmp_cmp_bit)
        MCLJmpCmpVal.put(res, self.jmp_cmp_val)
        MCLJmpTarget.put(res, self.jmp_target)
        return int(res)


class MCInstructionExec(MCInstruction):
    pass
