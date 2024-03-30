from myhdl import *

from src.components.ALU import ALUCtrl
from src.cpu import CPU
from src.mc.mc import MCInstruction, MCInstructionJump
from utils.log import get_logger
from utils.testutils import myhdl_pytest

L = get_logger()

MC_ROM = [
    MCInstruction(alu_ctrl=ALUCtrl.PASSA),
    MCInstructionJump(alu_ctrl=ALUCtrl.PASSA, jmp_target=10, jmp_cmp_bit=5, jmp_cmp_val=True),
    MCInstruction(alu_ctrl=ALUCtrl.ADD),
    MCInstructionJump(jmp_target=0, jmp_cmp_bit=0, jmp_cmp_val=False),
]

MC_ROM_COMPILED = [i.compile() for i in MC_ROM]


def get_subs(root):
    return {i.name: i for i in root.subs}


def get_first_sub(root, name_prefix):
    subs = get_subs(root)
    try:
        name = next(filter(lambda x: x.startswith(name_prefix), subs.keys()))
        return subs[name]
    except:
        raise Exception(f"No submodule {name_prefix}*")


def get_signals(root):
    return root.sigdict


@myhdl_pytest(gui=False, duration=None)
def test_cpu_regio():
    for src, comp in zip(MC_ROM, MC_ROM_COMPILED):
        L.info(f"MC{comp:064b}: {src}")

    cpu = CPU(MC_ROM_COMPILED)

    mc_signals = get_signals(get_first_sub(cpu, 'MCSequencer'))
    dp_signals = get_signals(get_first_sub(cpu, 'DataPath'))

    print(mc_signals)
    print(dp_signals)

    clk = mc_signals['clk']
    bus_a, bus_b, bus_c = [dp_signals[f'bus_{i}'] for i in ['a', 'b', 'c']]
    mc_pc = mc_signals['mc_pc']
    mc_cr = mc_signals['mc_cr']

    seq_mc_pc = []
    seq_bus_c = []

    @always_comb
    def check_mcpc():
        seq_mc_pc.append(int(mc_pc))

    @instance
    def stimulus():
        mc_ttl = 100
        while mc_ttl > 0:
            yield clk.negedge
            yield delay(1)

            seq_bus_c.append(int(bus_c))

            if mc_cr == 0:
                break

            mc_ttl -= 1
        else:
            raise StopSimulation
            raise Exception("Haven't reached microcode end before 100 ticks")

    return instances()
