from dataclasses import dataclass

from src.config import MC_INSTR_SZ
from src.mc.mcisa import *


@dataclass
class MCInstruction:
    instr_type: MCType = MCType.MC_RUN
    alu_ctrl: ALUCtrl = ALUCtrl.ZERO
    alu_flag_ctrl: ALUFlagCtrl = 0
    alu_port_a_ctrl: ALUPortCtrl = ALUPortCtrl.PASS
    alu_port_b_ctrl: ALUPortCtrl = ALUPortCtrl.PASS
    bus_a_in_ctrl: BusInCtrl = BusInCtrl.IGNORE
    bus_b_in_ctrl: BusInCtrl = BusInCtrl.IGNORE
    bus_c_out_ctrl: BusOutCtrl = BusInCtrl.IGNORE
    mem_ctrl: MemCtrl = MemCtrl.IGN

    def compile(self) -> int:
        res = intbv(0)[MC_INSTR_SZ:]
        MCALUCtrl.put(res, self.alu_ctrl)
        MCALUPortACtrl.put(res, self.alu_port_a_ctrl)
        MCALUPortBCtrl.put(res, self.alu_port_b_ctrl)
        MCALUFlagCtrl.put(res, self.alu_flag_ctrl)
        MCLType.put(res, self.instr_type)
        MCBusACtrl.put(res, self.bus_a_in_ctrl)
        MCBusBCtrl.put(res, self.bus_b_in_ctrl)
        MCBusCCtrl.put(res, self.bus_c_out_ctrl)
        MCMemCtrl.put(res, self.mem_ctrl)
        return int(res)

    @staticmethod
    def decompile(data: intbv | bytes) -> 'MCInstruction':
        if isinstance(data, bytes):
            data = intbv(int.from_bytes(data, byteorder='little'))
        return MCInstruction()


@dataclass
class MCInstructionJump(MCInstruction):
    jmp_cmp_bit: int = 0
    jmp_cmp_val: bool = False
    jmp_target: int = 0

    def __post_init__(self):
        self.instr_type = MCType.MC_JMP

    def compile(self) -> int:
        res = intbv(super().compile())
        MCJmpCmpBit.put(res, self.jmp_cmp_bit)
        MCJmpCmpVal.put(res, self.jmp_cmp_val)
        MCJmpTarget.put(res, self.jmp_target)
        return int(res)


class MCInstructionExec(MCInstruction):
    pass
