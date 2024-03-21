from myhdl import *

from utils.hdl import hdl_block
from utils.log import get_logger

L = get_logger()


@hdl_block
def ALUDecoder(control_bus, alu_ctrl, alu_port_a_ctrl, alu_port_b_ctrl, alu_flag_ctrl):
    @always_comb
    def run():
        alu_ctrl.next = control_bus[:]
        alu_port_a_ctrl.next = control_bus[:]
        alu_port_b_ctrl.next = control_bus[:]
        alu_flag_ctrl.next = control_bus[:]

    return run


@hdl_block
def RegWriteDecoder(
        control_bus,
        reg_cr_wr, reg_ps_wr, reg_ip_wr,
        reg_alu_a_wr, reg_alu_b_wr, reg_alu_o_wr
):
    @always_comb
    def run():
        pass

    return run


@hdl_block
def RegReadDecoder(
        control_bus,
        reg_cr_wr, reg_ps_wr, reg_ip_wr,
        reg_alu_a_wr, reg_alu_b_wr, reg_alu_o_wr
):
    @always_comb
    def run():
        pass

    return run
