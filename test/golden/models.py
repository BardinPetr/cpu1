from dataclasses import dataclass

from compiler.main import ForthCompilationArtifact
from machine.utils.introspection import TraceData


@dataclass
class MachineTestSpec:
    forth: str
    stdin: str
    sim_time_limit: int = 100000
    gui: bool = False


@dataclass
class MachineTestReport:
    trace_tick: TraceData
    trace_instr: TraceData
    stdout: str
    code: ForthCompilationArtifact
