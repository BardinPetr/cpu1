from src.config import *
from src.mc.decoders import *
from utils.hdl import hdl_block, dim
from utils.log import get_logger

L = get_logger()


@hdl_block
def RegisterFile(clk, write_enable,
                 out_port0_reg, out_port1_reg, in_port_reg,
                 out_port0_bus, out_port1_bus, in_port_bus,
                 count=8):
    assert count == (1 << dim(out_port0_reg))
    assert count == (1 << dim(out_port1_reg))
    assert count == (1 << dim(in_port_reg))

    registers = [Signal(intbv(0)[REG_SZ:]) for _ in range(count)]

    @always_comb
    def read():
        out_port0_bus.next = registers[out_port0_reg]
        out_port1_bus.next = registers[out_port1_reg]

    @always(write_enable.posedge)
    def write():
        L.debug(f"Regfile write [{in_port_reg}] = 0x{in_port_bus.val}")
        registers[in_port_reg].next = in_port_bus

    return instances()