from typing import Dict, Any

from machine.utils.introspection import IntrospectionTree


def gen_introspection_watches_inst(root: IntrospectionTree) -> Dict[str, Any]:
    dp = root.datapath
    return {
        "A": dp.bus_a,
        "B": dp.bus_b,
        "C": dp.bus_c,
        "IP": dp.reg_ip_out,
        "CR": dp.reg_cr_out,
        "AR": dp.reg_ar_out,
        "PS": dp.reg_ps_out,
        "DRR": dp.ram_drr,
        "DRW": dp.reg_drw_out,
        "DS_SP": dp.d_stack.sp,
        "DS_TOP": dp.d_stack_tos0,
        "DS_PRV": dp.d_stack_tos1,
        "RS_SP": dp.r_stack.sp,
        "RS_TOP": dp.r_stack_tos0,
        "RS_PRV": dp.r_stack_tos1,
        "IO_RD": dp.io_ctrl_data_output,
    }


def gen_introspection_watches_tick(root: IntrospectionTree) -> Dict[str, Any]:
    clk = root.clk_dp
    return {"CLK": clk, **gen_introspection_watches_inst(root)}
