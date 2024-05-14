from forth.lexer.tokens import ForthTokenType
from lplib.lexer.tokens import TokenType, Token

from isa import Opcode, Instruction

# __FORTH_DIRECT_ISA_MAP = {
#     ForthTokenType.MATH_ADD:      Opcode.ADD,
#     ForthTokenType.MATH_SUB:      Opcode.SUB,
#     ForthTokenType.MATH_DIV:      Opcode.DIV,
#     ForthTokenType.MATH_MUL:      Opcode.MUL,
#     ForthTokenType.MATH_MOD:      Opcode.MOD,
#
#     ForthTokenType.LOG_INV:       Opcode.INV,
#     ForthTokenType.LOG_AND:       Opcode.AND,
#     ForthTokenType.LOG_OR:        Opcode.OR,
#
#     ForthTokenType.CMP_EQ:        Opcode.CEQ,
#     ForthTokenType.CMP_LT:        Opcode.CLT,
#     ForthTokenType.CMP_GT:        Opcode.CGT,
#
#     ForthTokenType.MEM_STORE:     Opcode.STORE,
#     ForthTokenType.MEM_STORE_INC: Opcode.INCSTORE,
#     ForthTokenType.MEM_FETCH:     Opcode.FETCH,
# }


# def map_to_opcode(token: Token) -> Instruction:
    # opcode = __FORTH_DIRECT_ISA_MAP.get(token.type_id, None)
    # if opcode is None:
    #     raise ValueError(f"No translation for token {token}")
    # return Instruction(opcode)

# TODO implement:  type, i,
