from myhdl import *

from src.arch import *
from src.components.ALU import ALUCtrl, ALUPortCtrl
from src.cpu import CPU
from src.mc.mc import MCInstruction, MCInstructionJump
from test.test_cpu_mcseq import get_signals
from test.utils import get_first_sub
from utils import introspection
from utils.introspection import IntrospectionTree
from utils.log import get_logger
from utils.testutils import myhdl_pytest

introspection.use()

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
def test_cpu_mem_read():
    for src, comp in zip(MC_ROM, MC_ROM_COMPILED):
        L.info(f"MC{comp:064b}: {src}")

    LEN = 10
    RAM_SRC = [16 * i + 7 for i in range(LEN)]
    RAM_TARGET = [2 * i for i in RAM_SRC]

    cpu = CPU(MC_ROM_COMPILED, RAM_SRC)

    mc_signals = get_signals(get_first_sub(cpu, 'MCSequencer'))
    dp = get_first_sub(cpu, 'DataPath')
    ram = get_first_sub(dp, "RAMSyncSP")

    clk = mc_signals['clk']

    @instance
    def stimulus():
        for i in range(len(MC_ROM_COMPILED) * LEN):
            yield clk.posedge

        ram_real = ram.memdict['memory'].mem
        ram_real = [int(i) for i in ram_real[:len(RAM_TARGET)]]

        # print("TARGET RAM:", RAM_TARGET)
        # print("REAL   RAM:", ram_real)
        assert RAM_TARGET == ram_real

        raise StopSimulation()

    intro = IntrospectionTree.build(cpu)

    @instance
    def pull():
        while True:
            yield clk.posedge
            yield clk.negedge

    return cpu, stimulus, pull
