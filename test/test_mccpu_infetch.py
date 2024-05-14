from myhdl import *

from machine.arch import RegFileIdCtrl
from machine.cpu import CPU
from machine.mc.code import mcrom
from machine.utils.introspection import IntrospectionTree, Trace, TraceData
from machine.utils.log import get_logger
from machine.utils.runutils import display_trace_vcd
from machine.utils.testutils import myhdl_pytest, skip_clk

L = get_logger()


@myhdl_pytest(gui=False, duration=None)
def test_cpu_wmc_infetch():
    cpu = CPU(mcrom.ROM)

    intro = IntrospectionTree.build(cpu)
    dp = intro.datapath
    clk = intro.clk

    trace_res = TraceData()
    tracer = Trace(
        intro.clk,
        trace_res,
        {
            "CLK":    clk,
            "A":      dp.bus_a,
            "B":      dp.bus_b,
            "C":      dp.bus_c,
            "IP":     dp.rf.registers[RegFileIdCtrl.IP],
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
        yield skip_clk(clk, 10)

        display_trace_vcd('dist', 'f', trace_res)
        raise StopSimulation()

    return cpu, stimulus, tracer
