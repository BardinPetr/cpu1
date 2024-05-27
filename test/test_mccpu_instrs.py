import atexit

from myhdl import *

import src.machine.mc.mcisa as MCLocs
from compiler.main import compile_forth
from compiler.memory import unpack_binary
from isa.main import compile_instructions, Opcode
from isa.model.instructions import Instr
from machine.arch import RegFileIdCtrl
from machine.cpu import CPU
from machine.mc.mcinstr import MCInstructionExec
from machine.utils.log import get_logger
from machine.utils.runutils import display_trace_vcd
from src.machine.mc.code import mcrom
from src.machine.utils.introspection import IntrospectionTree, TraceTick, TraceData, TraceInstr
from src.machine.utils.testutils import myhdl_pytest

L = get_logger()

TESTS = [
    # [Opcode.ADD, 2, 1, lambda in_args, out_args: out_args[0] == (in_args[0] + in_args[1])],
    # [Opcode.SUB, 2, 1, lambda in_args, out_args: out_args[0] == (in_args[0] - in_args[1])],
    # [Opcode.STKSWP, 2, 2, lambda in_args, out_args: out_args == in_args[::-1]]
    # [Opcode.STKDUP, 2, 2, lambda in_args, out_args: out_args == in_args[::-1]],
    # [Opcode.STKPOP, 2, 2, lambda in_args, out_args: out_args == in_args[::-1]]
    # [Opcode.STKCP, dict(stack=0), 2, 2, lambda in_args, out_args: out_args == in_args[::-1]],
    # [Opcode.STKCP, dict(stack=1), 2, 2, lambda in_args, out_args: out_args == in_args[::-1]],
    # [Opcode.STKMV, dict(stack=0), 2, 2, lambda in_args, out_args: out_args == in_args[::-1]],
    # [Opcode.STKMV, dict(stack=1), 2, 2, lambda in_args, out_args: out_args == in_args[::-1]],
    # [Opcode.STKOVR, dict(stack=0), 2, 2, lambda in_args, out_args: out_args == in_args[::-1]],
    # [Opcode.STKOVR, dict(stack=1), 2, 2, lambda in_args, out_args: out_args == in_args[::-1]],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0xDEAD), 2, 2, lambda in_args, out_args: out_args == in_args[::-1]],
    # [Opcode.ISTKPSH, dict(stack=1, imm=0xBEEF), 2, 2, lambda in_args, out_args: out_args == in_args[::-1]],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0xDEAD), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0x20), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.STORE, dict(stack=0), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0x20), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.FETCH, dict(stack=0), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0x0), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.FETCH, dict(stack=0), 2, 2, lambda in_args, out_args: 0],

    # [Opcode.ISTKPSH, dict(stack=0, imm=0x20), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0x20), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.CEQ, dict(stack=0), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.STKPOP, {}, 2, 2, lambda in_args, out_args: out_args == in_args[::-1]],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0x21), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0x22), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.CEQ, dict(stack=0), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.STKPOP, {}, 2, 2, lambda in_args, out_args: out_args == in_args[::-1]],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0x21), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0x22), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.CLTS, dict(stack=0), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.STKPOP, {}, 2, 2, lambda in_args, out_args: out_args == in_args[::-1]],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0x21), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0x22), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.CGTS, dict(stack=0), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.STKPOP, {}, 2, 2, lambda in_args, out_args: out_args == in_args[::-1]],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0x20), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0x10), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.CLTS, dict(stack=0), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.STKPOP, {}, 2, 2, lambda in_args, out_args: out_args == in_args[::-1]],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0x20), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0x10), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.CGTS, dict(stack=0), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.STKPOP, {}, 2, 2, lambda in_args, out_args: out_args == in_args[::-1]],

    # [Opcode.ISTKPSH, dict(stack=0, imm=0xF0), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.RCALL, dict(imm=signed(2, 16)), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0xF1), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0xF2), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0xF3), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0xF4), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.RET, dict(), 2, 2, lambda in_args, out_args: 0],

    # [Opcode.ISTKPSH, dict(stack=0, imm=0x1), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.CJMP, dict(imm=signed(2, 16)), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0xF1), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0xF2), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0xF3), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0xF4), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0x0), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.CJMP, dict(imm=signed(2, 16)), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0xA1), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0xA2), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0xA3), 2, 2, lambda in_args, out_args: 0],
    # [Opcode.ISTKPSH, dict(stack=0, imm=0xA4), 2, 2, lambda in_args, out_args: 0],

    [Opcode.ISTKPSH, dict(stack=0, imm=0xF1), 2, 2, lambda in_args, out_args: 0],
    [Opcode.ISTKPSH, dict(stack=0, imm=0xF2), 2, 2, lambda in_args, out_args: 0],
    [Opcode.ISTKPSH, dict(stack=0, imm=0xF3), 2, 2, lambda in_args, out_args: 0],
    [Opcode.HLT, dict(), 2, 2, lambda in_args, out_args: 0],

]

