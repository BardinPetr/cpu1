from sys import stdin
from typing import TextIO

from myhdl import _simulator as sim
from myhdl import always, StopSimulation

from machine.arch import IOBusCtrl
from src.machine.utils.hdl import hdl_block, Bus
from src.machine.utils.introspection import introspect
from src.machine.utils.log import get_logger

L = get_logger()


@hdl_block
def IODevKeyboard(
    bus_clk,
    bus_ctrl,
    bus_addr,
    bus_data,
    address,
    address_count,
    source: TextIO = stdin,
    simulate_delay=0,
):
    end_address = address_count + address - 1
    data_drv = bus_data.driver()
    last_read_time = Bus(bits=128)

    @always(bus_clk.posedge)
    def run():
        if address <= bus_addr <= end_address:
            register = bus_addr - address

            if bus_ctrl & IOBusCtrl.RD:
                L.info(
                    f"READ DEV {address:02x} REG {register:02x} {sim.now():d} {int(last_read_time.val):d}"
                )
                busy = (sim.now() - last_read_time) < simulate_delay

                if register == 0:  # busy register
                    data_drv.next = busy
                elif register == 1:  # char register
                    if busy:
                        data_drv.next = 0xDEADBEEF
                    else:
                        last_read_time.next = sim.now()
                        data = source.read(1)
                        if not data:
                            raise StopSimulation("Ended due to input end")
                        data_drv.next = ord(data) & 0xFF
                else:
                    data_drv.next = 0

            if bus_ctrl & IOBusCtrl.TXE:
                data_drv.next = None

    return introspect()
