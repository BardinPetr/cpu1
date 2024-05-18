from compiler.forth.funclib import FunctionLibrary
from isa.model.instructions import Instr, ImmInstr
from isa.isa import Opcode

stdlib = FunctionLibrary()

STDOUT_DEV = 0
STDOUT_DEFAULT_REG = 0
STDOUT_INT_REG = 1
STDIN_DEV = 1
STDIN_DEFAULT_REG = 0


def gen_push(val: int) -> Instr:
    return ImmInstr(Opcode.IPUSH, imm=val)


# Maths
stdlib['+'] = [Instr(Opcode.ADD)]
stdlib['-'] = [Instr(Opcode.SUB)]
stdlib['*'] = [Instr(Opcode.MUL)]
stdlib['/'] = [Instr(Opcode.DIV)]  # maybe external synthetic?
stdlib['mod'] = [Instr(Opcode.MOD)]
stdlib['and'] = [Instr(Opcode.AND)]
stdlib['or'] = [Instr(Opcode.OR)]
stdlib['invert'] = [Instr(Opcode.INV)]
stdlib['negate'] = [Instr(Opcode.NEG)]
stdlib['1-'] = [Instr(Opcode.DEC)]
stdlib['1+'] = [Instr(Opcode.NEG)]

# compare
stdlib['='] = [Instr(Opcode.CEQ)]
stdlib['<'] = [Instr(Opcode.CLT)]
stdlib['>'] = [Instr(Opcode.CGT)]
stdlib['<>'] = [Instr(Opcode.CEQ), Instr(Opcode.INV)]
stdlib['<='] = [Instr(Opcode.DEC), Instr(Opcode.CLT)]
stdlib['>='] = [Instr(Opcode.INC), Instr(Opcode.CGT)]

# stack
stdlib['dup'] = [Instr(Opcode.STKDUP)]
stdlib['drop'] = [Instr(Opcode.STKDRP)]
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

# io in
stdlib['io@'] = [Instr(Opcode.IN)]
stdlib['key'] = [
    gen_push(STDIN_DEV),
    gen_push(STDIN_DEFAULT_REG),
    *stdlib['io@'].code
]

# io out
stdlib['io!'] = [Instr(Opcode.OUT)]
stdlib['.'] = [
    gen_push(STDOUT_DEV),
    gen_push(STDOUT_INT_REG),
    *stdlib['io!'].code
]
stdlib['emit'] = [
    gen_push(STDOUT_DEV),
    gen_push(STDOUT_INT_REG),
    *stdlib['io!'].code
]
stdlib['cr'] = [
    gen_push(ord('\n')),
    *stdlib['emit'].code
]

# strings
stdlib['2drop'] = [Instr(Opcode.STKDRP), Instr(Opcode.STKDRP)]
stdlib['2dup'] = [Instr(Opcode.STKOVR), Instr(Opcode.STKOVR)]
stdlib.add_ext("type", [
    # TODO
])
stdlib['cells'] = []