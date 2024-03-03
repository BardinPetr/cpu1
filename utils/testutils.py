from myhdl import block

from utils.runutils import run_sim


def myhdl_pytest(gui=False):
    def _myhdl_pytest(func):
        def wrapper():
            tb = block(func)()
            run_sim(tb, None, gui)

        return wrapper

    return _myhdl_pytest
