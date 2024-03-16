from myhdl import *

from src.components.ALU import ALU
from utils.hdl import hdl_block, create_int_signal
from utils.log import get_logger

L = get_logger()


@hdl_block
def DataPath():
    # ALU block
    alu_port_a, alu_port_b, alu_port_out = [create_int_signal() for _ in range(3)]
    # alu = ALU(_, _, _, alu_port_a, alu_port_b, alu_port_out, _, _)

    return instances()
