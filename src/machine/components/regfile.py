from myhdl import always_comb, always

from src.machine.config import REG_SZ
from src.machine.utils.hdl import hdl_block, dim, Bus
from src.machine.utils.introspection import introspect
from src.machine.utils.log import get_logger

L = get_logger()


@hdl_block
def RegisterFile(
    clk,
    write_enable,
    out_port0_reg,
    out_port1_reg,
    in_port_reg,
    out_port0_bus,
    out_port1_bus,
    in_port_bus,
    count=8,
):
    assert count == (1 << dim(out_port0_reg))
    assert count == (1 << dim(out_port1_reg))
    assert count == (1 << dim(in_port_reg))

    registers = [Bus(bits=REG_SZ) for _ in range(count)]

    @always_comb
    def read():
        out_port0_bus.next = registers[out_port0_reg]
        out_port1_bus.next = registers[out_port1_reg]

    @always(clk.negedge)
    def write():
        if write_enable:
            L.debug(f"Regfile write [{in_port_reg}] = 0x{in_port_bus.val}")
            registers[in_port_reg].next = in_port_bus

    return introspect()
