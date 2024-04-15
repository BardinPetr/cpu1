from mcasm.parse import mc_compile
from myhdl import *

from machine.arch import *
from machine.arch import ALUCtrl, ALUPortCtrl
from machine.cpu import CPU
from machine.mc.mc import MCInstruction, MCInstructionJump
from machine.utils.introspection import IntrospectionTree, TraceData, Trace, IntrospectedMemory
from machine.utils.log import get_logger
from machine.utils.testutils import myhdl_pytest

L = get_logger()

"""
This test is imitating read of program from RAM.
Each cycle:
    AR <- IP
    CR <- DR
    C  <- CR
    IP <- IP + 1

Test is to output to CR whole RAM segment from 0 to LEN.
"""

MC_ROM = mc_compile("""
(RF_IP PASSA) -> AR;
(DRR PASSA) -> RF_CR;
(RF_IP(INC) PASSA) -> RF_IP;
(RF_CR PASSA);
jump 0;
""").compiled


@myhdl_pytest(gui=False, duration=None)
def test_cpu_mem_read():
    for src, comp in zip(MC_ROM, MC_ROM):
        L.info(f"MC{comp:064b}: {src}")

    LEN = 10
    RAM = [16 * i + 7 for i in range(LEN)]
    cpu = CPU(MC_ROM, RAM)

    intro = IntrospectionTree.build(cpu)
    clk = intro.clk
    bus_a, bus_b, bus_c = intro.bus_a, intro.bus_b, intro.bus_c
    mem: IntrospectedMemory = intro.datapath.ram_mod.memory

    seq_cr = []

    trace_res = TraceData()
    tracer = Trace(
        intro.clk,
        trace_res,
        {
            "CLK": intro.clk,
            "MCR": intro.control_bus,
            "A":   intro.datapath.bus_a,
            "B":   intro.datapath.bus_b,
            "C":   intro.datapath.bus_c,
        }
    )

    @instance
    def stimulus():
        for i in range(len(MC_ROM) * LEN):
            yield clk.posedge
            yield delay(1)

            c_val = int(bus_c.val)

            yield clk.negedge
            yield delay(1)

            if (i % len(MC_ROM)) == 3:
                # 4-th command is just copy CR into BusC
                seq_cr.append(c_val)

        # print("TARGET CR:", RAM)
        # print("REAL   CR:", seq_cr)
        assert seq_cr == RAM

        # display_trace_vcd('dist', 'f', trace_res)
        raise StopSimulation()

    return cpu, stimulus, tracer
