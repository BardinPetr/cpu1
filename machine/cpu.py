from typing import List, Optional

from machine.components.base import Clock
from machine.config import *
from machine.datapath.datapath import DataPath
from machine.mc.mcseq import MCSequencer
from machine.utils.hdl import hdl_block, Bus, Bus1
from machine.utils.introspection import introspect


@hdl_block
def CPU(mc_rom: List[int], ram: Optional[List[int]] = None):
    # control module base clock
    clk = Bus1()
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

    return introspect()