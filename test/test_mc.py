import random

from myhdl import *

from src.components.ROM import AsyncROM
from src.components.base import Clock, Trig, RTrig, Counter, Reg
from src.mc.mcseq import MCSequencer
from utils.hdl import create_int_signal
from utils.testutils import myhdl_pytest
from src.config import *


@myhdl_pytest(gui=False, duration=1000)
def test_mc():
    clk = Signal(False)
    cld = Clock(clk, 10)

    CR = create_int_signal(MC_INSTR_BIT)
    PS = create_int_signal(MC_INSTR_BIT)

    mc_cr = create_int_signal(MC_INSTR_BIT)

    MC_ROM = [
        0b0_00000000_0_00000001_00,
        0b0_00000000_0_00000011_00,
        0b0_00000000_0_00000111_00,
        0b0_00000000_0_00001111_00,
        0b1_00000010_0_00000000_00
    ]
    mcc = MCSequencer(clk, mc_cr, CR, PS, mc_rom_data=MC_ROM)

    @instance
    def stimulus():
        cr_seq = []
        for i in range(14):
            yield clk.negedge
            cr_seq.append(mc_cr.val[:])

        # first normal iteration
        # then jumped to 0x2, run 0x2 to 0x4 and looped
        TARGET_SEQ = [
            *MC_ROM,
            *MC_ROM[2:],
            *MC_ROM[2:],
            *MC_ROM[2:]
        ]
        assert cr_seq == TARGET_SEQ

        raise StopSimulation

    return instances()
