from myhdl import always, always_comb

import src.machine.mc.mcisa as MCLocs
from machine.arch import MachineIOCtrl, IOBusCtrl
from machine.utils.log import get_logger
from src.machine.utils.hdl import hdl_block
from src.machine.utils.introspection import introspect

L = get_logger()


@hdl_block
def IOController(
    clk, clk_out, mc_control, bus_ctrl, bus_addr, bus_data, bus_c, data_output
):
    data_drv = bus_data.driver()

    @always(clk.negedge)
    def execute():
        enable = MCLocs.MCLType.get(mc_control) == MCLocs.MCType.MC_RUN
        ctrl = MCLocs.MCMachineIOCtrl.get(mc_control)

        if not enable or ctrl == MachineIOCtrl.NONE:
            data_drv.next = None
            bus_ctrl.next = 0
            return

        match ctrl:
            case MachineIOCtrl.SET_ADDR:
                L.debug("set addr {}", bus_c.val)
                bus_addr.next = bus_c

            case MachineIOCtrl.SET_DATA:
                L.debug("set data {}", bus_c.val)
                data_drv.next = bus_c

            case MachineIOCtrl.REQ_WRITE:
                L.debug("req write")
                bus_ctrl.next = IOBusCtrl.WR

            case MachineIOCtrl.REQ_READ:
                L.debug("req read")
                bus_ctrl.next = IOBusCtrl.RD

            case MachineIOCtrl.GET_DATA:
                bus_ctrl.next = IOBusCtrl.TXE

    @always(clk.posedge)
    def read():
        enable = MCLocs.MCLType.get(mc_control) == MCLocs.MCType.MC_RUN
        ctrl = MCLocs.MCMachineIOCtrl.get(mc_control)

        if enable and ctrl == MachineIOCtrl.GET_DATA:
            L.info(f"IOCTRL READ FROM {bus_addr} is {bus_data}")
            data_output.next = bus_data

    @always_comb
    def end():
        # generate clock bus with impulse from at command issue
        clk_out.next = ~clk

    return introspect()
