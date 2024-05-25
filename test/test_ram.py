from random import randrange

from myhdl import *

from machine.utils.hdl import Bus1
from machine.utils.introspection import introspect

from src.machine.components import Clock
from src.machine.components import RAMSyncSP
from src.machine.utils.testutils import myhdl_pytest


@myhdl_pytest(gui=False)
def test_sp_sync_ram():
    clk = Bus1()
    clock = Clock(clk, 10)

    addr_bits = 4
    size = 1 << addr_bits

    wr = Bus1()
    addr = Signal(intbv(0)[addr_bits:])
    in_data = Signal(intbv(0)[8:])
    out_data = Signal(intbv(0)[8:])

    mem = RAMSyncSP(clk, wr, addr, in_data, out_data, depth=size, width=8)

    @instance
    def stimulus():
        test_mem = {}
        test_data = [
            (randrange(0, size), intbv(randrange(0, 1 << 8)))
            for _ in range(size)
        ]
        print()

        for a, d in test_data:
            test_mem[a] = d
            addr.next = a
            in_data.next = d
            yield delay(5)
            wr.next = 1

            yield delay(20)

            wr.next = 0
            in_data.next = 0
            addr.next = 0

            yield delay(20)

        yield delay(200)

        for a, _ in test_data:
            addr.next = a

            yield delay(20)

            assert out_data.val == test_mem[a]
            yield delay(5)

            addr.next = 0

            yield delay(20)

        raise StopSimulation

    return introspect()
