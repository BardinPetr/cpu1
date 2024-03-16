from myhdl import block

from utils.runutils import run_sim


def myhdl_pytest(gui=False, duration=None):
    def _myhdl_pytest(func):
        def wrapper():
            tb = block(func)()
            run_sim(tb, duration, gui)

        return wrapper

    return _myhdl_pytest
