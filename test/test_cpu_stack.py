from myhdl import *

from src.machine import CPU
from src.machine import RegFileIdCtrl
from src.machine import get_logger
from src.machine.utils.introspection import IntrospectionTree, TraceTick, TraceData
from src.machine.utils.testutils import myhdl_pytest
from src.mcasm.parse import mc_compile

L = get_logger()


@myhdl_pytest(gui=False, duration=None)
def test_cpu_stack():
    """
    implemented function is equivalent to:
    while True:
    TODO
    """

    MC_ROM = mc_compile("""
        (Z(INC) ADD), push(D);
        (Z(INC) ADD), push(D);
        loop:
        (DSS ADD DST), push(R);
        pop(D); 
        pop(D); 
        (RST ADD), push(D);
        pop(R);
        (DST(INC) ADD), push(D);
        jmp loop;
    """).compiled

    for src, comp in zip(MC_ROM, MC_ROM):
        L.info(f"MC{comp:064b}: {src}")

    cpu = CPU(MC_ROM)

    intro = IntrospectionTree.build(cpu)
    dp = intro.datapath
    clk = intro.clk

    trace_res = TraceData()
    tracer = TraceTick(
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


@myhdl_pytest(gui=False, duration=None)
def test_cpu_stack_rep():
    MC_ROM = mc_compile("""
        (Z(INC) ADD) push(D);
        (Z(INC) ADD Z(INC)) push(D);
        (DSS ADD DST) rep(D); 
        (DSS SHL DST) poprep(D); 
        pop(D);
    """).compiled

    for src, comp in zip(MC_ROM, MC_ROM):
        L.info(f"MC{comp:064b}: {src}")

    cpu = CPU(MC_ROM)

    intro = IntrospectionTree.build(cpu)
    dp = intro.datapath
    clk = intro.clk

    trace_res = TraceData()
    tracer = TraceTick(
        intro.clk,
        trace_res,
        {
            "CLK":    clk,
            "IP":     dp.rf.registers[RegFileIdCtrl.IP],
            "DS_TOP": dp.d_stack_tos0,
            "DS_PRV": dp.d_stack_tos1,
            "DS_SP":  dp.d_stack.sp,
        }
    )

    @instance
    def stimulus():
        for i in range(len(MC_ROM) + 1):
            yield clk.negedge
            yield clk.posedge

        a = 2
        b = 1
        target = [b, a, b + a, b << (b + a), 0]

        res = trace_res.peek(0, ['DS_TOP'])
        res = [i['DS_TOP'] for i in res]

        assert res[:len(target)] == target

        # display_trace_vcd('dist', 'f', trace_res)
        raise StopSimulation()

    return cpu, stimulus, tracer
