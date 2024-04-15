from enum import IntEnum, Enum
from math import ceil, log2


class EnumEncodingType(Enum):
    SINGLE = 0
    MULTIPLE = 1
    AS_IS = MULTIPLE


class CtrlEnum(IntEnum):

    @classmethod
    def encoding_type(cls) -> EnumEncodingType:
        return EnumEncodingType.AS_IS

    @classmethod
    def encoded_len(cls):
        return len(cls)


class CEnumS(CtrlEnum):

    @classmethod
    def encoded_len(cls):
        return ceil(log2(len(cls)))

    @classmethod
    def encoding_type(cls) -> EnumEncodingType:
        return EnumEncodingType.SINGLE


class CEnumM(CtrlEnum):

    @classmethod
    def encoding_type(cls) -> EnumEncodingType:
        return EnumEncodingType.MULTIPLE
