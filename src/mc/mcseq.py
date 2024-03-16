from myhdl import *

from myhdl import *

from src.components.ROM import ROM
from src.config import *
from src.mc.mcisa import *
from utils.hdl import create_int_signal
from utils.hdl import hdl_block
from utils.log import get_logger

L = get_logger()


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
        L.debug(f"UPC: {int(mc_pc):032b} UCR: {int(mc_cr):032b}")

        match mc_get_type(mc_cr):
            case MCType.MC_RUN:
                mc_pc.next = mc_pc + 1

            case MCType.MC_JMP:
                reg = mc_get_cmp_reg(mc_cr)
                bit = mc_get_cmp_bit(mc_cr)
                req = mc_get_cmp_val(mc_cr)
                jmp = mc_get_cmp_jmp(mc_cr)

                reg_val = intbv(0)[DATA_BITS:]
                match reg:
                    case MCRegId.MC_R_PS:
                        reg_val[:] = cpu_ps
                    case MCRegId.MC_R_CR:
                        reg_val[:] = cpu_cr

                skip = reg_val[bit] ^ req
                if skip:
                    mc_pc.next = mc_pc + 1
                else:
                    mc_pc.next = jmp

                L.debug(f"JMP IF R{reg}[{bit}] == {req} TO {jmp}  ->  {'SKIP' if skip else 'JUMP'}")

    return instances()
