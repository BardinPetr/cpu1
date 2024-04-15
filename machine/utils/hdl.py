import functools
from typing import Optional, Type

from myhdl import block, intbv, modbv
from myhdl._Signal import _Signal

from machine.config import DATA_BITS
from machine.utils.enums import CtrlEnum


def hdl_block(func):
    return functools.wraps(func)(block(func))


def Bus(bits: Optional[int] = None, state=0, enum: Optional[Type[CtrlEnum]] = None) -> _Signal:
    if enum is not None and bits is None:
        bits = enum.encoded_len()
    return _Signal(intbv(state)[bits:], encoding=enum)


def Bus1(state=0) -> _Signal:
    return _Signal(intbv(state)[1:])


def dim(sig: _Signal | intbv | modbv) -> int:
    """
    Get signal underlying type size in bits
    :param sig: signal
    :return:    bit count
    """
    # if isinstance(sig, _Signal):
    #     sig = sig.val
    return sig._nrbits


def create_reg_signals(reg_size: int) -> tuple[_Signal, _Signal, _Signal]:
    return Bus(reg_size), Bus(reg_size), Bus1(False)


DIM = DATA_BITS

UINT_MIN = 0
UINT_MAX = (1 << DIM) - 1
SINT_MAX = (1 << (DIM - 1)) - 1
SINT_MIN = -(1 << (DIM - 1))


def trunc(x, n=DIM):
    return x & ((1 << n) - 1)


def negate(x, n=DIM):
    return trunc(~x + 1, n)


def set_signed(sig, val):
    sig.next = trunc(~abs(val) + 1) if val < 0 else val
