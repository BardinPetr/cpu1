import functools
from typing import Optional

from myhdl import *
from myhdl import _Signal

from src.config import DATA_BITS


def hdl_block(func):
    return functools.wraps(func)(block(func))


def Bus(bits=DATA_BITS, state=0) -> _Signal:
    return Signal(intbv(state)[bits:])


def dim(sig: _Signal._Signal | intbv | modbv) -> int:
    """
    Get signal underlying type size in bits
    :param sig: signal
    :return:    bit count
    """
    if isinstance(sig, _Signal._Signal):
        sig = sig.val
    return sig._nrbits


def create_or_use(sig: Optional[_Signal], size) -> _Signal:
    return Bus(size) if sig is None else sig


def create_reg_signals(reg_size: int) -> tuple[_Signal, _Signal, _Signal]:
    return Bus(reg_size), Bus(reg_size), Signal(False)
