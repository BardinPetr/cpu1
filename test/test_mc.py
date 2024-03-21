import logging

from myhdl import *

from src.components.base import Clock
from src.config import *
from src.mc.mcseq import MCSequencer, L as MCS_LOG
from utils.hdl import Bus
from utils.testutils import myhdl_pytest

MCS_LOG.setLevel(logging.DEBUG)


@myhdl_pytest(gui=False, duration=None)
def test_mc():
    clk = Signal(False)
    cld = Clock(clk, 10)

    CR = Bus(MC_INSTR_SZ)
    PS = Bus(MC_INSTR_SZ)

    mc_cr = Bus(MC_INSTR_SZ)

    MC_ROM = [
        0b0_00000000_0_00000001_00,
        0b0_00000000_0_00000011_00,
        0b1_00000010_1_00000000_00,  # should NOT jump as PS=0, cmp_val=1
        0b0_00000000_0_00000111_00,
        0b0_00000000_0_00001111_00,
        0b1_00000001_0_00000000_00  # should jump as PS=0, cmp_val=0
    ]

    # running to 0x2
    # jump at 0x2 to 0x2 is not working as ps hardcoded to 0
    # running to 0x5
    # jumped from 0x5 to 0x1
    # loop from 0x1
    TARGET_SEQ = [
        *MC_ROM,
        *MC_ROM[1:],
        *MC_ROM[1:],
        *MC_ROM[1:]
    ]

    mcc = MCSequencer(clk, mc_cr, CR, PS, mc_rom_data=MC_ROM)

    @instance
    def stimulus():
        cr_seq = []
        for i in range(len(TARGET_SEQ) + 1):
            yield clk.posedge
            cr_seq.append(int(mc_cr.val[:]))

        cr_seq = cr_seq[1:]  # ignore first as instruction loaded on falling

        assert cr_seq == TARGET_SEQ

        raise StopSimulation

    return instances()
