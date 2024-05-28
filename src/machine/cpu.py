from typing import List, Optional

from myhdl import intbv

from machine.io.bus import create_io_bus
from src.machine.components.base import Clock
from src.machine.config import DATA_BITS, MC_INSTR_SZ
from src.machine.datapath.datapath import DataPath
from src.machine.mc.components.mcseq import MCSequencer
from src.machine.utils.hdl import hdl_block, Bus, Bus1
from src.machine.utils.introspection import introspect


@hdl_block
def CPU(mc_rom: List[int],
        ram: Optional[List[int | intbv]] = None,
        iobus_clk=None, iobus_ctrl=None, iobus_addr=None, iobus_data=None):
    if any(map(lambda x: x is None, [iobus_clk, iobus_ctrl, iobus_addr, iobus_data])):
        iobus_clk, iobus_ctrl, iobus_addr, iobus_data = create_io_bus()

    # control module base clock
    clk_dp = Bus1(delay=0)
    clk = Bus1()
    clg = Clock(clk, 10)

    # control buses
    control_bus = Bus(MC_INSTR_SZ)

    # general-purpose buses
    bus_a = Bus(DATA_BITS)
    bus_b = Bus(DATA_BITS)
    bus_c = Bus(DATA_BITS)

    # submodules
    control = MCSequencer(
        clk, clk_dp,
        control_bus, bus_c,
        mc_rom_data=mc_rom
    )
    datapath = DataPath(
        clk_dp,
        control_bus,
        bus_a, bus_b, bus_c,
        iobus_clk, iobus_ctrl, iobus_addr, iobus_data,
        ram=ram
    )

    return introspect()
