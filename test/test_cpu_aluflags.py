from myhdl import *

from src.arch import PSFlags
from src.components.ALU import ALUCtrl
from src.cpu import CPU
from src.mc.mc import MCInstruction, MCInstructionJump
from test.utils import *
from utils.log import get_logger
from utils.testutils import myhdl_pytest

L = get_logger()

MC_ROM = [
    MCInstruction(alu_ctrl=ALUCtrl.ADD, alu_flag_ctrl=0b1111),
    MCInstructionJump(jmp_target=0, jmp_cmp_bit=0, jmp_cmp_val=False)
]

MC_ROM_COMPILED = [i.compile() for i in MC_ROM]


@myhdl_pytest(gui=False, duration=None)
def test_cpu_regio():
    for src, comp in zip(MC_ROM, MC_ROM_COMPILED):
        L.info(f"MC{comp:064b}: {src}")

    cpu = CPU(MC_ROM_COMPILED)

    mc_signals = get_signals(get_first_sub(cpu, 'MCSequencer'))
    dp_signals = get_signals(get_first_sub(cpu, 'DataPath'))

    clk = mc_signals['clk']
    bus_a, bus_b, bus_c = [dp_signals[f'bus_{i}'] for i in ['a', 'b', 'c']]
    ps = dp_signals['reg_ps_out']

    AB_IN = [
        (-1, 0),
        (0, 0),
        (1, 0),
        (UINT_MAX, 1),
        (0, negate(1)),
        (SINT_MAX, 1),
        (SINT_MIN, negate(1)),
    ]
    TARGET_PS = [
        dict(Z=False, N=True, C=False, V=False),
        dict(Z=True, N=False, C=False, V=False),
        dict(Z=False, N=False, C=False, V=False),
        dict(C=True),
        dict(N=True),
        dict(V=True),
        dict(V=True),
    ]
    ps_output = []

    @instance
    def stimulus():
        for a, b in AB_IN:
            set_signed(bus_a, a)
            set_signed(bus_b, b)
            yield clk.negedge
            yield clk.posedge

            ps_output.append(PSFlags.decode_flags(ps.val))

            yield clk.negedge
            yield delay(1)

        for real, test in zip(ps_output, TARGET_PS):
            for name, val in test.items():
                assert val == real[name]

        raise StopSimulation()

    return instances()