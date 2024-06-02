from machine.mc.components.decoders import (
    ALUDecoder,
    RegReadDecoder,
    RegWriteDecoder,
    StackDecoder,
)
from machine.mc.components.mcseq import MCSequencer
from src.machine.utils.hdl import hdl_block
from src.machine.utils.introspection import introspect
from src.machine.utils.log import get_logger

L = get_logger()


@hdl_block
def MCControl(
    clk,
    clk_dp,
    clk_dp_wr,
    control_bus,
    bus_c,
    alu_ctrl,
    alu_ctrl_pa,
    alu_ctrl_pb,
    alu_flag_ctrl,
    mux_bus_a_reg_in_ctrl,
    mux_bus_b_reg_in_ctrl,
    ram_a_wr,
    reg_ps_wr,
    demux_bus_c_reg_id,
    d_stack_shift,
    d_stack_wr,
    r_stack_shift,
    r_stack_wr,
    reg_drw_wr,
    reg_ar_wr,
    reg_ip_wr,
    reg_cr_wr,
    mc_rom_data,
):
    seq = MCSequencer(
        clk, clk_dp, clk_dp_wr, control_bus, bus_c, mc_rom_data=mc_rom_data
    )

    alu_dec = ALUDecoder(control_bus, alu_ctrl, alu_ctrl_pa, alu_ctrl_pb, alu_flag_ctrl)

    reg_r_dec = RegReadDecoder(
        control_bus,
        mux_bus_a_reg_in_ctrl,
        mux_bus_b_reg_in_ctrl,
    )

    reg_w_dec = RegWriteDecoder(
        clk_dp,
        control_bus,
        demux_bus_c_reg_id,
        ram_a_wr,
        reg_ps_wr,
        reg_drw_wr,
        reg_ar_wr,
        reg_ip_wr,
        reg_cr_wr,
    )

    stack_dec = StackDecoder(
        clk_dp, control_bus, d_stack_shift, d_stack_wr, r_stack_shift, r_stack_wr
    )

    return introspect()
