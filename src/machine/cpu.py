from typing import List, Optional

from machine.arch import IOBusCtrl
from machine.components.io.dev_printer import IODevPrinter
from src.machine.components.base import Clock
from src.machine.config import CONTROL_BUS_SZ, DATA_BITS, IO_ADDR_BUS_SIZE, IO_DATA_BUS_SIZE
from src.machine.datapath.datapath import DataPath
from src.machine.mc.components.mcseq import MCSequencer
from src.machine.utils.hdl import hdl_block, Bus, Bus1
from src.machine.utils.introspection import introspect


@hdl_block
def CPU(mc_rom: List[int], ram: Optional[List[int]] = None):
    # control module base clock
    clk_dp = Bus1(delay=1)
    clk = Bus1()
    clg = Clock(clk, 10)

    # control buses
    control_bus = Bus(CONTROL_BUS_SZ)

    # general-purpose buses
    bus_a = Bus(DATA_BITS)
    bus_b = Bus(DATA_BITS)
    bus_c = Bus(DATA_BITS)

    # io buses
    iobus_ctrl = Bus(enum=IOBusCtrl)
    iobus_addr = Bus(bits=IO_ADDR_BUS_SIZE)
    iobus_data = Bus(bits=IO_DATA_BUS_SIZE, tristate=True)
    iobus_clk = Bus1(0)

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

    # io
    dev0 = IODevPrinter(
        iobus_clk, iobus_ctrl, iobus_addr, iobus_data,
        address=0x10, address_count=0xF
    )
    dev1 = IODevPrinter(
        iobus_clk, iobus_ctrl, iobus_addr, iobus_data,
        address=0x20, address_count=0xF
    )

    return introspect()
