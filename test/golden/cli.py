#!/usr/bin/env python

import io
import os
from argparse import ArgumentParser
from os import path

from machine.utils.introspection import TraceData
from machine.utils.log import get_logger
from machine.utils.runutils import run_sim, display_trace_vcd
from test.golden.formatter import format_test_trace_output
from test.golden.testbench import machine_testbench

L = get_logger()

if __name__ == "__main__":
    parser = ArgumentParser(description="CLI machine integration test runner")
    parser.add_argument("ram_file", type=str, help="RAM image binary file")
    parser.add_argument("-i", "--stdin", type=str, help="Input text source file")
    parser.add_argument(
        "-o", "--stdout", type=str, help="File to which to store model output"
    )
    parser.add_argument(
        "-t",
        "--trace",
        type=str,
        help="Directory path where would be placed instruction- and tick-level traces and VCD files",
    )
    parser.add_argument(
        "-g", "--gtkwave", action="store_true", help="Launch gtkwave with traces"
    )

    args = parser.parse_args()

    with open(args.ram_file, "rb") as f:
        mem_binary = f.read()

    if args.stdin:
        input_text = open(args.stdin, "r").read()
    else:
        input_text = ""

    io_input_buffer, io_output_buffer = io.StringIO(input_text), io.StringIO()

    tick_trace_data, inst_trace_data = (
        TraceData(include_time=True),
        TraceData(period_ns=20, include_time=True),
    )
    dut = machine_testbench(
        dict(
            ram=mem_binary,
            io_input=io_input_buffer,
            io_output=io_output_buffer,
            io_input_delay=0,
            io_output_delay=0,
        ),
        tick_trace_data,
        inst_trace_data,
    )

    # Run testbench
    run_sim(dut, duration=10000, gtk_wave=args.gtkwave)

    if args.gtkwave:
        display_trace_vcd("dist", "instr_trace", inst_trace_data)
        display_trace_vcd("dist", "tick_trace", tick_trace_data)

    if args.trace:
        try:
            os.mkdir(args.trace)
        except FileExistsError:
            pass

        inst_trace_data.as_vcd(path.join(args.trace, "trace_instr.vcd"))
        tick_trace_data.as_vcd(path.join(args.trace, "trace_tick.vcd"))
        with open(path.join(args.trace, "trace_instr.md"), "w") as f:
            f.write(format_test_trace_output(inst_trace_data))
        with open(path.join(args.trace, "trace_tick.md"), "w") as f:
            f.write(format_test_trace_output(tick_trace_data))

    L.info(f"Instructions executed {len(inst_trace_data)}")
    L.info(f"Ticks executed {len(tick_trace_data) // 2}")

    if args.stdout:
        with open(args.stdout, "w") as f:
            f.write(io_output_buffer.getvalue())
