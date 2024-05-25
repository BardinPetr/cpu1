from dataclasses import dataclass
from math import log2, ceil
from typing import List, Tuple, Annotated, Optional, Sized, Union, get_type_hints

from myhdl import intbv

from src.machine.config import MC_INSTR_SZ
from src.machine.utils.enums import EncodedEnum, EnumEncodingType, CtrlEnum


class MCLocator:
    def __init__(self,
                 content: Optional[Sized | CtrlEnum] = None,
                 bits: Optional[int] = None,
                 select=EnumEncodingType.AS_IS):
        if bits is None:
            assert content is not None, "No way to deduce partial locator size"

            if issubclass(content, CtrlEnum):
                select = content.encoding_type()
                bits = content.encoded_len()
            else:
                sz = len(content)
                if select == EnumEncodingType.SINGLE:
                    bits = ceil(log2(max(2, sz)))
                else:
                    bits = max(1, sz)

        self.size = bits
        self.select = select
        self.loc_start: Optional[int] = None

    @property
    def loc_end(self):
        return self.loc_start + self.size

    def put(self, target: intbv, source: Union[int, intbv, EncodedEnum]):
        try:
            # convert EncodedEnum and CtrlEnum
            source = int(source)
        except ValueError:
            raise ValueError(f"Failed to compile field {source} of type {type(source)}")
        target[self.loc_end:self.loc_start] = source

    def get(self, source: intbv) -> intbv:
        return source[self.loc_end:self.loc_start]

    def at(self, pos: int) -> 'MCLocator':
        self.loc_start = pos
        return self

    def after(self, prev: 'MCLocator') -> 'MCLocator':
        self.loc_start = prev.loc_end
        return self

    def __str__(self):
        return f"LOC[{self.loc_start}:{self.loc_end})={self.size}b"


@dataclass
class BaseMCInstruction:

    def __post_init__(self):
        self._init_locators()
        self.fields = self._inspect_fields()

    def compile(self) -> int:
        res = intbv(0)[MC_INSTR_SZ:]

        fields = self._inspect_fields()
        for param_name, _, locator in fields:
            try:
                locator.put(res, self.__getattribute__(param_name))
            except AttributeError:
                print(f"Failed to process field {param_name}")

        return int(res)

    @staticmethod
    def decompile(data: intbv | bytes) -> 'BaseMCInstruction':
        if isinstance(data, bytes):
            data = intbv(int.from_bytes(data, byteorder='little'))
        return BaseMCInstruction()

    @classmethod
    def _init_locators(cls):
        return
        # fields = cls._inspect_fields()
        # for i, (name, annot, locator) in enumerate(fields):
        #     if i == 0:
        #         locator.at(0)
        #     if locator.loc_start is None:
        #         locator.after(fields[i - 1][2])

    @classmethod
    def _inspect_fields(cls) -> List[Tuple[str, Annotated, MCLocator]]:
        return [
            (name, annot, annot.__metadata__[0])
            for name, annot in get_type_hints(cls, include_extras=True).items()
        ]

    @classmethod
    def describe(cls):
        cls._init_locators()
        name = cls.__name__.replace("MCInstruction", "")
        fields = cls._inspect_fields()
        fields = [
            (f"[{loc.loc_start:2d}:{loc.loc_end:2d}) "
             f"{loc.size:2d}b   "
             f"{annot.__args__[0].__name__:12s}"
             f"as {name}")
            for name, annot, loc in fields
        ]
        sep = '\n  '
        return f"{name} [{sep}{sep.join(fields)}\n]"
