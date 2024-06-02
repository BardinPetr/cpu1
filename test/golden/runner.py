import io
import logging

from compiler.main import compile_forth
from machine.utils.introspection import TraceData
from machine.utils.log import get_logger
from machine.utils.runutils import run_sim
from test.golden.models import MachineTestReport, MachineTestSpec
from test.golden.testbench import machine_testbench

L = get_logger()


def add_log_stream(output):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(output)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(handler)


def execute_test(spec: MachineTestSpec) -> MachineTestReport:
    log_output = io.StringIO()
    add_log_stream(log_output)

    # Compile code
    fca = compile_forth(spec.forth)

    # Prepare testbench
    io_input_buffer, io_output_buffer = io.StringIO(spec.stdin), io.StringIO()
    tick_trace_data, inst_trace_data = (
        TraceData(include_time=True),
        TraceData(period_ns=20, include_time=True),
    )

    dut = machine_testbench(
        dict(
            ram=fca.mem_binary,
            io_input=io_input_buffer,
            io_output=io_output_buffer,
            io_input_delay=0,
            io_output_delay=0,
        ),
        tick_trace_data,
        inst_trace_data,
    )

    # Run testbench
    run_sim(dut, duration=spec.sim_time_limit, gtk_wave=spec.gui)

    # create report
    out_text = io_output_buffer.getvalue()
    logs = log_output.getvalue()
    return MachineTestReport(
        trace_tick=tick_trace_data,
        trace_instr=inst_trace_data,
        stdout=out_text,
        code=fca,
        logs=logs,
    )
