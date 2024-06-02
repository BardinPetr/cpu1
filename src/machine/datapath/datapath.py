from myhdl import always_comb

from machine.io.io_controller import IOController
from src.machine.components.ALU import ALU
from src.machine.components.ExtendedStack import ExtendedStack
from src.machine.components.RAM import RAMSyncSP
from src.machine.components.base import Register, Latch
from src.machine.components.mux import Mux, DeMux
from src.machine.config import (
    DATA_BITS,
    REG_PS_SZ,
    ADDR_BITS,
    STACK_D_DEPTH,
    IO_DATA_BUS_SIZE,
)
from src.machine.utils.hdl import hdl_block, Bus, create_reg_signals, Bus1
from src.machine.utils.introspection import introspect
from src.machine.utils.log import get_logger

L = get_logger()


@hdl_block
def DataPath(
    clk,
    clk_wr,
    control_bus,
    bus_a,
    bus_b,
    bus_c,
    iobus_clk,
    iobus_ctrl,
    iobus_addr,
    iobus_data,
    alu_ctrl,
    alu_ctrl_pa,
    alu_ctrl_pb,
    alu_flag_ctrl,
    mux_bus_a_reg_in_ctrl,
    mux_bus_b_reg_in_ctrl,
    ram_a_wr,
    reg_ps_wr,
    demux_bus_c_reg_wr,
    demux_bus_c_reg_id,
    d_stack_shift,
    d_stack_wr,
    r_stack_shift,
    r_stack_wr,
    ram=None,
):
    """
    Description of CPU datapath
    """
    zerobus = Bus(DATA_BITS, state=0)

    ########################################################################
    """REGISTERS SECTION"""
    # classic registers
    # Program State register (see PSFlags)
    reg_ps_out = Bus(REG_PS_SZ)
    reg_ps_in = Bus(REG_PS_SZ)
    reg_ps = Register(reg_ps_in, reg_ps_out, reg_ps_wr)

    # register tied to ram input addr
    reg_ar_in, reg_ar_out, reg_ar_wr = create_reg_signals()
    reg_ar = Register(reg_ar_in, reg_ar_out, reg_ar_wr)

    # register tied to ram input data
    reg_drw_in, reg_drw_out, reg_drw_wr = create_reg_signals()
    reg_drw = Register(reg_drw_in, reg_drw_out, reg_drw_wr)

    reg_cr_in, reg_cr_out, reg_cr_wr = create_reg_signals()
    reg_cr = Register(reg_cr_in, reg_cr_out, reg_cr_wr)

    reg_ip_in, reg_ip_out, reg_ip_wr = create_reg_signals()
    reg_ip = Register(reg_ip_in, reg_ip_out, reg_ip_wr)

    ########################################################################
    """IO SECTION"""
    io_ctrl_data_output = Bus(bits=IO_DATA_BUS_SIZE)
    io_ctrl = IOController(
        clk_wr,
        iobus_clk,
        control_bus,
        iobus_ctrl,
        iobus_addr,
        iobus_data,
        bus_c,
        io_ctrl_data_output,
    )

    ########################################################################
    """RAM SECTION"""
    ram_drr = Bus(
        DATA_BITS
    )  # no need to make real register for DR, just using output bus from memory module

    ram_mod = RAMSyncSP(
        clk,
        ram_a_wr,
        reg_ar_out,
        reg_drw_out,
        ram_drr,
        depth=2**ADDR_BITS,
        width=DATA_BITS,
        contents=ram,
    )

    ########################################################################
    """STACK SECTION"""
    d_stack_full, r_stack_full, d_stack_empty, r_stack_empty = (
        Bus1(0),
        Bus1(0),
        Bus1(1),
        Bus1(1),
    )
    d_stack_tos0, d_stack_tos1, r_stack_tos0, r_stack_tos1 = [
        Bus(DATA_BITS) for _ in range(4)
    ]
    d_stack_in, r_stack_in = [Bus(DATA_BITS) for _ in range(2)]

    d_stack = ExtendedStack(
        clk_wr,
        d_stack_shift,
        d_stack_wr,
        d_stack_in,
        d_stack_tos0,
        d_stack_tos1,
        d_stack_empty,
        d_stack_full,
        depth=STACK_D_DEPTH,
        width=DATA_BITS,
    )
    r_stack = ExtendedStack(
        clk_wr,
        r_stack_shift,
        r_stack_wr,
        r_stack_in,
        r_stack_tos0,
        r_stack_tos1,
        r_stack_empty,
        r_stack_full,
        depth=STACK_D_DEPTH,
        width=DATA_BITS,
    )

    ########################################################################
    """BUS INPUT SECTION"""
    bus_in = [
        zerobus,
        reg_ps_out,
        ram_drr,
        io_ctrl_data_output,
        d_stack_tos0,
        d_stack_tos1,
        r_stack_tos0,
        r_stack_tos1,
        reg_ip_out,
        reg_cr_out,
    ]

    # select input channel according to BusInCtrl
    mux_bus_a_registers_in = Mux(bus_in, output=bus_a, ctrl=mux_bus_a_reg_in_ctrl)
    mux_bus_b_registers_in = Mux(bus_in, output=bus_b, ctrl=mux_bus_b_reg_in_ctrl)

    ########################################################################
    """BUS OUTPUT SECTION"""
    # forward WR signals
    demux_bus_c_reg_wr_cmd = DeMux(
        demux_bus_c_reg_wr,
        # According to BusOutCtrl
        [
            zerobus,
            zerobus,
            reg_drw_wr,
            reg_ar_wr,
            zerobus,
            zerobus,
            reg_ip_wr,
            reg_cr_wr,
        ],
        ctrl=demux_bus_c_reg_id,
    )

    # forward data signals
    demux_bus_c_reg_wr_data = DeMux(
        bus_c,
        # According to BusOutCtrl
        [
            zerobus,
            zerobus,
            reg_drw_in,
            reg_ar_in,
            d_stack_in,
            r_stack_in,
            reg_ip_in,
            reg_cr_in,
        ],
        ctrl=demux_bus_c_reg_id,
    )

    ########################################################################
    """ALU SECTION"""
    # ALU control signals
    alu_flag_out = Bus(bits=4)
    alu_a_in, alu_b_in = Bus(DATA_BITS), Bus(DATA_BITS)
    latch_alu_a_in = Latch(bus_a, alu_a_in, clk)
    latch_alu_b_in = Latch(bus_b, alu_b_in, clk)

    # ALU module
    alu = ALU(
        alu_ctrl, alu_ctrl_pa, alu_ctrl_pb, alu_a_in, alu_b_in, bus_c, alu_flag_out
    )

    ########################################################################
    """PS CONTROL"""
    reg_ps_updated_flag_input = Bus(bits=4)

    @always_comb
    def update_ps():
        reg_ps_updated_flag_input.next = reg_ps_out & (~0xF) | alu_flag_out

    mux_ps_input = Mux(
        [reg_ps_out, reg_ps_updated_flag_input], reg_ps_in, ctrl=alu_flag_ctrl
    )

    return introspect()
