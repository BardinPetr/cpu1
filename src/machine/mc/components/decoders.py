from myhdl import *

import src.machine.mc.mcisa as MCLocs
from src.machine.utils.hdl import hdl_block
from src.machine.utils.introspection import introspect
from src.machine.utils.log import get_logger

L = get_logger()


@hdl_block
def ALUDecoder(control_bus, alu_ctrl, alu_port_a_ctrl, alu_port_b_ctrl, alu_flag_ctrl):
    @always_comb
    def run():
        alu_flag_ctrl.next = MCLocs.MCALUFlagCtrl.get(control_bus)
        alu_port_b_ctrl.next = MCLocs.MCALUPortBCtrl.get(control_bus)
        alu_port_a_ctrl.next = MCLocs.MCALUPortACtrl.get(control_bus)
        alu_ctrl.next = MCLocs.MCALUCtrl.get(control_bus)

    return introspect()


@hdl_block
def RegReadDecoder(control_bus, mux_busa_in_ctrl, mux_busb_in_ctrl):
    @always_comb
    def run():
        mux_busa_in_ctrl.next = MCLocs.MCBusACtrl.get(control_bus)
        mux_busb_in_ctrl.next = MCLocs.MCBusBCtrl.get(control_bus)

    return introspect()


@hdl_block
def RegWriteDecoder(
    clk, control_bus, ram_a_wr, reg_ps_wr, register_wr, register_demux_id
):
    @always(clk.posedge)
    def select():
        c_out_ctrl = MCLocs.MCBusCCtrl.get(control_bus)

    @always(clk.negedge)
    def write():
        is_exec_cmd = MCLocs.MCLType.get(control_bus) == MCLocs.MCType.MC_RUN

        c_out_ctrl = MCLocs.MCBusCCtrl.get(control_bus)
        register_wr.next = is_exec_cmd & (c_out_ctrl != 0)
        register_demux_id.next = c_out_ctrl

        ram_ctrl = MCLocs.MCMemCtrl.get(control_bus)[0]
        ram_a_wr.next = is_exec_cmd & ram_ctrl

        alu_flag_ctrl = MCLocs.MCALUFlagCtrl.get(control_bus)
        reg_ps_wr.next = is_exec_cmd & (alu_flag_ctrl != 0)

    @always(clk.posedge)
    def reset():
        register_wr.next = 0

    return introspect()


@hdl_block
def StackDecoder(
    clk, control_bus, d_stack_shift, d_stack_wr, r_stack_shift, r_stack_wr
):
    @always_comb
    def run():
        is_exec_cmd = MCLocs.MCLType.get(control_bus) == MCLocs.MCType.MC_RUN
        ctrl_d = MCLocs.MCStackDCtrl.get(control_bus)
        ctrl_r = MCLocs.MCStackRCtrl.get(control_bus)

        d_stack_shift.next = ctrl_d[2:].signed()
        r_stack_shift.next = ctrl_r[2:].signed()

        d_stack_wr.next = ctrl_d[2] & is_exec_cmd
        r_stack_wr.next = ctrl_r[2] & is_exec_cmd

    return introspect()
