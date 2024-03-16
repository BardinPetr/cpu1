from enum import IntEnum

from lark import Lark, Transformer, v_args


class Location:

    def __init__(self, name: str = None, pos: int = -1):
        self.name = name
        self.pos = pos

    def __repr__(self):
        return f"L<{self.name}@{self.pos}>"

    def __str__(self):
        return self.__repr__()


class Register(IntEnum):
    PS = 0
    CR = 1
    PC = 2

    def __repr__(self):
        return f"REG<{self.name}>"


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

    HEXNUMBER = lambda self, x: int(x, 16)
    BINNUMBER = bool
    NUMBER = int

    REGISTER = lambda self, x: Register[x]


txt = """
label1: 
add
adc
jmp 132
# jmp 0x23
label2 : jmp 0x42
jmp label1
if CR[4] == 0 jmp 0x42 
if CR[4] == 1 jmp label2 
"""

grammar = open("uasm.lark", "r").read()
l = Lark(grammar)
ast = l.parse(txt)
ast = TypeTransformer().transform(ast)

print(ast.pretty())

print(ast)
