from typing import List, Optional

from myhdl import *

from src.components.base import Clock
from src.config import *
from src.datapath.datapath import DataPath
from src.mc.mcseq import MCSequencer
from utils.hdl import hdl_block, Bus


@hdl_block
def CPU(mc_rom: List[int], ram: Optional[List[int]] = None):
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
    datapath = DataPath(clk, control_bus, bus_a, bus_b, bus_c, ram=ram)

    return instances()
