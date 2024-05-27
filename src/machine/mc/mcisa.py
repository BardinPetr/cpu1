from enum import IntEnum
from typing import TypeVar

from src.machine.arch import BusInCtrl, BusOutCtrl, MemCtrl, ALUCtrl, ALUPortCtrl, ALUFlagCtrl, StackCtrl, MachineCtrl, \
    MachineIOCtrl
from src.machine.mc.base import MCLocator as L
from src.machine.utils.enums import CEnumS

T = TypeVar('T', bound=IntEnum)


class MCType(CEnumS):
    MC_RUN = 0b0
    MC_JMP = 0b1


# common
MCLType = L(MCType).at(0)
MCALUCtrl = L(ALUCtrl).after(MCLType)
MCALUPortACtrl = L(ALUPortCtrl).after(MCALUCtrl)
MCALUPortBCtrl = L(ALUPortCtrl).after(MCALUPortACtrl)
MCBusACtrl = L(BusInCtrl).after(MCALUPortBCtrl)
MCBusBCtrl = L(BusInCtrl).after(MCBusACtrl)

# ending for exec
MCALUFlagCtrl = L(ALUFlagCtrl).after(MCBusBCtrl)
MCBusCCtrl = L(BusOutCtrl).after(MCALUFlagCtrl)
MCMemCtrl = L(MemCtrl).after(MCBusCCtrl)
MCStackDCtrl = L(StackCtrl).after(MCMemCtrl)
MCStackRCtrl = L(StackCtrl).after(MCStackDCtrl)
MCMachineCtrl = L(MachineCtrl).after(MCStackRCtrl)
MCMachineIOCtrl = L(MachineIOCtrl).after(MCMachineCtrl)

# ending for jump
MCJmpCmpBit = L(bits=16).after(MCBusBCtrl)
MCJmpCmpVal = L(bits=1).after(MCJmpCmpBit)
MCJmpTarget = L(bits=11).after(MCJmpCmpVal)

MCHeadNormal = MCMachineIOCtrl
MCHeadJump = MCJmpTarget

if __name__ == "__main__":
    print(f"MCN LEN={MCHeadNormal.loc_end}")
    print(f"MCJ LEN={MCHeadJump.loc_end}")
