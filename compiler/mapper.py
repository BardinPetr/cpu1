from forth.lexer.tokens import ForthTokenType
from lplib.lexer.tokens import TokenType

from isa import Opcode

__FORTH_DIRECT_ISA_MAP = {
    ForthTokenType.MATH_ADD: Opcode.ADD,
    ForthTokenType.MATH_SUB: Opcode.SUB,
    ForthTokenType.MATH_DIV: Opcode.DIV,
    ForthTokenType.MATH_MUL: Opcode.MUL,
    ForthTokenType.MATH_MOD: Opcode.MOD,

    ForthTokenType.LOG_INV:  Opcode.INV,
    ForthTokenType.LOG_AND:  Opcode.AND,
    ForthTokenType.LOG_OR:   Opcode.OR,

    ForthTokenType.CMP_EQ:   Opcode.CEQ,
    ForthTokenType.CMP_LT:   Opcode.CLT,
    ForthTokenType.CMP_GT:   Opcode.CGT,
}


def map_to_opcode(token: TokenType) -> Opcode:
    opcode = __FORTH_DIRECT_ISA_MAP.get(token, None)
    if opcode is None:
        raise ValueError(f"No translation for token {token}")
    return opcode
