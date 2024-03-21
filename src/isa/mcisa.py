from dataclasses import dataclass

from myhdl import intbv

from src.config import MC_INSTR_SZ
from src.mc.mcisa import MCType, MCALUCtrl, MCALUPortCtrl


@dataclass
class MCInstruction:
    instr_type: MCType
    alu_ctrl: MCALUCtrl
    alu_port_a_ctrl: MCALUPortCtrl
    alu_port_b_ctrl: MCALUPortCtrl

    def compile(self) -> intbv:
        res = intbv(0)[MC_INSTR_SZ:]
        return res

    @staticmethod
    def decompile(data: intbv | bytes) -> 'MCInstruction':
        if isinstance(data, bytes):
            data = intbv(int.from_bytes(data, byteorder='little'))

        return MCInstruction()


class MCInstructionJump(MCInstruction):
    pass


class MCInstructionExec(MCInstruction):
    pass
