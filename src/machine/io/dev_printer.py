from sys import stdout
from typing import TextIO

from myhdl import always, delay, instance

from machine.arch import IOBusCtrl
from src.machine.utils.hdl import hdl_block, Bus
from src.machine.utils.introspection import introspect
from src.machine.utils.log import get_logger

L = get_logger()


@hdl_block
def IODevPrinter(
    bus_clk,
    bus_ctrl,
    bus_addr,
    bus_data,
    address,
    address_count,
    output: TextIO = stdout,
    simulate_delay=0,
):
    end_address = address_count + address - 1
    data_drv = bus_data.driver()

    print_control = Bus(bits=2)
    print_value = Bus(bits=32)

    @always(bus_clk.posedge)
    def run():
        if address <= bus_addr <= end_address:
            register = bus_addr - address

            if bus_ctrl & IOBusCtrl.WR:
                L.info(f"WRITE DEV {address:02x} REG {register:02x} VAL {bus_data}")
                if print_control != 0:
                    return  # ignore while busy

                if register == 1:
                    print_control.next = 1
                    print_value.next = 0xFF & bus_data
                elif register == 2:
                    print_control.next = 2
                    print_value.next = bus_data
                else:
                    print_control.next = 0

            if bus_ctrl & IOBusCtrl.RD:
                L.info(f"READ DEV {address:02x} REG {register:02x}")
                if register == 0:  # busy register
                    data_drv.next = print_control != 0
                else:
                    data_drv.next = 0

            if bus_ctrl & IOBusCtrl.TXE:
                data_drv.next = None

    # simulate printing process with timings
    @instance
    def do_print():
        while True:
            yield bus_clk.negedge

            if print_control != 0:
                text = (
                    chr(int(print_value))
                    if print_control == 1
                    else str(int(print_value))
                )
                print(text, file=output, end="")

                yield delay(simulate_delay)
                print_control.next = 0

    return introspect()
