import logging

from myhdl import *

from machine.utils.hdl import Bus, Bus1
from machine.utils.introspection import introspect

from src.machine.components import Clock
from src.machine.config import MC_INSTR_SZ
from src.machine.mc.mcinstr import MCInstructionJump, MCInstructionExec
from src.machine.mc.components.mcseq import MCSequencer, L as MCS_LOG
from src.machine.utils.testutils import myhdl_pytest

MCS_LOG.setLevel(logging.DEBUG)


@myhdl_pytest(gui=False, duration=None)
def test_mc():
    clk = Bus1()
    cld = Clock(clk, 10)

    CR = Bus(MC_INSTR_SZ)
    busc = Bus(MC_INSTR_SZ, state=0b10)

    mc_cr = Bus(MC_INSTR_SZ)

    MC_ROM = [
        MCInstructionExec(),
        MCInstructionExec(),
        MCInstructionJump(jmp_target=100, jmp_cmp_bit=1, jmp_cmp_val=False),
        MCInstructionExec(),
        MCInstructionExec(),
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
