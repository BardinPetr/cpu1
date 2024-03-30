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


def get_signals(root):
    return root.sigdict


@myhdl_pytest(gui=True, duration=None)
def test_cpu0():
    for src, comp in zip(MC_ROM, MC_ROM_COMPILED):
        L.info(f"MC{comp:064b}: {src}")

    cpu = CPU(MC_ROM_COMPILED)

    mc_signals = get_signals(get_subs(cpu)['MCSequencer0'])
    dp_signals = get_signals(get_subs(cpu)['DataPath0'])

    print(mc_signals)
    print(dp_signals)

    clk = mc_signals['clk']
    bus_a, bus_b, bus_c = [dp_signals[f'bus_{i}'] for i in ['a', 'b', 'c']]
    mc_pc = mc_signals['mc_pc']
    mc_cr = mc_signals['mc_cr']

    seq_mc_pc = []
    seq_bus_c = []

    delta_b = 2

    # for buses input imitation without real register io
    @always(clk.posedge)
    def run():
        bus_a.next = bus_a + 1
        bus_b.next = bus_b + delta_b

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
            raise Exception("Haven't reached microcode end before 100 ticks")

        # accumulate > 0x20 and then jump to 0x10 in mc rom
        target_pc_seq = [0, 1, 2, 3] * 8 + [0, 1, 10, 11]
        assert target_pc_seq == seq_mc_pc

        target_seq = []
        global_counter = 1
        for i in range(len(seq_bus_c)):
            match i % 4:
                case 0:
                    # bus A is imitating instruction counter, alu is PASS_A
                    target_seq.append(global_counter)
                case 1:
                    # also mirrored bus A, now for check in first jump
                    target_seq.append(global_counter)
                case 2:
                    # C = A + B,   B increases by delta_b each iteration
                    target_seq.append(global_counter + delta_b * global_counter)
                case 3:
                    # second jump zero on alu
                    target_seq.append(0)
            global_counter += 1

        print("REAL C:", seq_bus_c)
        print("TEST C:", target_seq)
        assert target_seq[:-2] == seq_bus_c[:-2]

        raise StopSimulation

    return instances()
