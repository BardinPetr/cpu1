import functools
from typing import Optional, Type

from myhdl import block, intbv, modbv, TristateSignal
from myhdl._ShadowSignal import _TristateSignal
from myhdl._Signal import _Signal, Signal

from src.machine.config import DATA_BITS
from src.machine.utils.enums import CtrlEnum


def hdl_block(func):
    return functools.wraps(func)(block(func))


def Bus(bits: Optional[int] = None,
        state=0,
        min=None, max=None,
        enum: Optional[Type[CtrlEnum]] = None,
        tristate=False) -> _Signal | _TristateSignal:
    if min is not None or max is not None:
        content = intbv(state, min=min, max=max)
    else:
        if enum is not None and bits is None:
            bits = enum.encoded_len()
        content = intbv(state)[bits:]

    if tristate:
        sig = TristateSignal(content)
        sig.encoding = enum
        return sig

    return _Signal(content, encoding=enum)


def Bus1(state=0, delay=0) -> _Signal:
    return Signal(intbv(state)[1:], delay=delay)


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
SINT16_MAX = (1 << (16 - 1)) - 1
SINT16_MIN = -(1 << (16 - 1))


def trunc(x, n=DIM):
    return x & ((1 << n) - 1)


def negate(x, n=DIM):
    return trunc(~x + 1, n)


def signed(val, n=DIM):
    return trunc(~abs(val) + 1, n) if val < 0 else val


def set_signed(sig, val):
    sig.next = signed(val)
