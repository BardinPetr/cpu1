from enum import IntEnum, auto


class PSFlags(IntEnum):
    Z = 0
    N = 1
    C = 2
    V = 3


class RegFileId(IntEnum):
    PS = 0
    IP = auto()
    CR = auto()
    DR = auto()
