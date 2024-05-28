from compiler.utils.funclib import FunctionLibrary
from isa.main import Opcode
from src.isa.model.instructions import Instr, ImmInstr

stdlib = FunctionLibrary()

STDOUT_BUSY_REG = 0x10
STDOUT_CHAR_REG = 0x11
STDOUT_INT_REG = 0x12
STDIN_BUSY_REG = 0x20
STDIN_REG = 0x21


def gen_push(val: int) -> Instr:
    return ImmInstr(Opcode.ISTKPSH, imm=val)


# Maths
stdlib['+'] = [Instr(Opcode.ADD)]
stdlib['-'] = [Instr(Opcode.SUB)]
stdlib['*'] = [Instr(Opcode.MUL)]
stdlib['/'] = [Instr(Opcode.DIV)]
stdlib['mod'] = [Instr(Opcode.MOD)]
stdlib['and'] = [Instr(Opcode.AND)]
stdlib['or'] = [Instr(Opcode.OR)]
stdlib['invert'] = [Instr(Opcode.INV)]
stdlib['negate'] = [Instr(Opcode.NEG)]
stdlib['1-'] = [Instr(Opcode.DEC)]
stdlib['1+'] = [Instr(Opcode.INC)]

# compare
stdlib['='] = [Instr(Opcode.CEQ)]
stdlib['<'] = [Instr(Opcode.CLTS)]
stdlib['>'] = [Instr(Opcode.CGTS)]
stdlib['u<'] = [Instr(Opcode.CLTU)]
stdlib['u>'] = [Instr(Opcode.CGTU)]
stdlib['<>'] = [Instr(Opcode.CEQ), Instr(Opcode.INV)]
stdlib['<='] = [Instr(Opcode.DEC), Instr(Opcode.CLTS)]
stdlib['>='] = [Instr(Opcode.INC), Instr(Opcode.CGTS)]

# stack
stdlib['dup'] = [Instr(Opcode.STKDUP)]
stdlib['drop'] = [Instr(Opcode.STKPOP)]
stdlib['swap'] = [Instr(Opcode.STKSWP)]
stdlib['over'] = [Instr(Opcode.STKOVR)]
stdlib['true'] = [gen_push(1)]
stdlib['false'] = [gen_push(0)]

# mem
stdlib['!'] = [Instr(Opcode.STORE)]
stdlib['@'] = [Instr(Opcode.FETCH)]
stdlib['+!'] = [
    Instr(Opcode.STKSWP),
    Instr(Opcode.STKOVR),
    Instr(Opcode.FETCH),
    Instr(Opcode.ADD),
    Instr(Opcode.STKSWP),
    Instr(Opcode.STORE),
]

# ctrl
stdlib['i'] = [Instr(Opcode.STKCP, stack=1)]
stdlib['halt'] = [Instr(Opcode.HLT)]
stdlib['cells'] = []

# io in
stdlib['io@'] = [Instr(Opcode.IN)]
stdlib['key'] = [
    gen_push(STDIN_REG),
    *stdlib['io@'].code
]

# io out
stdlib['io!'] = [Instr(Opcode.OUT)]
stdlib['.'] = [
    gen_push(STDOUT_INT_REG),
    *stdlib['io!'].code
]
stdlib['emit'] = [
    gen_push(STDOUT_CHAR_REG),
    *stdlib['io!'].code
]
stdlib['cr'] = [
    gen_push(ord('\n')),
    *stdlib['emit'].code
]
