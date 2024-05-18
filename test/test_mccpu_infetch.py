from myhdl import *

from isa.main import compile_instructions, Opcode
from isa.model.instructions import Instr
from machine.utils.runutils import display_trace_vcd
from src.machine import CPU
from src.machine import RegFileIdCtrl
from src.machine import get_logger
from src.machine.mc.code import mcrom
from src.machine.utils.introspection import IntrospectionTree, Trace, TraceData
from src.machine.utils.testutils import skip_clk, myhdl_pytest

L = get_logger()

RAM = compile_instructions([
    Instr(Opcode.ADD),
    Instr(Opcode.SUB)
])


@myhdl_pytest(gui=False, duration=None)
def test_cpu_wmc_infetch():
    cpu = CPU(mcrom.ROM, ram=RAM)
    print(RAM)

    intro = IntrospectionTree.build(cpu)
    dp = intro.datapath
    clk = intro.clk
    ip = dp.rf.registers[RegFileIdCtrl.IP]

    trace_res = TraceData()
    tracer = Trace(
        intro.clk,
        trace_res,
        {
            "CLK":    clk,
            "A":      dp.bus_a,
            "B":      dp.bus_b,
            "C":      dp.bus_c,
            "IP":     ip,
            "CR":     dp.rf.registers[RegFileIdCtrl.CR],
            "DS_S":   dp.d_stack.in_shift,
            "DS_W":   dp.d_stack.in_wr_top,
            "DS_IN":  dp.d_stack_in,
            "DS_TOP": dp.d_stack_tos0,
            "DS_PRV": dp.d_stack_tos1,
            "DS_SP":  dp.d_stack.sp,
            "RS_TOP": dp.r_stack_tos0,
            "RS_SP":  dp.r_stack.sp,
        }
    )

    @instance
    def stimulus():
        while ip != 0xa:
            yield clk.negedge

        display_trace_vcd('dist', 'f', trace_res)
        raise StopSimulation()

    return cpu, stimulus, tracer
