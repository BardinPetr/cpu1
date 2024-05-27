import random

from myhdl import intbv

from machine.config import DATA_BITS
from machine.utils.hdl import signed, SINT_MIN, SINT_MAX, UINT_MAX, UINT_MIN


def q(a, b):
    a = intbv(signed(a))[1 + DATA_BITS:]
    b = intbv(signed(b))[1 + DATA_BITS:]
    b[:] = ~b + 1

    # pre_out = intbv((a + b))
    pre_out = intbv((a + b))

    out = pre_out[DATA_BITS:]
    sign = pre_out[DATA_BITS - 1]
    carry = pre_out[DATA_BITS]

    a_sign, b_sign = a[DATA_BITS - 1], b[DATA_BITS - 1]
    return {
        'n':   sign,
        'z':   not out,
        'c':   carry,
        'v':   (sign ^ a_sign) & (sign ^ b_sign),  # (a_sign & b_sign & (~sign)) | ((~a_sign) & (~b_sign) & sign),
        'a':   a,
        'b':   b,
        'res': out
    }


# a, b = 2147483647, 1
# print(a, b, q(a, b))


for i in range(10000):
    a, b = [random.randint(SINT_MIN, SINT_MAX) for _ in range(2)]
    res = q(a, b)
    lt = res['n'] ^ res['v']
    assert lt == (a < b), f"{a} s< {b} = {a < b} LT={lt} {res}"

for i in range(10000):
    a, b = [random.randint(UINT_MIN, UINT_MAX) for _ in range(2)]
    res = q(a, b)
    lt = res['c']
    assert lt == (a < b), f"{a} u< {b} = {a < b} LT={lt} {res}"