RAM = compile_instructions([
    Instr(i[0], **i[1]) for i in TESTS
])


@myhdl_pytest(gui=False, duration=None)
def test_cpu_wmc_infetch():
    RAM = compile_forth("""
        16 2 3 + * 100 - halt
    """)
    RAM = unpack_binary(RAM)

    print("Microcode")
    print(*mcrom.MICROCODE.commands, sep='\n')
    print("RAM")
    print(RAM)

    for i in mcrom.MICROCODE.commands:
        if isinstance(i, MCInstructionExec):
            print(i.alu_flag_ctrl, i.compile(), MCLocs.MCALUFlagCtrl.get(intbv(i.compile())))

    cpu = CPU(mcrom.ROM, ram=RAM)

    intro = IntrospectionTree.build(cpu)
    dp = intro.datapath
    clk = intro.clk_dp
    ip = dp.rf.registers[RegFileIdCtrl.IP]
    mc_pc = intro.control.mc_pc
    d_stack = dp.d_stack

    trace_res = TraceData()
    tracer = TraceTick(clk, trace_res, {
        "CLK":    clk,
        "A":      dp.bus_a,
        "B":      dp.bus_b,
        "C":      dp.bus_c,
        "IP":     ip,
        "CR":     dp.rf.registers[RegFileIdCtrl.CR],
        "AR":     dp.reg_ar_out,
        "DR":     dp.reg_dr_out,
        "DRW":    dp.ram_a_in,
        "RAM_WR": dp.ram_a_wr,
        # "RAR_W":     dp.reg_ar_wr,
        # "RAR_O":     dp.reg_ar_out,
        # "RAR_I":     dp.reg_ar_in,
        # "OC":     dp.demux_bus_c_reg_id,
        # "OCW":     dp.demux_bus_c_reg_wr,
        # "DS_S":   d_stack.in_shift,
        # "DS_W":   d_stack.in_wr_top,
        # "DS_IN":  dp.d_stack_in,
        "DS_SP":  d_stack.sp,
        "DS_TOP": dp.d_stack_tos0,
        "DS_PRV": dp.d_stack_tos1,
        "RS_SP":  dp.r_stack.sp,
        "RS_TOP": dp.r_stack_tos0,
        "RS_PRV": dp.r_stack_tos1,
        "MCPC":   mc_pc,
        "FLAGSI": dp.reg_ps_in,
        "FLAGSO": dp.reg_ps_out,
        "FLAGSW": dp.reg_ps_wr,
    })

    itrace_res = TraceData()
    itracer = TraceInstr(
        clk, itrace_res, {
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

    # temp_stack = []
    # @always_comb
    # def pre_cmd():
    #     catch_ip = ip
    #     print("!!!", catch_ip)
    #
    #     if 0 < ip <= len(TESTS):
    #         # check previous cmd result
    #         _, cnt_in, cnt_out, check = TESTS[ip - 1]
    #         sources = [temp_stack.pop() for _ in range(cnt_in)][::-1]
    #         results = d_stack.mem[d_stack.sp - cnt_out:d_stack.sp]
    #         print(ip, sources, results)
    #         # assert check(sources, results)
    #
    #     if ip >= len(TESTS):
    #         return
    #
    #     # prepare for next command
    #     _, cnt_in, cnt_out, check = TESTS[ip]
    #
    #     for i in range(cnt_in):
    #         val = random.randint(-1000, 1000)
    #         temp_stack.append(val)
    #         push_stack(d_stack, signed(val))
    #
    #     print("Psh", temp_stack)

    @instance
    def stimulus():
        steps = 10000
        while steps := (steps - 1):
            yield clk.posedge
        yield StopSimulation()

    @atexit.register
    def stop():
        pass
        # display_trace_vcd('dist', 't2', itrace_res)
        # display_trace_vcd('dist', 't1', trace_res)

    return cpu, stimulus, tracer, itracer
