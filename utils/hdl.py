import functools

from myhdl import *
from myhdl import _Signal

from src.components.config import DATA_BITS


def hdl_block(func):
    return functools.wraps(func)(block(func))


def create_int_signal(bits=DATA_BITS) -> _Signal:
    return Signal(intbv(0)[bits:])


def dim(sig: _Signal) -> int:
    """
    Get signal underlying type size in bits
    :param sig: signal
    :return:    bit count
    """
    return sig.val._nrbits
