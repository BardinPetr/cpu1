from myhdl import *

from src.machine import CPU
from src.machine import get_logger
from src.machine.utils.introspection import IntrospectionTree, Trace, TraceData
from src.machine.utils.testutils import myhdl_pytest
from src.mcasm.parse import mc_compile

L = get_logger()

"""
Each cycle:
    AR  <- IP
    CR  <- DRR
    DRW <- CR << 1
    WRITE MEM 
    IP  <- IP + 1
    
(should double all ram values inplace)
"""

MC_ROM = mc_compile("""
(IP PASSA) -> AR;
(DRR PASSA) -> CR;
(IP(INC) PASSA) -> IP;
(CR SHL IGNORE(INC)) -> DRW;
store;
jump 0;
""").compiled


@myhdl_pytest(gui=False, duration=None)
def test_cpu_mem_rw():
    for src, comp in zip(MC_ROM, MC_ROM):
        L.info(f"MC{comp:064b}: {src}")

    LEN = 10
    RAM_SRC = [16 * i + 7 for i in range(LEN)]
    RAM_TARGET = [2 * i for i in RAM_SRC]

    cpu = CPU(MC_ROM, RAM_SRC)
    intro = IntrospectionTree.build(cpu)

    clk = intro.clk
    ram = intro.datapath.ram_mod.memory

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
            **{f"M{i}": ram[i] for i in range(LEN)}
        }
    )

    @instance
    def stimulus():
        for i in range(len(MC_ROM) * LEN):
            yield clk.posedge

        ram_real = [int(ram[i]) for i in range(len(RAM_TARGET))]

        # print("TARGET RAM:", RAM_TARGET)
        # print("REAL   RAM:", ram_real)
        assert RAM_TARGET == ram_real

        # display_trace_vcd('dist', 'f', trace_res)
        raise StopSimulation()

    return cpu, stimulus, tracer
