from machine.arch import IOBusCtrl
from machine.config import IO_ADDR_BUS_SIZE, IO_DATA_BUS_SIZE
from machine.utils.hdl import Bus1, Bus


def create_io_bus():
    iobus_ctrl = Bus(enum=IOBusCtrl)
    iobus_addr = Bus(bits=IO_ADDR_BUS_SIZE)
    iobus_data = Bus(bits=IO_DATA_BUS_SIZE, tristate=True)
    iobus_clk = Bus1(0)
    return iobus_clk, iobus_ctrl, iobus_addr, iobus_data
