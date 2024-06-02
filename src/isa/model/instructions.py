from dataclasses import dataclass
from typing import Optional

from myhdl import intbv

from isa.model.opcodes import OpcodeEnum
from machine.utils.hdl import signed
from src.machine.config import INSTR_BITS


@dataclass
class Instruction:
    opcode: OpcodeEnum
    stack: Optional[int] = None
    ctrl: Optional[int] = None
    imm: int = 0

    def __post_init__(self):
        self.group = self.opcode.value[0]
        self.alt = self.opcode.value[1]
        if self.ctrl is None:
            if self.stack is not None:
                self.ctrl = self.stack
            else:
                self.ctrl = 0

    def __repr__(self):
        return str(self)

    def str_stack(self):
        return "@R" if self.stack is not None and self.stack == 1 else ""

    def __str__(self):
        return f"<{self.opcode}{self.str_stack()}>"

    def pack(self) -> intbv:
        res = intbv()[INSTR_BITS:]
        res[16:] = signed(self.imm, 16)
        res[16 + 4 : 16] = self.ctrl
        res[20 + 8 : 20] = self.alt
        res[28 + 4 : 28] = self.group
        return res


Instr = Instruction


@dataclass
class ImmInstr(Instruction):
    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"{super().__str__()}(I|{self.imm})"


@dataclass
class IPRelImmInstr(Instruction):
    abs: Optional[int] = None
    rel: Optional[int] = None

    def relocate(self, cur_ip: int, base: int = 0) -> ImmInstr:
        """
        Get new instruction with computed IP-relative offset
        If instruction has only absolute position, relative position is deduced
        :param cur_ip: memory position of that instruction. (+1 is added automatically)
        :param base: offset added to abs field
        :return: ImmInstr with configured imm field to relative position
        """
        if self.rel is not None:
            relative = self.rel
        elif self.abs is not None:
            relative = base + self.abs - (cur_ip + 1)
        else:
            raise ValueError(
                "Failed to get IP-relative location. Nor abs, nor rel fields specified"
            )

        return ImmInstr(opcode=self.opcode, ctrl=self.ctrl, imm=relative)

    def __repr__(self):
        return str(self)

    def __str__(self):
        r = self.rel if self.rel else "?"
        a = f"->{self.abs}" if self.abs else ""
        return f"{super().__str__()}(I|R{r}{a})"


@dataclass
class AbsImmInstr(Instruction):
    ref_object_name: Optional[str] = None

    def relocate(self, base: int = 0) -> ImmInstr:
        """
        Get new instruction with computed absolute address to fixed memory point
        :param base: offset added
        :return: ImmInstr with configured imm field to absolute position
        """
        return ImmInstr(opcode=self.opcode, ctrl=self.ctrl, imm=base + self.imm)
