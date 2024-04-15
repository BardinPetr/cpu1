from myhdl import *

from machine.arch import *
from machine.arch import ALUCtrl, ALUPortCtrl
from machine.cpu import CPU
from machine.mc.mc import MCInstruction, MCInstructionJump
from machine.utils.introspection import introspect, IntrospectionTree
from machine.utils.log import get_logger
from machine.utils.testutils import myhdl_pytest

L = get_logger()

MC_ROM = [
    MCInstruction(
        alu_ctrl=ALUCtrl.ADD,
        alu_port_b_ctrl=ALUPortCtrl.INC,
        bus_a_in_ctrl=BusInCtrl.RF_IP,
        bus_c_out_ctrl=BusOutCtrl.RF_IP
    ),
    MCInstruction(
        alu_ctrl=ALUCtrl.PASSA,
        bus_a_in_ctrl=BusInCtrl.RF_IP
    ),
    MCInstructionJump(jmp_target=0, jmp_cmp_bit=0, jmp_cmp_val=False),
]

MC_ROM_COMPILED = [i.compile() for i in MC_ROM]


@myhdl_pytest(gui=False, duration=None)
def test_cpu_regio():
    for src, comp in zip(MC_ROM, MC_ROM_COMPILED):
        L.info(f"MC{comp:064b}: {src}")

    cpu = CPU(MC_ROM_COMPILED)

    intro = IntrospectionTree.build(cpu)
    clk = intro.clk
    bus_a, bus_b, bus_c = intro.bus_a, intro.bus_b, intro.bus_c
    mc_pc = intro.control.mc_pc

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
        for i in range(END - 1):
            target_bus_c += [i + 2, i + 1, 0]

        print("TARGET :", target_bus_c)
        print("REAL   :", seq_bus_c)

        assert target_bus_c == seq_bus_c

        raise StopSimulation()

    return introspect()
