from enum import auto

from myhdl import *

from src.components.mux import DeMux
from src.mc.mcisa import *
from utils.hdl import hdl_block, Bus
from utils.log import get_logger

L = get_logger()


class MainBusCtrl(IntEnum):
    ZERO = 0
    PASSA = auto()


@hdl_block
def ALUDecoder(
        # clk,
        control_bus,
        alu_ctrl, alu_port_a_ctrl, alu_port_b_ctrl, alu_flag_ctrl
):
    # @always(clk.posedge)
    @always_comb
    def run():
        alu_flag_ctrl.next = MCALUFlagCtrl.get(control_bus)
        alu_port_b_ctrl.next = MCALUPortBCtrl.get(control_bus)
        alu_port_a_ctrl.next = MCALUPortACtrl.get(control_bus)
        alu_ctrl.next = MCALUCtrl.get(control_bus)

    return run


@hdl_block
def RegReadDecoder(
        # clk,
        control_bus,
        mux_busa_rfnr_ctrl, mux_busb_rfnr_ctrl,
        mux_busa_in_ctrl, mux_busb_in_ctrl,
        regfile_out0_id, regfile_out1_id
):
    # @always(clk.posedge)
    @always_comb
    def run():
        rd_a = MCBusACtrl.get(control_bus)
        rd_b = MCBusBCtrl.get(control_bus)

        # if rd_X[2] == 1 then  rd_X[2:] is regfile register, else register source
        mux_busa_rfnr_ctrl.next = rd_a[2]
        mux_busb_rfnr_ctrl.next = rd_b[2]
        mux_busa_in_ctrl.next = rd_a[2:]
        mux_busb_in_ctrl.next = rd_b[2:]
        regfile_out0_id.next = rd_a[2:]
        regfile_out1_id.next = rd_b[2:]

    return instances()


@hdl_block
def RegWriteDecoder(
        clk,
        control_bus,
        reg_ps_wr,
        regfile_wr, regfile_in_id
):
    register_wr_cmd = Signal(False)
    register_demux_id = Bus(2)
    demux = DeMux(
        register_wr_cmd,
        [reg_ps_wr],
        register_demux_id
    )

    @always(clk.negedge)
    def run():
        wr_ctrl = MCBusCCtrl.get(control_bus)

        enable = wr_ctrl != MainBusInCtrl.IGNORE

        # if wr_ctrl[2] == 1 then  wr_ctrl[2:] is regfile register, else register source
        register_wr_cmd.next = enable and (not wr_ctrl[2])
        regfile_wr.next = enable and wr_ctrl[2]

        regfile_in_id.next = wr_ctrl[2:]
        register_demux_id.next = wr_ctrl[2:]

    return instances()
