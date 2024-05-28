from typing import Dict, Any

from machine.arch import RegFileIdCtrl
from machine.utils.introspection import IntrospectionTree


def gen_introspection_watches_inst(root: IntrospectionTree) -> Dict[str, Any]:
    dp = root.datapath
    return {
        "IP":     dp.rf.registers[RegFileIdCtrl.IP],
        "CR":     dp.rf.registers[RegFileIdCtrl.CR],
        "PS":     dp.reg_ps_out,
        "DS_TOP": dp.d_stack_tos0,
        "DS_PRV": dp.d_stack_tos1,
        "RS_TOP": dp.r_stack_tos0,
        "RS_PRV": dp.r_stack_tos1
    }


def gen_introspection_watches_tick(root: IntrospectionTree) -> Dict[str, Any]:
    clk = root.clk_dp
    dp = root.datapath

    return {
        "CLK":    clk,
        "A":      dp.bus_a,
        "B":      dp.bus_b,
        "C":      dp.bus_c,
        "IP":     dp.rf.registers[RegFileIdCtrl.IP],
        "CR":     dp.rf.registers[RegFileIdCtrl.CR],
        "AR":     dp.reg_ar_out,
        "DR":     dp.reg_dr_out,
        "DRW":    dp.ram_a_in,
        "RAM_WR": dp.ram_a_wr,
        "DS_SP":  dp.d_stack.sp,
        "DS_TOP": dp.d_stack_tos0,
        "DS_PRV": dp.d_stack_tos1,
        "RS_SP":  dp.r_stack.sp,
        "RS_TOP": dp.r_stack_tos0,
        "RS_PRV": dp.r_stack_tos1,
        "FLAGSI": dp.reg_ps_in,
        "FLAGSO": dp.reg_ps_out,
        "FLAGSW": dp.reg_ps_wr,
    }
