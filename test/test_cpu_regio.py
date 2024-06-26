from myhdl import *

from machine.cpu import CPU
from machine.utils.log import get_logger
from src.machine.utils.introspection import introspect, IntrospectionTree
from src.machine.utils.testutils import myhdl_pytest
from src.mcasm.parse import mc_compile

L = get_logger()

MC_ROM = mc_compile("""
start:
(IP ADD Z(INC)) -> IP;
(IP ADD);
jump start;
""").compiled


@myhdl_pytest(gui=False, duration=None)
def test_cpu_regio():
    cpu = CPU(MC_ROM)

    intro = IntrospectionTree.build(cpu)
    clk = intro.clk_dp
    bus_a, bus_b, bus_c = intro.bus_a, intro.bus_b, intro.bus_c
    mc_pc = intro.control.seq.mc_pc

    seq_mc_pc = []
    seq_bus_c = []

    @always_comb
    def check_mcpc():
        seq_mc_pc.append(int(mc_pc))

    END = 20

    @instance
    def stimulus():
        mc_ttl = 100
        while mc_ttl > 0:
            yield clk.negedge
            yield delay(1)

            c_val = int(bus_c)
            if c_val > END:
                break
            seq_bus_c.append(c_val)

            mc_ttl -= 1
        else:
            raise Exception("Haven't reached microcode end before 100 ticks")

        """
        ON falling edge BUS_C HAS:
        1st:  A=IP, B=1, C=A+B => store C to IP  (IP += 1)   so on that instruction C is the next IP
        2nd:  C = IP
        3rd:  Jump (no ALU op)
        """
        target_bus_c = []
        for i in range(END):
            target_bus_c += [i + 1, i + 1, 0]

        print("TARGET :", target_bus_c)
        print("REAL   :", seq_bus_c)

        assert seq_bus_c == target_bus_c

        raise StopSimulation()

    return introspect()
