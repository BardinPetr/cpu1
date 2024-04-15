from machine.utils.hdl import hdl_block
from machine.utils.runutils import run_sim


def myhdl_pytest(gui=False, duration=None):
    def _myhdl_pytest(func):
        def wrapper():
            blk = hdl_block(func)
            tb = blk()
            run_sim(tb, duration, gui)

        return wrapper

    return _myhdl_pytest
