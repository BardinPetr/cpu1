from typing import Optional, List

from myhdl import instances, Signal, _Signal
from myhdl._block import _Block, block

from src.components.base import Register, Clock
from src.datapath.datapath import DataPath
from src.mc.mcseq import MCSequencer
from utils.hdl import hdl_block, Bus

from src.config import *

MC_ROM = [
    0b0_00000000_0_00000001_00,
    0b0_00000000_0_00000011_00,
    0b1_00000010_1_00000000_00,
    0b0_00000000_0_00000111_00,
    0b0_00000000_0_00001111_00,
    0b1_00000001_0_00000000_00
]


@hdl_block
def CPU(mc_rom: List[int]):
    # control module base clock
    clk = Signal(False)
    clg = Clock(clk, 10)

    # control buses
    control_bus = Bus(CONTROL_BUS_SZ)

    # general-purpose buses
    bus_a = Bus(DATA_BITS)
    bus_b = Bus(DATA_BITS)
    bus_c = Bus(DATA_BITS)

    # submodules
    control = MCSequencer(clk, control_bus, bus_c, mc_rom_data=mc_rom)
    datapath = DataPath(control_bus, bus_a, bus_b, bus_c)

    return instances()
