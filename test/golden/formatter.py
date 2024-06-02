from tabulate import tabulate

from compiler.main import ForthCompilationArtifact
from machine.utils.introspection import TraceData


def format_test_code_output(fca: ForthCompilationArtifact) -> str:
    return "\n".join(
        f"{i:03d}: {line}"
        for i, line in enumerate(fca.flat)
        if not isinstance(line, int)
    )


def format_test_trace_output(trace: TraceData):
    checkpoints = [[str(i) for i in cp] for cp in trace.as_list()]

    return tabulate(
        checkpoints,
        headers=trace.labels,
        tablefmt="github",
        stralign="left",
    )
