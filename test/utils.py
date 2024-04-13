from src.config import DATA_BITS

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
