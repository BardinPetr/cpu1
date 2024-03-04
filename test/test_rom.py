from random import randrange

from myhdl import *

from src.ROM import AsyncROM
from utils.testutils import myhdl_pytest


@myhdl_pytest(gui=False)
def test_rom():
    addr_bits = 8
    data_bits = 8
    size = 1 << addr_bits

    en = Signal(False)
    addr = Signal(intbv(0)[addr_bits:])
    data = Signal(intbv(0)[data_bits:])

    test_data = [randrange(0, size) for _ in range(size)]

    mem = AsyncROM(en, addr, data, test_data)

    @instance
    def stimulus():
        for a, v in enumerate(test_data):
            addr.next = a
            yield delay(1)
            en.next = 1

            # wait for data to be present
            yield delay(10)

            assert data.val == v
            en.next = 0

            yield delay(20)

        raise StopSimulation

    return instances()
