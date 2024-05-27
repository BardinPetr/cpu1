import io
from typing import List

from machine.arch import IOBusCtrl
from machine.config import IO_ADDR_BUS_SIZE, IO_DATA_BUS_SIZE
from machine.cpu import CPU
from machine.io.bus import create_io_bus
from machine.io.dev_keyboard import IODevKeyboard
from machine.io.dev_printer import IODevPrinter
from machine.mc.code import mcrom
from machine.utils.hdl import hdl_block, Bus, Bus1
from machine.utils.introspection import introspect


@hdl_block
def Machine(ram: List[int]):
    # external io buses
    iobus_clk, iobus_ctrl, iobus_addr, iobus_data = create_io_bus()

    cpu = CPU(
        mcrom.ROM, ram,
        iobus_clk, iobus_ctrl, iobus_addr, iobus_data,
    )

    dev0 = IODevPrinter(
        iobus_clk, iobus_ctrl, iobus_addr, iobus_data,
        address=0x10, address_count=0x3
    )
    dev1 = IODevKeyboard(
        iobus_clk, iobus_ctrl, iobus_addr, iobus_data,
        address=0x20, address_count=0x3,
        source=io.StringIO("hello")
    )

    return introspect()
