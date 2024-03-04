from random import randrange

from myhdl import *

from src.RAM import SDRAM, DRAM
from src.base import Clock
from utils.testutils import myhdl_pytest


@myhdl_pytest(gui=False)
def test_sdram():
    clk = Signal(False)
    clock = Clock(clk, 10)

    addr_bits = 4
    size = 1 << addr_bits

    en, we, oe = [Signal(False) for i in range(3)]
    addr = Signal(intbv(0)[addr_bits:])
    data = TristateSignal(intbv(0)[8:])
    data_in = data.driver()

    mem = SDRAM(clk, en, we, oe, addr, data, size)

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
            data_in.next = d
            yield delay(5)
            en.next = 1
            we.next = 1

            yield delay(20)

            en.next = 0
            we.next = 0
            data_in.next = None
            addr.next = 0

            yield delay(20)

        yield delay(200)

        for a, _ in test_data:
            addr.next = a
            yield delay(1)
            en.next = 1
            oe.next = 1

            yield delay(20)

            assert data.val == test_mem[a]
            yield delay(5)

            en.next = 0
            oe.next = 0
            addr.next = 0

            yield delay(20)

        raise StopSimulation

    return instances()


@myhdl_pytest(gui=False)
def test_dram():
    clk = Signal(False)
    clock = Clock(clk, 10)

    addr_bits = 4
    size = 1 << addr_bits

    wr = Signal(False)
    addr = Signal(intbv(0)[addr_bits:])
    in_data = Signal(intbv(0)[8:])
    out_data = Signal(intbv(0)[8:])

    mem = DRAM(clk, wr, addr, in_data, out_data, size)

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

    return instances()
