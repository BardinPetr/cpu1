from enum import IntEnum
from math import ceil, log2
from typing import Union


class EnumEncoding:
    SINGLE = 0
    MULTIPLE = 1


class EnumSC(IntEnum):

    @classmethod
    def encoded_len(cls):
        return ceil(log2(len(cls)))


class EnumMC(IntEnum):

    @classmethod
    def encoded_len(cls):
        return len(cls)


IntEnums = Union[EnumMC, EnumSC]
