import functools

from myhdl import block


def hdl_block(func):
    return functools.wraps(func)(block(func))
