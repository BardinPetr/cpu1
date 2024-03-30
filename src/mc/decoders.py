from myhdl import *

from src.mc.mcisa import *
from utils.hdl import hdl_block
from utils.log import get_logger

L = get_logger()


@hdl_block
def ALUDecoder(
        clk,
        control_bus,
        alu_ctrl, alu_port_a_ctrl, alu_port_b_ctrl, alu_flag_ctrl
):
    @always(clk.posedge)
    def run():
        alu_flag_ctrl.next = MCALUFlagCtrl.get(control_bus)
        alu_port_b_ctrl.next = MCALUPortBCtrl.get(control_bus)
        alu_port_a_ctrl.next = MCALUPortACtrl.get(control_bus)
        alu_ctrl.next = MCALUCtrl.get(control_bus)

    return run


@hdl_block
def RegWriteDecoder(
        clk,
        control_bus,
        reg_cr_wr, reg_ps_wr, reg_ip_wr,
        reg_alu_a_wr, reg_alu_b_wr, reg_alu_o_wr
):
    @always(clk.posedge)
    def run():
        pass

    return run


@hdl_block
def RegReadDecoder(
        clk,
        control_bus,
        reg_cr_wr, reg_ps_wr, reg_ip_wr,
        reg_alu_a_wr, reg_alu_b_wr, reg_alu_o_wr
):
    @always(clk.posedge)
    def run():
        pass

    return run
