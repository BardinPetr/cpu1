from dataclasses import dataclass
from typing import Annotated

import src.machine.mc.mcisa as MCLocs
from src.machine.arch import (
    ALUCtrl,
    ALUPortCtrl,
    StackCtrl,
    MemCtrl,
    BusOutCtrl,
    ALUFlagCtrl,
    BusInCtrl,
    MachineCtrl,
    MachineIOCtrl,
)
from src.machine.mc.base import BaseMCInstruction


@dataclass
class MCInstruction(BaseMCInstruction):
    instr_type: Annotated[MCLocs.MCType, MCLocs.MCLType] = MCLocs.MCType.MC_RUN
    alu_ctrl: Annotated[ALUCtrl, MCLocs.MCALUCtrl] = ALUCtrl.ZERO
    alu_port_a_ctrl: Annotated[ALUPortCtrl, MCLocs.MCALUPortACtrl] = ALUPortCtrl.PASS
    alu_port_b_ctrl: Annotated[ALUPortCtrl, MCLocs.MCALUPortBCtrl] = ALUPortCtrl.PASS
    bus_a_in_ctrl: Annotated[BusInCtrl, MCLocs.MCBusACtrl] = 0
    bus_b_in_ctrl: Annotated[BusInCtrl, MCLocs.MCBusBCtrl] = 0

    def __repr__(self):
        return str(self)

    def __str__(self):
        return (
            f"<{self.alu_ctrl}"
            f" A={self.alu_port_a_ctrl}({self.bus_a_in_ctrl}) "
            f"B={self.alu_port_b_ctrl}({self.bus_b_in_ctrl})>"
        )


@dataclass
class MCInstructionJump(MCInstruction):
    jmp_cmp_bit: Annotated[int, MCLocs.MCJmpCmpBit] = 0
    jmp_cmp_val: Annotated[bool, MCLocs.MCJmpCmpVal] = False
    jmp_target: Annotated[int, MCLocs.MCJmpTarget] = 0

    def __post_init__(self):
        self.instr_type = MCLocs.MCType.MC_JMP
        super().__post_init__()

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{super().__str__()} & <JMP bit={self.jmp_cmp_bit} ={self.jmp_cmp_val:d} to={self.jmp_target}>"


@dataclass
class MCInstructionExec(MCInstruction):
    alu_flag_ctrl: Annotated[ALUFlagCtrl, MCLocs.MCALUFlagCtrl] = 0
    bus_c_out_ctrl: Annotated[BusOutCtrl, MCLocs.MCBusCCtrl] = 0
    mem_ctrl: Annotated[MemCtrl, MCLocs.MCMemCtrl] = MemCtrl.IGN
    stack_d_ctrl: Annotated[StackCtrl, MCLocs.MCStackDCtrl] = StackCtrl.NONE
    stack_r_ctrl: Annotated[StackCtrl, MCLocs.MCStackRCtrl] = StackCtrl.NONE
    machine_ctrl: Annotated[MachineCtrl, MCLocs.MCMachineCtrl] = 0
    io_ctrl: Annotated[MachineIOCtrl, MCLocs.MCMachineIOCtrl] = 0


if __name__ == "__main__":
    print(MCInstructionJump.describe())
    print(MCInstructionExec.describe())
