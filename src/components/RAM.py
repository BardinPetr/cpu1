from myhdl import *
from myhdl import _Signal
from myhdl._ShadowSignal import _TristateSignal

from utils.hdl import hdl_block
from utils.log import get_logger

L = get_logger()

@hdl_block
def SDRAM(
        clk: _Signal,
        en: _Signal,
        we: _Signal,
        oe: _Signal,
        addr: _Signal,
        data: _TristateSignal,
        size: int):
    """
    SDRAM emulation component
    Write and read on rising edge of clock according to WE/OE
    :param clk:     clock in
    :param en:      1 - enable, 0 - disable
    :param we:      WriteEnable: 1 - write, 0 - read
    :param oe:      OutputEnable: 1 - data lane is output, 0 - data lane as input
    :param addr:    address bus
    :param data:    RW data bus
    :param size:    emulated memory size in bytes
    """

    memory = [intbv(0) for _ in range(size)]

    data_out = data.driver()

    @always(oe)
    def tristate():
        if not en or not oe:
            delay(1)
            data_out.next = None

    @always(clk.posedge)
    def run():
        if en:
            _addr = int(addr.val)
            if _addr >= size:
                raise Exception(f"Invalid address {_addr:x}")

            if we and not oe:
                L.debug(f"WRITE [0x{_addr:x}] = {data.val}")
                memory[_addr][:] = data.val

            if not we and oe:
                L.debug(f"READ [0x{_addr:x}] == {memory[_addr]}")
                data_out.next = memory[_addr]

    return instances()


@hdl_block
def DRAM(
        clk: _Signal,
        wr: _Signal,
        addr: _Signal,
        in_data: _Signal,
        out_data: _Signal,
        size: int):
    """
    DRAM emulation component
    Write on rising edge of clock according to WR, read always
    :param clk:        clock in
    :param wr:         1 - write, 0 - no
    :param addr:       address bus
    :param in_data:    Write data bus
    :param out_data:   Read data bus
    :param size:       emulated memory size in bytes
    """

    memory = [intbv(0) for _ in range(size)]

    @always(clk.posedge)
    def write():
        if wr:
            _addr = int(addr.val)
            if _addr >= size:
                raise Exception(f"Invalid address {_addr:x}")

            L.debug(f"WRITE [0x{_addr:x}] = {in_data.val}")
            memory[_addr][:] = in_data.val

    @always_comb
    def read():
        _addr = int(addr.val)
        if _addr >= size:
            raise Exception(f"Invalid address {_addr:x}")

        L.debug(f"READ [0x{_addr:x}] == {memory[_addr]}")
        out_data.next = memory[_addr]

    return instances()
