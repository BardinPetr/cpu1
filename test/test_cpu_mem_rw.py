from myhdl import *

from src.arch import *
from src.components.ALU import ALUCtrl, ALUPortCtrl
from src.cpu import CPU
from src.mc.mc import MCInstruction, MCInstructionJump
from utils.introspection import IntrospectionTree, Trace, TraceData
from utils.log import get_logger
from utils.testutils import myhdl_pytest

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

MC_ROM = [
    MCInstruction(
        bus_a_in_ctrl=BusInCtrl.RF_IP,
        alu_ctrl=ALUCtrl.PASSA,
        bus_c_out_ctrl=BusOutCtrl.AR
    ),
    MCInstruction(
        bus_a_in_ctrl=BusInCtrl.DRR,
        alu_ctrl=ALUCtrl.PASSA,
        bus_c_out_ctrl=BusOutCtrl.RF_CR
    ),
    MCInstruction(
        bus_a_in_ctrl=BusInCtrl.RF_IP,
        alu_port_a_ctrl=ALUPortCtrl.INC,
        alu_ctrl=ALUCtrl.PASSA,
        bus_c_out_ctrl=BusOutCtrl.RF_IP
    ),
    MCInstruction(
        bus_a_in_ctrl=BusInCtrl.RF_CR,
        alu_port_b_ctrl=ALUPortCtrl.INC,
        alu_ctrl=ALUCtrl.SHL,
        bus_c_out_ctrl=BusOutCtrl.DRW
    ),
    MCInstruction(
        mem_ctrl=MemCtrl.WR
    ),
    MCInstructionJump(jmp_target=0, jmp_cmp_bit=0, jmp_cmp_val=False),
]

MC_ROM_COMPILED = [i.compile() for i in MC_ROM]


@myhdl_pytest(gui=False, duration=None)
def test_cpu_mem_rw():
    for src, comp in zip(MC_ROM, MC_ROM_COMPILED):
        L.info(f"MC{comp:064b}: {src}")

    LEN = 10
    RAM_SRC = [16 * i + 7 for i in range(LEN)]
    RAM_TARGET = [2 * i for i in RAM_SRC]

    cpu = CPU(MC_ROM_COMPILED, RAM_SRC)
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
        for i in range(len(MC_ROM_COMPILED) * LEN):
            yield clk.posedge

        ram_real = [int(ram[i]) for i in range(len(RAM_TARGET))]

        # print("TARGET RAM:", RAM_TARGET)
        # print("REAL   RAM:", ram_real)
        assert RAM_TARGET == ram_real

        # display_trace_vcd('dist', 'f', trace_res)
        raise StopSimulation()

    return cpu, stimulus, tracer
