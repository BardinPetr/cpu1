import sys
from io import StringIO
from typing import List, TextIO

from compiler.memory import unpack_binary
from machine.config import IO_PRINTER_ADDR_BASE, IO_PRINTER_ADDR_COUNT, \
    IO_KEYBOARD_ADDR_BASE, IO_KEYBOARD_ADDR_COUNT
from machine.cpu import CPU
from machine.io.bus import create_io_bus
from machine.io.dev_keyboard import IODevKeyboard
from machine.io.dev_printer import IODevPrinter
from machine.mc.code import mcrom
from machine.utils.hdl import hdl_block
from machine.utils.introspection import introspect


@hdl_block
def Machine(ram: List[int] | bytes,
            rom=None,
            io_input: TextIO = StringIO(),
            io_output: TextIO = StringIO(),
            io_input_delay: int = 1000,
            io_output_delay: int = 1000):
    if rom is None:
        rom = mcrom.ROM
    if isinstance(ram, bytes | bytearray):
        ram = unpack_binary(ram)

    # external io buses
    iobus_clk, iobus_ctrl, iobus_addr, iobus_data = create_io_bus()

    cpu = CPU(
        rom, ram,
        iobus_clk, iobus_ctrl, iobus_addr, iobus_data
    )

    dev0 = IODevPrinter(
        iobus_clk, iobus_ctrl, iobus_addr, iobus_data,
        address=IO_PRINTER_ADDR_BASE, address_count=IO_PRINTER_ADDR_COUNT,
        output=io_output, simulate_delay=io_output_delay
    )
    dev1 = IODevKeyboard(
        iobus_clk, iobus_ctrl, iobus_addr, iobus_data,
        address=IO_KEYBOARD_ADDR_BASE, address_count=IO_KEYBOARD_ADDR_COUNT,
        source=io_input, simulate_delay=io_input_delay
    )

    return introspect()
