from forth.main import parseAST
from lplib.lexer.tstream import CharStream

from compiler.forth.models import ForthCode
from compiler.forth.stdlib import stdlib
from compiler.forth.transformer import ForthTransformer


def translate_forth(forth_code: str) -> ForthCode:
    tr = ForthTransformer(funclib=stdlib)
    ast = parseAST(CharStream(forth_code))
    code = tr(ast)
    return code
