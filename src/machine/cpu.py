from typing import List, Optional

from myhdl import intbv

from machine.arch import BusInCtrl, ALUCtrl, BusOutCtrl, ALUFlagCtrl, ALUPortCtrl
from machine.bus import create_io_bus, create_clk_bus
from machine.mc.components.control import MCControl
from src.machine.components.base import Clock
from src.machine.config import DATA_BITS, MC_INSTR_SZ
from src.machine.datapath.datapath import DataPath
from src.machine.utils.hdl import hdl_block, Bus, Bus1
from src.machine.utils.introspection import introspect


@hdl_block
def CPU(
    mc_rom: List[int],
    ram: Optional[List[int | intbv]] = None,
    iobus_clk=None,
    iobus_ctrl=None,
    iobus_addr=None,
    iobus_data=None,
):
    if any(map(lambda x: x is None, [iobus_clk, iobus_ctrl, iobus_addr, iobus_data])):
        iobus_clk, iobus_ctrl, iobus_addr, iobus_data = create_io_bus()

    # control module base clock
    clk, clk_dp, clk_dp_wr = create_clk_bus()
    clg = Clock(clk, 10)

    # control buses
    control_bus = Bus(MC_INSTR_SZ)
    mux_bus_a_reg_in_ctrl, mux_bus_b_reg_in_ctrl = (
        Bus(enum=BusInCtrl),
        Bus(enum=BusInCtrl),
    )
    alu_ctrl = Bus(enum=ALUCtrl)
    alu_flag_ctrl = Bus(enum=ALUFlagCtrl)
    alu_ctrl_pa, alu_ctrl_pb = [Bus(enum=ALUPortCtrl) for _ in range(2)]
    reg_ps_wr, ram_a_wr = [Bus1(0) for _ in range(2)]
    d_stack_wr, r_stack_wr = [Bus1(0) for _ in range(2)]
    d_stack_shift, r_stack_shift = [Bus(min=-1, max=2) for _ in range(2)]
    reg_drw_wr, reg_ar_wr, reg_ip_wr, reg_cr_wr = [Bus1(0) for _ in range(4)]
    demux_bus_c_reg_id = Bus(enum=BusOutCtrl)

    # general-purpose buses
    bus_a = Bus(DATA_BITS)
    bus_b = Bus(DATA_BITS)
    bus_c = Bus(DATA_BITS)

    # submodules
    control = MCControl(
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
        mc_rom_data=mc_rom,
    )

    datapath = DataPath(
        clk_dp,
        clk_dp_wr,
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
        demux_bus_c_reg_id,
        d_stack_shift,
        d_stack_wr,
        r_stack_shift,
        r_stack_wr,
        reg_drw_wr,
        reg_ar_wr,
        reg_ip_wr,
        reg_cr_wr,
        ram=ram,
    )

    return introspect()
