from myhdl._Signal import _Signal

from src.machine.utils.hdl import hdl_block
from src.machine.utils.runutils import run_sim


def myhdl_pytest(gui=False, duration=None):
    def _myhdl_pytest(func):
        def wrapper():
            blk = hdl_block(func)
            tb = blk()
            run_sim(tb, duration, gui)

        return wrapper

    return _myhdl_pytest


def skip_clk(clk: _Signal, cnt: int):
    for _ in range(cnt + 1):
        yield clk.posedge
        yield clk.negedge
