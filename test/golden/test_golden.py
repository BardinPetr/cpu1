import pytest

from test.golden.formatter import format_test_code_output, format_test_trace_output
from test.golden.models import MachineTestSpec
from test.golden.runner import execute_test
from pytest_golden.plugin import GoldenTestFixture


@pytest.mark.golden_test("golden_def/*.yml")
def test_golden(golden: GoldenTestFixture):
    spec = MachineTestSpec(
        forth=golden["in_forth"],
        stdin=golden["in_stdin"]
    )

    res = execute_test(spec)

    out_code = format_test_code_output(res.code)
    out_trace_tick = format_test_trace_output(res.trace_tick)
    out_trace_instr = format_test_trace_output(res.trace_instr)

    with open(f"test_trace_tick_{golden.path.name}.md", "w") as f:
        f.write(out_trace_tick)
    with open(f"test_trace_instr_{golden.path.name}.md", "w") as f:
        f.write(out_trace_instr)

    assert len(res.trace_tick) and len(res.trace_instr), "Simulation failed"
    assert out_code == golden.out["out_compiled"], "Compiled instruction list mismatch"
    assert res.stdout == golden.out["out_stdout"], "Stdout mismatch"
    assert out_trace_instr == golden.out["out_trace"], "Instruction trace mismatch"
