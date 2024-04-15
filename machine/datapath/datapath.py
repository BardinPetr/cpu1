from machine.arch import RegFileIdCtrl, RegFileOrNormalRegister
from machine.components.ALU import ALU
from machine.components.RAM import RAMSyncSP
from machine.components.base import Register
from machine.components.mux import Mux, DeMux
from machine.config import *
from machine.datapath.regfile import RegisterFile
from machine.mc.decoders import *
from machine.utils.hdl import hdl_block, Bus, create_reg_signals, Bus1
from machine.utils.introspection import introspect
from machine.utils.log import get_logger

L = get_logger()


@hdl_block
def DataPath(clk, control_bus, bus_a, bus_b, bus_c, ram=None):
    """
    Description of CPU datapath
    """
    zerobus = Bus(DATA_BITS, state=0)

    ########################################################################
    """REGISTERS SECTION"""
    # classic registers
    # Program State register (see PSFlags)
    reg_ps_out = Bus(REG_PS_SZ)
    reg_ps_wr = TristateSignal(intbv(0)[1:])
    reg_ps_in = TristateSignal(intbv(0)[REG_PS_SZ:])
    reg_ps = Register(reg_ps_in, reg_ps_out, reg_ps_wr)

    # register tied to ram input addr
    reg_ar_in, reg_ar_out, reg_ar_wr = create_reg_signals(REG_SZ)
    reg_ar = Register(reg_ar_in, reg_ar_out, reg_ar_wr)

    """REGISTER FILE SECTION"""
    regfile_wr = Bus1()
    regfile_out0_id, regfile_out1_id, regfile_in_id = [Bus(enum=RegFileIdCtrl) for _ in range(3)]
    regfile_out0, regfile_out1, regfile_in = [Bus(REG_SZ) for _ in range(3)]

    rf = RegisterFile(
        clk, regfile_wr,
        regfile_out0_id, regfile_out1_id, regfile_in_id,
        regfile_out0, regfile_out1, regfile_in,
        count=REGFILE_COUNT
    )

    ########################################################################
    """RAM SECTION"""

    ram_a_wr = Bus1()
    ram_a_in, ram_a_out = Bus(DATA_BITS), Bus(DATA_BITS)
    reg_dr_out = Bus(DATA_BITS)  # no need to make real register for DR, just using output bus from memory module

    ram_mod = RAMSyncSP(
        clk,
        ram_a_wr, reg_ar_out, ram_a_in, reg_dr_out,
        depth=2 ** ADDR_BITS, width=DATA_BITS,
        contents=ram
    )

    ########################################################################
    """BUS INPUT SECTION"""
    mux_bus_a_reg_in_ctrl, mux_bus_b_reg_in_ctrl = Bus(enum=BusInCtrl), Bus(enum=BusInCtrl)
    mux_bus_a_nr_rf_ctrl, mux_bus_b_nr_rf_ctrl = Bus(enum=RegFileOrNormalRegister), Bus(enum=RegFileOrNormalRegister)
    tmp_bus_a_sig, tmp_bus_b_sig = Bus(REG_SZ), Bus(REG_SZ)

    # according to BusInCtrl
    _reg_inputs = [zerobus, reg_ps_out, reg_dr_out, zerobus]
    mux_bus_a_registers_in = Mux(
        _reg_inputs,
        tmp_bus_a_sig, mux_bus_a_reg_in_ctrl
    )
    mux_bus_b_registers_in = Mux(
        _reg_inputs,
        tmp_bus_b_sig, mux_bus_b_reg_in_ctrl
    )

    mux_bus_a_nr_rf = Mux(
        [tmp_bus_a_sig, regfile_out0],
        bus_a, mux_bus_a_nr_rf_ctrl
    )
    mux_bus_b_nr_rf = Mux(
        [tmp_bus_b_sig, regfile_out1],
        bus_b, mux_bus_b_nr_rf_ctrl
    )

    ########################################################################
    """BUS OUTPUT SECTION"""
    demux_tmp_bus_c = Bus(REG_SZ)
    demux_bus_c_reg_wr = Bus1()
    demux_bus_c_reg_id = Bus(enum=BusOutCtrl)
    demux_bus_c_nr_rf = Bus(enum=RegFileOrNormalRegister)

    # Order of demux out should be according to BusOutCtrl!
    # TODO add write from BusC to PS via reg_ps_in.driver()

    demux_bus_c_reg_wr_cmd = DeMux(
        demux_bus_c_reg_wr,
        [zerobus, reg_ps_wr.driver(), ram_a_wr, reg_ar_wr],
        demux_bus_c_reg_id
    )
    demux_bus_c_reg_wr_data = DeMux(
        demux_tmp_bus_c,
        [zerobus, zerobus, ram_a_in, reg_ar_in],
        demux_bus_c_reg_id
    )
    demux_bus_c = DeMux(
        bus_c,
        [demux_tmp_bus_c, regfile_in],
        demux_bus_c_nr_rf
    )

    ########################################################################
    """ALU SECTION"""
    # ALU control signals
    alu_ctrl = Bus(enum=ALUCtrl)
    alu_flag_ctrl = Bus(enum=ALUFlagCtrl)
    alu_ctrl_pa, alu_ctrl_pb = [Bus(enum=ALUPortCtrl) for _ in range(2)]

    # ALU module
    alu = ALU(
        alu_ctrl, alu_ctrl_pa, alu_ctrl_pb,
        bus_a, bus_b,
        bus_c,
        alu_flag_ctrl,
        reg_ps_out,
        reg_ps_in.driver()
    )

    ########################################################################
    """CONTROL SECTION"""
    alu_dec = ALUDecoder(
        control_bus,
        alu_ctrl, alu_ctrl_pa, alu_ctrl_pb, alu_flag_ctrl
    )

    reg_r_dec = RegReadDecoder(
        control_bus,
        mux_bus_a_nr_rf_ctrl, mux_bus_b_nr_rf_ctrl,
        mux_bus_a_reg_in_ctrl, mux_bus_b_reg_in_ctrl,
        regfile_out0_id, regfile_out1_id
    )

    reg_w_dec = RegWriteDecoder(
        clk,
        control_bus,
        ram_a_wr,
        reg_ps_wr.driver(),
        demux_bus_c_reg_wr, demux_bus_c_reg_id, demux_bus_c_nr_rf,
        regfile_wr, regfile_in_id
    )

    return introspect()