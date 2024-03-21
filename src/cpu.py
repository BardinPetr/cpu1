from typing import Optional, List

from myhdl import *

from src.components.ALU import ALUCtrl, ALUPortCtrl
from src.components.base import Register, Clock
from src.datapath.datapath import DataPath
from src.mc.mc import MCInstruction, MCInstructionJump
from src.mc.mcisa import MCType
from src.mc.mcseq import MCSequencer
from utils.hdl import hdl_block, Bus

from src.config import *
from utils.runutils import run_sim

MC_ROM = [
]


@hdl_block
def CPU(mc_rom: List[int]):
    # control module base clock
    clk = Signal(False)
    clg = Clock(clk, 10)

    # control buses
    control_bus = Bus(CONTROL_BUS_SZ)

    # general-purpose buses
    bus_a = Bus(DATA_BITS)
    bus_b = Bus(DATA_BITS)
    bus_c = Bus(DATA_BITS)

    # submodules
    control = MCSequencer(clk, control_bus, bus_c, mc_rom_data=mc_rom)
    datapath = DataPath(control_bus, bus_a, bus_b, bus_c)

    return instances()


if __name__ == "__main__":
    compiled = [i.compile() for i in MC_ROM]

    for src, comp in zip(MC_ROM, compiled):
        print(f"{comp:040b}: {src}")

    cpu = CPU(compiled)
    run_sim(cpu, 1000, True)
