from enum import auto

from myhdl import *

from src.mc.mcisa import *
from utils.hdl import hdl_block
from utils.log import get_logger

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

    return run


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

        # if rd_X[2] == 1 then  rd_X[2:] is regfile register, else register source
        mux_busa_nr_rf_ctrl.next = rd_a[2]
        mux_busb_nr_rf_ctrl.next = rd_b[2]
        mux_busa_in_ctrl.next = rd_a[2:]
        mux_busb_in_ctrl.next = rd_b[2:]
        regfile_out0_id.next = rd_a[2:]
        regfile_out1_id.next = rd_b[2:]

    return instances()


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
        regfile_in_id.next = wr_ctrl[2:]
        register_demux_id.next = wr_ctrl[2:]
        demux_bus_c_nr_rf.next = wr_ctrl[2]

        enable = wr_ctrl != 0

        # if wr_ctrl[2] == 1 then  wr_ctrl[2:] is regfile register, else register source
        # regfile write occurring on neg edge of clk!
        regfile_wr.next = enable and wr_ctrl[2]

    @always(clk.negedge)
    def run():
        wr_ctrl = MCBusCCtrl.get(control_bus)

        register_wr.next = (wr_ctrl != 0) and (not wr_ctrl[2])

        # if alu has any flag outputs, then set write to PS register directly
        alu_flag_ctrl = MCALUFlagCtrl.get(control_bus)
        if alu_flag_ctrl > 0:
            reg_ps_wr_drv.next = True
        else:
            reg_ps_wr_drv.next = None

    return instances()
