from dataclasses import dataclass
from typing import Annotated, List, Tuple, get_type_hints

from machine.config import MC_INSTR_SZ
from machine.mc.mcisa import *


@dataclass
class MCInstruction:
    instr_type: Annotated[MCType, MCLType] = MCType.MC_RUN
    alu_ctrl: Annotated[ALUCtrl, MCALUCtrl] = ALUCtrl.ZERO
    alu_port_a_ctrl: Annotated[ALUPortCtrl, MCALUPortACtrl] = ALUPortCtrl.PASS
    alu_port_b_ctrl: Annotated[ALUPortCtrl, MCALUPortBCtrl] = ALUPortCtrl.PASS
    bus_a_in_ctrl: Annotated[BusInCtrl, MCBusACtrl] = 0
    bus_b_in_ctrl: Annotated[BusInCtrl, MCBusBCtrl] = 0

    def __post_init__(self):
        self._init_locators()
        self.fields = self._inspect_fields()

    def compile(self) -> int:
        res = intbv(0)[MC_INSTR_SZ:]

        fields = self._inspect_fields()
        for param_name, _, locator in fields:
            try:
                locator.put(res, self.__getattribute__(param_name))
            except AttributeError:
                print(f"Failed to process field {param_name}")

        return int(res)

    @staticmethod
    def decompile(data: intbv | bytes) -> 'MCInstruction':
        if isinstance(data, bytes):
            data = intbv(int.from_bytes(data, byteorder='little'))
        return MCInstructionExec()

    @classmethod
    def _init_locators(cls):
        fields = cls._inspect_fields()
        for i, (name, annot, locator) in enumerate(fields):
            if i == 0:
                locator.at(0)
            if locator.loc_start is None:
                locator.after(fields[i - 1][2])

    @classmethod
    def _inspect_fields(cls) -> List[Tuple[str, Annotated, MCLocator]]:
        return [
            (name, annot, annot.__metadata__[0])
            for name, annot in get_type_hints(cls, include_extras=True).items()
        ]

    @classmethod
    def describe(cls):
        cls._init_locators()
        name = cls.__name__.replace("MCInstruction", "")
        fields = cls._inspect_fields()
        fields = [
            (f"[{loc.loc_start:2d}:{loc.loc_end:2d}) "
             f"{loc.size:2d}b   "
             f"{annot.__args__[0].__name__:12s}"
             f"as {name}")
            for name, annot, loc in fields
        ]
        sep = '\n  '
        return f"{name} [{sep}{sep.join(fields)}\n]"


@dataclass
class MCInstructionJump(MCInstruction):
    jmp_cmp_bit: Annotated[int, MCJmpCmpBit] = 0
    jmp_cmp_val: Annotated[bool, MCJmpCmpVal] = False
    jmp_target: Annotated[int, MCJmpTarget] = 0

    def __post_init__(self):
        self.instr_type = MCType.MC_JMP
        super().__post_init__()


@dataclass
class MCInstructionExec(MCInstruction):
    alu_flag_ctrl: Annotated[ALUFlagCtrl, MCALUFlagCtrl] = 0
    bus_c_out_ctrl: Annotated[BusOutCtrl, MCBusCCtrl] = 0
    mem_ctrl: Annotated[MemCtrl, MCMemCtrl] = MemCtrl.IGN
    stack_d_ctrl: Annotated[StackCtrl, MCStackDCtrl] = StackCtrl.NONE
    stack_r_ctrl: Annotated[StackCtrl, MCStackRCtrl] = StackCtrl.NONE


if __name__ == "__main__":
    print(MCInstructionJump.describe())
    print(MCInstructionExec.describe())
