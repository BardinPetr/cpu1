from compiler.funclib import FunctionLibrary
from compiler.isa import Instr, Opcode

stdlib = FunctionLibrary()

stdlib['+'] = [Instr(Opcode.ADD)]
