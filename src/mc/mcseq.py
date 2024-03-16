from myhdl import *

from src.components.ALU import ALU
from src.mc.mcisa import *
from utils.hdl import hdl_block, create_int_signal, dim
from utils.log import get_logger

from src.components.ROM import AsyncROM, ROM
from src.components.base import Clock, Trig, RTrig, Counter, Reg
from utils.hdl import create_int_signal
from utils.testutils import myhdl_pytest
from src.config import *

L = get_logger()


def printb(*args):
    print(*[bin(i, dim(i)) for i in args])


@hdl_block
def MCSequencer(clk, mc_cr, cpu_cr, cpu_ps, mc_rom_data):
    mc_pc = create_int_signal(MC_ADDR_SZ)

    mc_rom = ROM(
        clk,
        mc_pc,
        mc_cr,
        mc_rom_data
    )

    @always(clk.negedge)
    def load():
        print("UPC:", mc_pc, "UCR:", mc_cr)

        match mc_get_type(mc_cr):
            case MCType.MC_RUN:
                mc_pc.next = mc_pc + 1

            case MCType.MC_JMP:
                reg = mc_get_cmp_reg(mc_cr)
                bit = mc_get_cmp_bit(mc_cr)
                req = mc_get_cmp_val(mc_cr)
                jmp = mc_get_cmp_jmp(mc_cr)

                print(f"JMP IF R{reg}[{bit}] == {req} TO {jmp}")

                reg_val = intbv(0)[DATA_BITS:]
                match reg:
                    case MCRegId.MC_R_PS:
                        reg_val[:] = cpu_ps
                    case MCRegId.MC_R_CR:
                        reg_val[:] = cpu_cr

                if reg_val[bit] ^ req:
                    mc_pc.next = mc_pc + 1
                else:
                    mc_pc.next = jmp

    return instances()
