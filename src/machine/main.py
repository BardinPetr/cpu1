from typing import List

from machine.arch import IOBusCtrl
from machine.components.io.dev_printer import IODevPrinter
from machine.config import IO_ADDR_BUS_SIZE, IO_DATA_BUS_SIZE
from machine.cpu import CPU
from machine.mc.code import mcrom
from machine.utils.hdl import hdl_block, Bus, Bus1
from machine.utils.introspection import introspect


@hdl_block
def Machine(ram: List[int]):
    # external io buses
    iobus_ctrl = Bus(enum=IOBusCtrl)
    iobus_addr = Bus(bits=IO_ADDR_BUS_SIZE)
    iobus_data = Bus(bits=IO_DATA_BUS_SIZE, tristate=True)
    iobus_clk = Bus1(0)

    cpu = CPU(
        mcrom.ROM, ram,
        iobus_clk, iobus_ctrl, iobus_addr, iobus_data,
    )

    dev0 = IODevPrinter(
        iobus_clk, iobus_ctrl, iobus_addr, iobus_data,
        address=0x10, address_count=0xF
    )
    dev1 = IODevPrinter(
        iobus_clk, iobus_ctrl, iobus_addr, iobus_data,
        address=0x20, address_count=0xF
    )

    return introspect()
