from myhdl import *

from machine.cpu import CPU
from machine.utils.log import get_logger
from machine.utils.runutils import display_trace_vcd
from src.machine.utils.introspection import IntrospectionTree, TraceTick, TraceData
from src.machine.utils.testutils import myhdl_pytest
from src.mcasm.parse import mc_compile

L = get_logger()

"""
Each cycle:
    AR  <- IP
    CR  <- DR
    DR <- CR << 1
    WRITE MEM 
    IP  <- IP + 1
    
(should double all ram values inplace)
"""

MC_ROM = mc_compile("""
(IP ADD) -> AR;
(DR ADD) -> CR;
(IP(INC) ADD) -> IP;
(CR SHL Z(INC)) -> DR, store;
jump 0;
""").compiled


@myhdl_pytest(gui=False, duration=None)
def test_cpu_mem_rw():
    LEN = 10
    RAM_SRC = [16 * i + 7 for i in range(LEN)]
    RAM_TARGET = [2 * i for i in RAM_SRC]

    cpu = CPU(MC_ROM, RAM_SRC)
    intro = IntrospectionTree.build(cpu)

    clk = intro.clk_dp
    ram = intro.datapath.ram_mod.memory

    trace_res = TraceData()
    tracer = TraceTick(
        clk,
        trace_res,
        {
            "CLK": intro.clk_dp,
            "MCR": intro.control_bus,
            "A":   intro.datapath.bus_a,
            "B":   intro.datapath.bus_b,
            "C":   intro.datapath.bus_c,
            "AR":     intro.datapath.reg_ar_out,
            "DR":     intro.datapath.reg_dr_out,
            "DRW":    intro.datapath.ram_a_in,
            "RAM_WR": intro.datapath.ram_a_wr,
            **{f"M{i}": ram[i] for i in range(LEN)}
        }
    )

    @instance
    def stimulus():
        for i in range(len(MC_ROM) * LEN):
            yield clk.negedge

        ram_real = [int(ram[i]) for i in range(len(RAM_TARGET))]

        # print("TARGET RAM:", RAM_TARGET)
        # print("REAL   RAM:", ram_real)
        assert ram_real == RAM_TARGET

        # display_trace_vcd('dist', 'f', trace_res)
        raise StopSimulation()

    return cpu, stimulus, tracer
