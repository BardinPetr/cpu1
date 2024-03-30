from src.components.ALU import ALU
from src.components.mux import Mux
from src.config import *
from src.datapath.regfile import RegisterFile
from src.mc.decoders import *
from utils.hdl import hdl_block, Bus, create_reg_signals
from utils.log import get_logger

L = get_logger()


@hdl_block
def DataPath(clk, control_bus, bus_a, bus_b, bus_c):
    """
    Description of CPU datapath
    """

    ########################################################################
    """REGISTERS SECTION"""
    # register signals
    reg_ps_in, reg_ps_out, reg_ps_wr = create_reg_signals(REG_SZ)

    regfile_wr = Signal(False)
    regfile_out0_id, regfile_out1_id, regfile_in_id = [Bus(REGFILE_CTRL_SZ) for _ in range(3)]
    regfile_out0, regfile_out1, regfile_in = [Bus() for _ in range(3)]

    # registers
    rf = RegisterFile(
        clk, regfile_wr,
        regfile_out0_id, regfile_out1_id, regfile_in_id,
        regfile_out0, regfile_out1, regfile_in,
        count=REGFILE_COUNT
    )

    ########################################################################
    """BUS INPUT SECTION"""
    mux_bus_a_reg_in_ctrl, mux_bus_b_reg_in_ctrl = Bus(2), Bus(2)
    mux_bus_a_rfnr_ctrl, mux_bus_b_rfnr_ctrl = Bus(1), Bus(1)
    tmp_bus_a_sig, tmp_bus_b_sig = Bus(REG_SZ), Bus(REG_SZ)

    mux_bus_a_registers_in = Mux(
        [reg_ps_out, reg_ps_out, reg_ps_out, reg_ps_out],
        tmp_bus_a_sig, mux_bus_a_reg_in_ctrl
    )
    mux_bus_b_registers_in = Mux(
        [reg_ps_out, reg_ps_out, reg_ps_out, reg_ps_out],
        tmp_bus_b_sig, mux_bus_b_reg_in_ctrl
    )

    mux_bus_a_rf_nr = Mux(
        [tmp_bus_a_sig, regfile_out0],
        bus_a, mux_bus_a_rfnr_ctrl
    )
    mux_bus_b_rf_nr = Mux(
        [tmp_bus_b_sig, regfile_out1],
        bus_b, mux_bus_b_rfnr_ctrl
    )

    ########################################################################
    """ALU SECTION"""
    # ALU control signals
    alu_ctrl = Bus(ALU_CTRL_BUS_SZ)
    alu_flag_ctrl = Bus(ALU_CTRL_FLAG_BUS_SZ)
    alu_ctrl_pa, alu_ctrl_pb = [Bus(ALU_CTRL_PORT_BUS_SZ) for _ in range(2)]

    # ALU module
    alu = ALU(
        alu_ctrl, alu_ctrl_pa, alu_ctrl_pb,
        bus_a, bus_b,
        bus_c,
        alu_flag_ctrl,
        reg_ps_out,
        reg_ps_in
    )

    ########################################################################
    """CONTROL SECTION"""
    alu_dec = ALUDecoder(
        # clk,
        control_bus,
        alu_ctrl, alu_ctrl_pa, alu_ctrl_pb, alu_flag_ctrl
    )

    reg_r_dec = RegReadDecoder(
        # clk,
        control_bus,
        mux_bus_a_rfnr_ctrl, mux_bus_b_rfnr_ctrl,
        mux_bus_a_reg_in_ctrl, mux_bus_b_reg_in_ctrl,
        regfile_out0_id, regfile_out1_id
    )

    reg_w_dec = RegWriteDecoder(
        clk,
        control_bus,
        reg_ps_wr,
        regfile_wr, regfile_in_id
    )

    return instances()
