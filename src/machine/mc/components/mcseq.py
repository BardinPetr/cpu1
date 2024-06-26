from myhdl import StopSimulation, always, always_comb

import src.machine.mc.mcisa as MCLocs
from machine.arch import MachineCtrl
from src.machine.components.ROM import ROM
from src.machine.config import MC_ADDR_SZ
from src.machine.utils.hdl import Bus
from src.machine.utils.hdl import hdl_block
from src.machine.utils.introspection import introspect
from src.machine.utils.log import get_logger

L = get_logger()


@hdl_block
def MCSequencer(clk, clk_dp, clk_dp_wr, mc_cr, cpu_bus_c, mc_rom_data):
    mc_pc = Bus(MC_ADDR_SZ)

    mc_rom = ROM(clk, mc_pc, mc_cr, mc_rom_data)

    @always_comb
    def dp_clg():
        clk_dp.next = clk
        clk_dp_wr.next = clk

    @always(clk.negedge)
    def load():
        L.debug(f"UPC: {int(mc_pc):010b} UCR: {int(mc_cr):064b}")

        is_exec = MCLocs.MCLType.get(mc_cr) == MCLocs.MCType.MC_RUN

        do_halt = MCLocs.MCMachineCtrl.get(mc_cr) & MachineCtrl.HALT
        if do_halt and is_exec:
            raise StopSimulation("Stopped at HALT instruction")

        if is_exec:
            mc_pc.next = mc_pc + 1
        else:
            bit = MCLocs.MCJmpCmpBit.get(mc_cr)
            val = MCLocs.MCJmpCmpVal.get(mc_cr)
            jmp = MCLocs.MCJmpTarget.get(mc_cr)

            skip = cpu_bus_c[bit] ^ val
            if skip:
                mc_pc.next = mc_pc + 1
            else:
                mc_pc.next = jmp

            L.debug(
                f"JMP IF BUSC[{bit}] == {val} TO {jmp} -- (cur {cpu_bus_c[bit]:b}) => {'SKIP' if skip else 'JUMP'}"
            )

    return introspect()
