import io

from compiler.main import compile_forth
from machine.utils.introspection import TraceData
from machine.utils.log import get_logger
from machine.utils.runutils import run_sim
from test.golden.models import MachineTestReport, MachineTestSpec
from test.golden.testbench import machine_testbench

L = get_logger()


def execute_test(spec: MachineTestSpec) -> MachineTestReport:
    # Compile code
    fca = compile_forth(spec.forth)

    # Prepare testbench
    io_input_buffer, io_output_buffer = io.StringIO(spec.stdin), io.StringIO()
    tick_trace_data, inst_trace_data = TraceData(period_ns=10), TraceData(period_ns=20)

    dut = machine_testbench(
        dict(
            ram=fca.mem_binary,
            io_input=io_input_buffer,
            io_output=io_output_buffer,
            io_input_delay=0,
            io_output_delay=0
        ),
        tick_trace_data,
        inst_trace_data,
    )

    # Run testbench
    run_sim(dut, duration=spec.sim_time_limit)

    # create report
    out_text = io_output_buffer.getvalue()
    return MachineTestReport(
        trace_tick=tick_trace_data,
        trace_instr=inst_trace_data,
        stdout=out_text,
        code=fca
    )


def cli():
    pass
    # display_trace_vcd('dist', 'instr_trace', inst_trace_data)
    # display_trace_vcd('dist', 'tick_trace', tick_trace_data)


if __name__ == "__main__":
    cli()
