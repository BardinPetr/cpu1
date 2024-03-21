from myhdl import *

from src.components.ALU import ALU
from src.components.base import Register
from src.mc.decoders import *

from utils.hdl import hdl_block, Bus, create_reg_signals
from utils.log import get_logger

from src.config import *

L = get_logger()


@hdl_block
def DataPath(control_bus, bus_a, bus_b, bus_c):
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
    reg_cr_in, reg_cr_out, reg_cr_wr = create_reg_signals(REG_SZ)
    reg_ps_in, reg_ps_out, reg_ps_wr = create_reg_signals(REG_SZ)
    reg_ip_in, reg_ip_out, reg_ip_wr = create_reg_signals(REG_SZ)
    # reg__in, reg__out, reg__wr = create_reg_signals(REG_SZ)

    # registers
    reg_cr = Register(reg_cr_in, reg_cr_out, reg_cr_wr)
    reg_ps = Register(reg_ps_in, reg_ps_out, reg_ps_wr)
    reg_ip = Register(reg_ip_in, reg_ip_out, reg_ip_wr)

    ########################################################################
    """ALU SECTION"""
    # ALU control signals
    alu_ctrl = Bus(ALU_CTRL_BUS_SZ)
    alu_flag_ctrl = Bus(ALU_CTRL_FLAG_BUS_SZ)
    alu_ctrl_pa, alu_ctrl_pb = [Bus(ALU_CTRL_PORT_BUS_SZ) for _ in range(2)]

    # ALU data signals
    alu_in_a, alu_in_b, alu_out = [Bus(DATA_BITS) for _ in range(3)]

    # ALU module
    alu = ALU(
        alu_ctrl, alu_ctrl_pa, alu_ctrl_pb,
        alu_in_a, alu_in_b,
        alu_out,
        alu_flag_ctrl,
        reg_ps_out,
        reg_ps_in
    )

    ########################################################################
    """Temporary registers"""
    # ALU registers signals
    reg_alu_a_wr, reg_alu_b_wr, reg_alu_o_wr = [Signal(False) for _ in range(3)]

    # ALU registers
    reg_alu_a = Register(bus_a, alu_in_a, reg_alu_a_wr)
    reg_alu_b = Register(bus_b, alu_in_b, reg_alu_b_wr)
    reg_alu_o = Register(alu_out, bus_c, reg_alu_o_wr)

    ########################################################################
    """CONTROL SECTION"""
    alu_dec = ALUDecoder(
        control_bus,
        alu_ctrl, alu_ctrl_pa, alu_ctrl_pb, alu_flag_ctrl
    )
    # reg_w_dec = RegWriteDecoder(
    #     control_bus,
    #     reg_cr_wr, reg_ps_wr, reg_ip_wr,
    #     reg_alu_a_wr, reg_alu_b_wr, reg_alu_o_wr
    # )
    # reg_r_dec = RegReadDecoder(
    #     control_bus,
    #     ...  # TODO fill
    # )

    @always_comb
    def update():
        alu_in_a.next = bus_a
        alu_in_b.next = bus_b
        bus_c.next = alu_out

    return instances()
