from myhdl import *

from src.arch import *
from src.components.ALU import ALUCtrl, ALUPortCtrl
from src.cpu import CPU
from src.mc.mc import MCInstruction, MCInstructionJump
from test.test_cpu_mcseq import get_signals
from test.utils import get_first_sub
from utils.log import get_logger
from utils.testutils import myhdl_pytest

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

MC_ROM = [
    MCInstruction(
        bus_a_in_ctrl=BusInCtrl.RF_IP,
        alu_ctrl=ALUCtrl.PASSA,
        bus_c_out_ctrl=BusOutCtrl.AR
    ),
    MCInstruction(
        bus_a_in_ctrl=BusInCtrl.DR,
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
        alu_ctrl=ALUCtrl.PASSA,
    ),
    MCInstructionJump(jmp_target=0, jmp_cmp_bit=0, jmp_cmp_val=False),
]

MC_ROM_COMPILED = [i.compile() for i in MC_ROM]


@myhdl_pytest(gui=False, duration=None)
def test_cpu_mem_read():
    for src, comp in zip(MC_ROM, MC_ROM_COMPILED):
        L.info(f"MC{comp:064b}: {src}")

    LEN = 10
    RAM = [16 * i + 7 for i in range(LEN)]
    cpu = CPU(MC_ROM_COMPILED, RAM)

    mc_signals = get_signals(get_first_sub(cpu, 'MCSequencer'))
    dp = get_first_sub(cpu, 'DataPath')
    dp_signals = get_signals(dp)
    ram_signals = get_signals(get_first_sub(dp, "RAMSyncSP"))

    mem_addr = ram_signals['addr']

    clk = mc_signals['clk']
    bus_a, bus_b, bus_c = [dp_signals[f'bus_{i}'] for i in ['a', 'b', 'c']]

    seq_cr = []

    @instance
    def stimulus():
        mc_ttl = 100
        for i in range(len(MC_ROM_COMPILED) * LEN):
            yield clk.posedge
            yield delay(1)

            c_val = int(bus_c.val)

            yield clk.negedge
            yield delay(1)

            # addr = int(mem_addr.val)
            # print(f"{c_val=:x} {addr=:x}")

            if mc_ttl % 5 == 4:
                # 4-th command is just copy CR into BusC
                seq_cr.append(c_val)

            mc_ttl -= 1

        # print("TARGET CR:", RAM)
        # print("REAL   CR:", seq_cr)

        raise StopSimulation()

    return cpu, stimulus
