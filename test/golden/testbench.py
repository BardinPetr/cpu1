from typing import Dict

from machine.main import Machine
from machine.mc.code import mcrom
from machine.utils.hdl import hdl_block
from machine.utils.introspection import TraceData, IntrospectionTree, TraceTick, TraceInstr
from test.golden.introspection import gen_introspection_watches_tick, gen_introspection_watches_inst


@hdl_block
def machine_testbench(
        machine_args: Dict,
        tick_trace_data: TraceData,
        inst_trace_data: TraceData,
):
    machine = Machine(**machine_args)

    intro = IntrospectionTree.build(machine).cpu
    clk = intro.clk_dp

    tick_tracer = TraceTick(
        clk,
        tick_trace_data,
        gen_introspection_watches_tick(intro)
    )

    inst_tracer = TraceInstr(
        clk,
        inst_trace_data,
        gen_introspection_watches_inst(intro),
        intro.control.mc_pc, mc_pc_trigger_value=mcrom.MICROCODE.labels['end']
    )

    return machine, tick_tracer, inst_tracer
