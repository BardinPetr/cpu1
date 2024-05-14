from dataclasses import dataclass
from typing import Dict, List

from lplib.lexer.tokens import Token
from lplib.parser.transformer import Transformer

from compiler.isa import ImmInstr, Opcode, Instruction
from compiler.mapper import map_to_opcode


@dataclass
class ForthVariable:
    name: str
    loc: int
    size_slots: int


@dataclass
class Command:
    pass


@dataclass
class ForthFunction:
    name: str
    loc: int
    code: List[Command]

    def __post_init__(self):
        self.size_slots = len(self.code) * 1


class ForthLangTransformer(Transformer):
    SLOT_SIZE = 1

    def __init__(self):
        super().__init__()
        self.__constants: Dict[str, int] = {}
        self.__variables = {}
        self.__functions = {}
        self.__storage_mem_pos = 0
        self.__func_mem_pos = 0

    def def_const(self, name, value):
        if name in self.__constants:
            raise Exception(f"Constant {name} redefined")
        self.__constants[name] = value

    def def_var(self, name, slots=1):
        if name in self.__variables:
            raise Exception(f"Variable {name} redefined")
        self.__variables[name] = ForthVariable(name, self.__storage_mem_pos, slots)
        self.__storage_mem_pos += slots

    def def_arr(self, name, count):
        self.def_var(name, count + 1)

    def function(self, name, lines):
        if name in self.__functions:
            raise Exception(f"Function {name} redefined")
        func = ForthFunction(name, self.__func_mem_pos, lines)
        self.__func_mem_pos += func.size_slots
        self.__functions[name] = func

    def program(self, *lines):
        return lines


class ForthISATransformer(Transformer):

    def cmd_push(self, value: int):
        return ImmInstr(Opcode.IPUSH, value)

    def cmd_calc(self, value: Token):
        return Instruction(map_to_opcode(value.type_id))

    def cmd_compare(self, value):
        return Instruction(map_to_opcode(value.type_id))

    def cmd_mem(self, value):
        pass

    def cmd_io(self, value):
        pass

    def cmd_call(self, value):
        pass
