import functools

from myhdl import block, Signal, intbv, modbv
from myhdl._Signal import _Signal

from src.config import DATA_BITS


def hdl_block(func):
    return functools.wraps(func)(block(func))


def Bus(bits=DATA_BITS, state=0) -> _Signal:
    return Signal(intbv(state)[bits:])


def dim(sig: _Signal | intbv | modbv) -> int:
    """
    Get signal underlying type size in bits
    :param sig: signal
    :return:    bit count
    """
    if isinstance(sig, _Signal):
        sig = sig.val
    return sig._nrbits


def create_reg_signals(reg_size: int) -> tuple[_Signal, _Signal, _Signal]:
    return Bus(reg_size), Bus(reg_size), Signal(False)
