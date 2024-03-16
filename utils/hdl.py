import functools

from myhdl import *
from myhdl import _Signal

from src.config import DATA_BITS


def hdl_block(func):
    return functools.wraps(func)(block(func))


def create_int_signal(bits=DATA_BITS) -> _Signal:
    return Signal(intbv(0)[bits:])


def dim(sig: _Signal._Signal | intbv | modbv) -> int:
    """
    Get signal underlying type size in bits
    :param sig: signal
    :return:    bit count
    """
    if isinstance(sig, _Signal._Signal):
        sig = sig.val
    return sig._nrbits
