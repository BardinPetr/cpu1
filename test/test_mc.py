import logging

from myhdl import *

from src.components.base import Clock
from src.config import *
from src.mc.mc import MCInstruction, MCInstructionJump
from src.mc.mcseq import MCSequencer, L as MCS_LOG
from utils.hdl import Bus
from utils.introspection import introspect
from utils.testutils import myhdl_pytest

MCS_LOG.setLevel(logging.DEBUG)


@myhdl_pytest(gui=False, duration=None)
def test_mc():
    clk = Signal(False)
    cld = Clock(clk, 10)

    CR = Bus(MC_INSTR_SZ)
    busc = Bus(MC_INSTR_SZ, state=0b10)

    mc_cr = Bus(MC_INSTR_SZ)

    MC_ROM = [
        MCInstruction(),
        MCInstruction(),
        MCInstructionJump(jmp_target=100, jmp_cmp_bit=1, jmp_cmp_val=False),
        MCInstruction(),
        MCInstruction(),
        MCInstructionJump(jmp_target=1, jmp_cmp_bit=1, jmp_cmp_val=True),
    ]
    MC_ROM = [i.compile() for i in MC_ROM]

    # running to 0x2
    # jump at 0x2 to 0x2 is not working as BUSC hardcoded to 0b10 and jump if BUSC[1]==False
    # running to 0x5
    # jumped from 0x5 to 0x1
    # loop from 0x1
    TARGET_SEQ = [
        *MC_ROM,
        *MC_ROM[1:],
        *MC_ROM[1:],
        *MC_ROM[1:]
    ]

    mcc = MCSequencer(clk, mc_cr, busc, mc_rom_data=MC_ROM)

    @instance
    def stimulus():
        cr_seq = []
        for i in range(len(TARGET_SEQ) + 1):
            yield clk.posedge
            cr_seq.append(int(mc_cr.val[:]))

        cr_seq = cr_seq[1:]  # ignore first as instruction loaded on falling

        assert cr_seq == TARGET_SEQ

        raise StopSimulation

    return introspect()
