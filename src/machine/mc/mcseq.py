from myhdl import *

from src.machine.components.ROM import ROM
from src.machine.config import *
from src.machine.mc.mcisa import *
from src.machine.utils.hdl import Bus
from src.machine.utils.hdl import hdl_block
from src.machine.utils.introspection import introspect
from src.machine.utils.log import get_logger

L = get_logger()


@hdl_block
def MCSequencer(clk, mc_cr, cpu_bus_c, mc_rom_data):
    mc_pc = Bus(MC_ADDR_SZ)

    mc_rom = ROM(
        clk,
        mc_pc,
        mc_cr,
        mc_rom_data
    )

    @always(clk.negedge)
    def load():
        L.debug(f"UPC: {int(mc_pc):010b} UCR: {int(mc_cr):064b}")

        match MCLType.get(mc_cr):
            case MCType.MC_RUN:
                mc_pc.next = mc_pc + 1

            case MCType.MC_JMP:
                bit = MCJmpCmpBit.get(mc_cr)
                val = MCJmpCmpVal.get(mc_cr)
                jmp = MCJmpTarget.get(mc_cr)

                skip = cpu_bus_c[bit] ^ val
                if skip:
                    mc_pc.next = mc_pc + 1
                else:
                    mc_pc.next = jmp

                L.debug(
                    f"JMP IF BUSC[{bit}] == {val} TO {jmp} -- (cur {cpu_bus_c[bit]:b}) => {'SKIP' if skip else 'JUMP'}")

    return introspect()
