from typing import List

from lark import Transformer, Token

from mcasm.utils import Location


class TypeTransformer(Transformer):
    def LOC(self, val):
        vals = str(val)
        if vals.startswith("0x"):
            return Location(pos=int(val, 16))
        if vals.isdecimal() or vals.startswith("-"):
            return Location(pos=int(val))
        return self.ID(val)

    def ID(self, val):
        return Location(name=str(val))

    def block(self, val: List[Token]):
        return val

    BINARY = lambda self, x: int(x, 2)
    HEXNUMBER = lambda self, x: int(x, 16)
    BINNUMBER = lambda self, x: int(x, 2)
    NUMBER = int
