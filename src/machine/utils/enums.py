from dataclasses import dataclass
from enum import IntEnum, Enum
from functools import reduce
from math import ceil, log2
from typing import List, Type


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

    # TODO Fix counting of values
    # @classmethod
    # def __len__(cls):
    #     zeroes = len([i for i in cls if i.value == 0])
    #     return len(cls) - zeroes

    @classmethod
    def decode_names(cls, names: List[str]) -> List["CtrlEnum"]:
        return [cls[i] for i in names]

    @classmethod
    def encode_from_names(cls, items: List[str]) -> "EncodedEnum":
        return cls.encode(cls.decode_names(items))

    @classmethod
    def encode(cls, items: List["CtrlEnum"]) -> "EncodedEnum":
        return EncodedEnum(cls, items)


class CEnumS(CtrlEnum):
    """
    Enum with binary encoding
    """

    @classmethod
    def encoded_len(cls):
        return ceil(log2(len(cls)))

    @classmethod
    def encoding_type(cls) -> EnumEncodingType:
        return EnumEncodingType.SINGLE


class CEnumM(CtrlEnum):
    """
    Enum with by-bit encoding and multiple select
    """

    @classmethod
    def encoding_type(cls) -> EnumEncodingType:
        return EnumEncodingType.MULTIPLE

    @classmethod
    def encode(cls, items: List[CtrlEnum]) -> "EncodedEnum":
        return EncodedEnum(cls, items)


@dataclass
class EncodedEnum:
    source: Type[CtrlEnum]
    items: List[CtrlEnum]

    def __post_init__(self):
        if self.source.encoding_type() == EnumEncodingType.SINGLE:
            if len(self.items) != 1:
                raise ValueError("Passed multiple values for single-choice enum")
            self.value = self.items[0].value
        else:
            self.value = reduce(lambda a, i: a | i.value, self.items, 0)

    def __int__(self) -> int:
        return self.value

    def __repr__(self):
        return str(self)

    def __str__(self):
        lst = ",".join([i.name for i in self.items])
        return f"[{lst}]" if len(self.items) > 1 else lst
