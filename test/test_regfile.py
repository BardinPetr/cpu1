import random

from myhdl import *

from machine.utils.hdl import Bus, Bus1
from machine.utils.introspection import introspect
from machine.utils.log import get_logger
from src.machine.components import Clock
from src.machine.components import RegisterFile
from src.machine.utils.testutils import myhdl_pytest

L = get_logger()


@myhdl_pytest(gui=False, duration=None)
def test_regfile():
    clk = Bus1()
    clg = Clock(clk, 10)

    sz = 8
    bits = 3

    we = Bus1()
    out0id, out1id, inid = [Bus(bits) for _ in range(3)]
    out0bus, out1bus, inbus = [Bus() for _ in range(3)]

    rf = RegisterFile(clk, we, out0id, out1id, inid, out0bus, out1bus, inbus, count=sz)

    rf_sim = [0 for _ in range(sz)]

    @instance
    def stimulus():
        values = random.choices(range(1, 1 << 8), k=2 * sz)
        cmds = list(zip(list(range(sz)) * 2, values))
        random.shuffle(cmds)

        # write all registers twice
        for i, val in cmds:
            # do write
            yield clk.posedge
            inid.next = i
            inbus.next = val
            we.next = True

            # request for that register
            out0id.next = i
            out1id.next = i

            yield delay(1)

            # before falling edge there should be previous value
            assert rf_sim[i] == out0bus.val
            assert rf_sim[i] == out1bus.val

            yield clk.negedge

            # write should occur on falling edge
            rf_sim[i] = val

            yield delay(1)
            we.next = False

            # reads are not sequential
            assert rf_sim[i] == out0bus.val
            assert rf_sim[i] == out1bus.val

        # check final data with different ports
        for i in range(sz - 1):
            out0id.next = i
            out1id.next = i + 1

            yield delay(1)

            assert rf_sim[i] == out0bus.val
            assert rf_sim[i + 1] == out1bus.val

            yield delay(1)

        raise StopSimulation

    return introspect()
