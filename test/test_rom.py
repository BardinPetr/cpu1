from random import randrange

from myhdl import *

from src.components.ROM import ROM
from utils.introspection import introspect
from utils.testutils import myhdl_pytest


@myhdl_pytest(gui=False)
def test_rom():
    addr_bits = 8
    data_bits = 8
    size = 1 << addr_bits

    clk = Signal(False)
    addr = Signal(intbv(0)[addr_bits:])
    data = Signal(intbv(0)[data_bits:])

    test_data = [randrange(0, size) for _ in range(size)]

    mem = ROM(clk, addr, data, test_data)

    @instance
    def stimulus():
        for a, v in enumerate(test_data):
            addr.next = a

            yield delay(5)
            clk.next = 1
            yield delay(5)
            clk.next = 0

            assert data.val == v

            yield delay(20)

        raise StopSimulation

    return introspect()
