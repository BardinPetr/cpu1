from myhdl import *

from src.components.ALU import ALU
from src.components.base import Register
from src.components.mux import Mux
from src.datapath.regfile import RegisterFile
from src.mc.decoders import *

from utils.hdl import hdl_block, Bus, create_reg_signals
from utils.log import get_logger

from src.config import *

L = get_logger()


@hdl_block
def DataPath(clk, control_bus, bus_a, bus_b, bus_c):
    """
    Description of CPU datapath
    :param control_bus:
    :param bus_a:
    :param bus_b:
    :param bus_c:
    :return:
    """

    ########################################################################
    """REGISTERS SECTION"""
    # register signals
    reg_ps_in, reg_ps_out, reg_ps_wr = create_reg_signals(REG_SZ)

    regfile_wr = Signal(False)
    regfile_out0_id, regfile_out1_id, regfile_in_id = [Bus(REGFILE_CTRL_SZ) for _ in range()]
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

    mux_busa_in_ctrl, mux_busb_in_ctrl = Bus(2), Bus(2)

    mux_bus_a_in = Mux(
        [regfile_out0, 0, 0, 0],
        bus_a, mux_busa_in_ctrl
    )
    mux_bus_b_in = Mux(
        [regfile_out1, 0, 0, 0],
        bus_a, mux_busb_in_ctrl
    )

    ########################################################################
    """ALU SECTION"""
    # ALU control signals
    alu_ctrl = Bus(ALU_CTRL_BUS_SZ)
    alu_flag_ctrl = Bus(ALU_CTRL_FLAG_BUS_SZ)
    alu_ctrl_pa, alu_ctrl_pb = [Bus(ALU_CTRL_PORT_BUS_SZ) for _ in range(2)]

    # ALU data signals
    # alu_in_a, alu_in_b, alu_out = [Bus(DATA_BITS) for _ in range(3)]

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
    """Temporary registers"""
    # ALU registers signals
    # reg_alu_a_wr, reg_alu_b_wr, reg_alu_o_wr = [Signal(False) for _ in range(3)]

    # ALU registers
    # reg_alu_a = Register(bus_a, alu_in_a, reg_alu_a_wr)
    # reg_alu_b = Register(bus_b, alu_in_b, reg_alu_b_wr)
    # reg_alu_o = Register(alu_out, bus_c, reg_alu_o_wr)

    ########################################################################
    """CONTROL SECTION"""
    alu_dec = ALUDecoder(
        clk,
        control_bus,
        alu_ctrl, alu_ctrl_pa, alu_ctrl_pb, alu_flag_ctrl
    )

    # reg_w_dec = RegWriteDecoder(
    #     control_bus,
    #     reg_ps_wr, regfile_wr,
    # )
    # reg_r_dec = RegReadDecoder(
    #     control_bus,
    #     ...  # TODO fill
    # )

    # @always_comb
    # def update():

    return instances()
