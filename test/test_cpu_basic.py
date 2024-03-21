from myhdl import *

from src.components.ALU import ALUCtrl, ALUPortCtrl
from src.cpu import CPU
from src.mc.mc import MCInstruction, MCInstructionJump
from src.mc.mcisa import MCType
from utils.log import get_logger
from utils.testutils import myhdl_pytest

L = get_logger()

MC_ROM = [
    MCInstruction(MCType.MC_RUN, ALUCtrl.PASSA, 0b1111, ALUPortCtrl.PASS, ALUPortCtrl.PASS),
    MCInstructionJump(MCType.MC_JMP, ALUCtrl.PASSA, 0, 0, 0, 0, 5, 1, 10),
    MCInstruction(MCType.MC_RUN, ALUCtrl.ADD, 0b1111, ALUPortCtrl.PASS, ALUPortCtrl.PASS),
    MCInstructionJump(MCType.MC_JMP, 0, 0, 0, 0, 0, 0, 0, 0)
]

MC_ROM_COMPILED = [i.compile() for i in MC_ROM]

for src, comp in zip(MC_ROM, MC_ROM_COMPILED):
    print(f"{comp:040b}: {src}")


def get_subs(root):
    return {i.name: i for i in root.subs}


def get_signals(root):
    return root.sigdict


@myhdl_pytest(gui=False, duration=None)
def test_cpu0():
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

    @always(clk.posedge)
    def run():
        bus_a.next = bus_a + 1
        bus_b.next = bus_b + delta_b

    @always_comb
    def check_bus_c():
        seq_bus_c.append(int(bus_c))

    @always_comb
    def check_mcpc():
        seq_mc_pc.append(int(mc_pc))

    @instance
    def stimulus():
        mc_ttl = 100
        while mc_ttl > 0:
            yield clk.negedge
            yield delay(1)

            if mc_cr == 0:
                break

            mc_ttl -= 1
        else:
            raise Exception("Haven't reached microcode end before 100 ticks")

        # accumulate > 0x20 and then jump to 0x10 in mc rom
        target_pc_seq = [0, 1, 2, 3] * 8 + [0, 1, 10, 11]
        assert target_pc_seq == seq_mc_pc

        # print(seq_mc_pc)
        # print(seq_bus_c)

        global_counter = 0
        for i, c in enumerate(seq_bus_c[:-2]):
            match i % 4:
                case 0:
                    # second jump zero on alu
                    assert 0 == c
                case 1:
                    # bus A is imitating instruction counter, alu is PASS_A
                    assert global_counter == c
                case 2:
                    # also mirrored bus A, now for check in first jump
                    assert global_counter == c
                case 3:
                    # C = A + B,   B increases by delta_b each iteration
                    assert (global_counter + delta_b * global_counter) == c
            global_counter += 1

        raise StopSimulation

    return instances()
