from mcasm.parse import mc_compile
from myhdl import *

from machine.arch import PSFlags
from machine.cpu import CPU
from machine.utils.hdl import *
from machine.utils.introspection import introspect, IntrospectionTree
from machine.utils.log import get_logger
from machine.utils.testutils import myhdl_pytest

L = get_logger()

MC_ROM = mc_compile("""
(ADD), set(N,Z,V,C);
jump 0;
""").compiled


@myhdl_pytest(gui=False, duration=None)
def test_cpu_aluflags():
    cpu = CPU(MC_ROM)

    intro = IntrospectionTree.build(cpu)
    clk = intro.clk
    bus_a, bus_b, bus_c = intro.bus_a, intro.bus_b, intro.bus_c
    ps = intro.datapath.reg_ps.d_out

    AB_IN = [
        (-1, 0),
        (0, 0),
        (1, 0),
        (UINT_MAX, 1),
        (0, negate(1)),
        (SINT_MAX, 1),
        (SINT_MIN, negate(1)),
    ]
    TARGET_PS = [
        dict(Z=False, N=True, C=False, V=False),
        dict(Z=True, N=False, C=False, V=False),
        dict(Z=False, N=False, C=False, V=False),
        dict(C=True),
        dict(N=True),
        dict(V=True),
        dict(V=True),
    ]
    ps_output = []

    @instance
    def stimulus():
        for a, b in AB_IN:
            set_signed(bus_a, a)
            set_signed(bus_b, b)
            yield clk.negedge
            yield delay(1)

            ps_output.append(PSFlags.decode_flags(ps.val))

            yield clk.negedge
            yield delay(1)

        print(ps_output)
        print(TARGET_PS)

        for real, test in zip(ps_output, TARGET_PS):
            for name, val in test.items():
                assert val == real[name]

        raise StopSimulation()

    return introspect()
