from enum import auto

from myhdl import *

from src.machine.mc.mcisa import *
from src.machine.utils.hdl import hdl_block
from src.machine.utils.introspection import introspect
from src.machine.utils.log import get_logger

L = get_logger()


class MainBusCtrl(IntEnum):
    ZERO = 0
    PASSA = auto()


@hdl_block
def ALUDecoder(
        control_bus,
        alu_ctrl, alu_port_a_ctrl, alu_port_b_ctrl, alu_flag_ctrl
):
    @always_comb
    def run():
        alu_flag_ctrl.next = MCALUFlagCtrl.get(control_bus)
        alu_port_b_ctrl.next = MCALUPortBCtrl.get(control_bus)
        alu_port_a_ctrl.next = MCALUPortACtrl.get(control_bus)
        alu_ctrl.next = MCALUCtrl.get(control_bus)

    return introspect()


@hdl_block
def RegReadDecoder(
        control_bus,
        mux_busa_nr_rf_ctrl, mux_busb_nr_rf_ctrl,
        mux_busa_in_ctrl, mux_busb_in_ctrl,
        regfile_out0_id, regfile_out1_id
):
    @always_comb
    def run():
        rd_a = MCBusACtrl.get(control_bus)
        rd_b = MCBusBCtrl.get(control_bus)

        # if rd_X[3] == 1 then  rd_X[3:] is regfile register, else register source
        mux_busa_nr_rf_ctrl.next = rd_a[3]
        mux_busb_nr_rf_ctrl.next = rd_b[3]
        mux_busa_in_ctrl.next = rd_a[3:]
        mux_busb_in_ctrl.next = rd_b[3:]
        regfile_out0_id.next = rd_a[3:]
        regfile_out1_id.next = rd_b[3:]

    return introspect()


@hdl_block
def RegWriteDecoder(
        clk,
        control_bus,
        ram_a_wr,
        reg_ps_wr_drv,
        register_wr, register_demux_id, demux_bus_c_nr_rf,
        regfile_wr, regfile_in_id
):
    @always_comb
    def update():
        mem_ctrl = MCMemCtrl.get(control_bus)
        ram_a_wr.next = mem_ctrl[0]

        wr_ctrl = MCBusCCtrl.get(control_bus)
        regfile_in_id.next = wr_ctrl[3:]
        register_demux_id.next = wr_ctrl[3:]
        demux_bus_c_nr_rf.next = wr_ctrl[3]

        enable = wr_ctrl != 0

        # if wr_ctrl[2] == 1 then  wr_ctrl[2:] is regfile register, else register source
        # regfile write occurring on neg edge of clk!
        regfile_wr.next = enable and wr_ctrl[3]

    @always(clk.negedge)
    def run():
        wr_ctrl = MCBusCCtrl.get(control_bus)

        register_wr.next = (wr_ctrl != 0) and (not wr_ctrl[3])

        # if alu has any flag outputs, then set write to PS register directly
        alu_flag_ctrl = MCALUFlagCtrl.get(control_bus)
        if alu_flag_ctrl > 0:
            reg_ps_wr_drv.next = True
        else:
            reg_ps_wr_drv.next = None

    @always(clk.posedge)
    def reset():
        register_wr.next = 0

    return introspect()


@hdl_block
def StackDecoder(
        clk,
        control_bus,
        d_stack_shift, d_stack_wr,
        r_stack_shift, r_stack_wr
):
    @always_comb
    def run():
        ctrl_d = MCStackDCtrl.get(control_bus)
        ctrl_r = MCStackRCtrl.get(control_bus)
        d_stack_wr.next = ctrl_d[2]
        r_stack_wr.next = ctrl_r[2]
        d_stack_shift.next = ctrl_d[2:].signed()
        r_stack_shift.next = ctrl_r[2:].signed()

    return introspect()
