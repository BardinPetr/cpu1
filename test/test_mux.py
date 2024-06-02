from random import randrange

from myhdl import *

from machine.components.mux import Mux, DeMux
from machine.utils.introspection import introspect
from src.machine.utils.testutils import myhdl_pytest


@myhdl_pytest(gui=False)
def test_mux():
    inputs = [Signal(intbv(i)[8:]) for i in range(32)]
    outputs = [Signal(intbv(0)[8:]) for i in range(2)]
    ctrls = [Signal(intbv(0)[5:]) for i in range(2)]

    m2 = Mux(inputs[:2], outputs[0], ctrls[0])
    m32 = Mux(inputs[:32], outputs[1], ctrls[1])

    @instance
    def stimulus():
        for i, dim in enumerate([1, 5]):
            for v in range(2**dim):
                ctrls[i].next = v
                yield delay(1)
                assert outputs[i].val == v
        raise StopSimulation

    return introspect()


@myhdl_pytest(gui=False)
def test_demux():
    outputs = [Signal(intbv(0)[8:]) for i in range(32)]
    input = Signal(intbv(0)[8:])
    ctrl = Signal(intbv(0)[5:])

    m32 = DeMux(input, outputs, ctrl)

    @instance
    def stimulus():
        for v in range(32):
            data = randrange(128)
            ctrl.next = v
            input.next = data
            yield delay(20)

            assert all(
                outputs[i].val == (data if i == v else 0) for i in range(len(outputs))
            )
            yield delay(5)

        raise StopSimulation

    return introspect()
