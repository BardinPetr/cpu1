from mcasm.parse import mc_compile
from myhdl import *

from machine.arch import RegFileIdCtrl
from machine.cpu import CPU
from machine.utils.introspection import IntrospectionTree, Trace, TraceData
from machine.utils.log import get_logger
from machine.utils.runutils import display_trace_vcd
from machine.utils.testutils import myhdl_pytest

L = get_logger()

"""
implemented function is equivalent to:
while True:
    PUSH(1)
    PUSH(1)
    A = POP()
    B = POP()
    C = A + B
    PUSH(C)
    PUSH(TOP + 1)
"""

MC_ROM = mc_compile("""
(IGNORE(INC) PASSA), push(D);
(IGNORE(INC) PASSA), push(D);
loop:
(D_TOS ADD D_TOS), push(R);
pop(D); 
pop(D); 
(R_TOS PASSA), push(D);
pop(R);
(D_TOS(INC) PASSA), push(D);
jmp loop;
""").compiled


@myhdl_pytest(gui=False, duration=None)
def test_cpu_stack():
    for src, comp in zip(MC_ROM, MC_ROM):
        L.info(f"MC{comp:064b}: {src}")

    cpu = CPU(MC_ROM)

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
        # skip init
        yield clk.negedge
        yield clk.posedge
        yield clk.negedge
        yield clk.posedge

        stack = [1, 1]
        stack_target = []
        cnt = 5
        loop_size = 7
        for i in range(cnt):
            for _ in range(loop_size):
                yield clk.posedge
                yield clk.negedge
            top = stack.pop()
            prv = stack.pop()
            stack.append(top + prv)
            stack.append(1 + stack[-1])
            stack_target.append(tuple(stack))

        stack_real = trace_res.peek(
            front=0,
            names=["DS_PRV", "DS_TOP"]
        )
        stack_real = stack_real[2:]
        stack_real = stack_real[6::loop_size]  # time after 6th instruction in loop (JMP)
        stack_real = [(i["DS_PRV"], i["DS_TOP"]) for i in stack_real]

        # print(stack_real)
        # print(stack_target)
        assert stack_real == stack_target

        # display_trace_vcd('dist', 'f', trace_res)
        raise StopSimulation()

    return cpu, stimulus, tracer
