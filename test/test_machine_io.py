import atexit

from myhdl import *
from myhdl._ShadowSignal import _SliceSignal

from isa.main import compile_instructions, Opcode
from isa.model.instructions import Instr
from machine.arch import RegFileIdCtrl
from machine.main import Machine
from machine.utils.log import get_logger
from machine.utils.runutils import display_trace_vcd
from src.machine.mc.code import mcrom
from src.machine.utils.introspection import IntrospectionTree, TraceTick, TraceData, TraceInstr
from src.machine.utils.testutils import myhdl_pytest

L = get_logger()

TESTS = [
    [Opcode.ISTKPSH, dict(imm=0x12), 0, 0, lambda x, y: None],
    [Opcode.IN, dict(), 0, 0, lambda x, y: None],
    [Opcode.ISTKPSH, dict(imm=64), 0, 0, lambda x, y: None],
    [Opcode.ISTKPSH, dict(imm=0x11), 0, 0, lambda x, y: None],
    [Opcode.OUT, dict(), 0, 0, lambda x, y: None],
    [Opcode.ISTKPSH, dict(imm=0x12), 0, 0, lambda x, y: None],
    [Opcode.IN, dict(), 0, 0, lambda x, y: None],
    # [Opcode.ISTKPSH, dict(imm=0xBBCC), 0, 0, lambda x, y: None],
    # [Opcode.ISTKPSH, dict(imm=0x2B), 0, 0, lambda x, y: None],
    # [Opcode.OUT, dict(), 0, 0, lambda x, y: None],
    [Opcode.HLT, dict(), 0, 0, lambda x, y: None],
]

RAM = compile_instructions([
    Instr(i[0], **i[1]) for i in TESTS
])


@myhdl_pytest(gui=False, duration=None)
def test_cpu_wmc_infetch():
    machine = Machine(ram=RAM)

    intro = IntrospectionTree.build(machine).cpu
    dp = intro.datapath
    clk = intro.clk
    ip = dp.rf.registers[RegFileIdCtrl.IP]
    mc_pc = intro.control.mc_pc
    d_stack = dp.d_stack

    trace_res = TraceData()
    tracer = TraceTick(intro.clk, trace_res, {
        "CLK":        clk,
        "A":          dp.bus_a,
        "B":          dp.bus_b,
        "C":          dp.bus_c,
        "IP":         ip,
        "CR":         dp.rf.registers[RegFileIdCtrl.CR],
        "AR":         dp.reg_ar_out,
        "DR":         dp.reg_dr_out,
        "DRW":        dp.ram_a_in,
        "RAM_WR":     dp.ram_a_wr,
        # "RAR_W":     dp.reg_ar_wr,
        # "RAR_O":     dp.reg_ar_out,
        # "RAR_I":     dp.reg_ar_in,
        # "OC":     dp.demux_bus_c_reg_id,
        # "OCW":     dp.demux_bus_c_reg_wr,
        # "DS_S":   d_stack.in_shift,
        # "DS_W":   d_stack.in_wr_top,
        # "DS_IN":  dp.d_stack_in,
        "DS_SP":      d_stack.sp,
        "DS_TOP":     dp.d_stack_tos0,
        "DS_PRV":     dp.d_stack_tos1,
        "RS_SP":      dp.r_stack.sp,
        "RS_TOP":     dp.r_stack_tos0,
        "RS_PRV":     dp.r_stack_tos1,
        "MCPC":       mc_pc,
        "FLAGSI":     dp.reg_ps_in,
        "FLAGSO":     dp.reg_ps_out,
        "FLAGSW":     dp.reg_ps_wr,
        "IO_ABUS":    intro.iobus_addr,
        "IO_DBUS":    intro.iobus_data,
        "IO_CTRL":    intro.iobus_ctrl,
        "IO_CLK":     intro.iobus_clk,
        "F":          dp.io_ctrl.fuck,
        "MC_IO_CTRL": _SliceSignal(intro.control_bus, 45, 42),
    })

    itrace_res = TraceData()
    itracer = TraceInstr(
        intro.clk, itrace_res, {
            "IP":     ip,
            "PS":     dp.reg_ps_out,
            "CR":     dp.rf.registers[RegFileIdCtrl.CR],
            "DS_TOP": dp.d_stack_tos0,
            "DS_PRV": dp.d_stack_tos1,
            "RS_TOP": dp.r_stack_tos0,
            "RS_PRV": dp.r_stack_tos1
        },
        mc_pc, mc_pc_trigger_value=mcrom.MICROCODE.labels['end']
    )

    @instance
    def stimulus():
        steps = 10000
        while steps := (steps - 1):
            yield clk.posedge
        yield StopSimulation()

    @atexit.register
    def stop():
        display_trace_vcd('dist', 't2', itrace_res)
        display_trace_vcd('dist', 't1', trace_res)

    return machine, stimulus, tracer, itracer
