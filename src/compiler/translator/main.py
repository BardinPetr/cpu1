from forth.main import parseAST
from lplib.lexer.tstream import CharStream

from src.compiler.translator.utils.models import ForthCode
from src.compiler.translator.stdlib import stdlib
from src.compiler.translator.transformer import ForthTransformer


def translate_forth(forth_code: str) -> ForthCode:
    tr = ForthTransformer(funclib=stdlib)
    ast = parseAST(CharStream(forth_code))
    code = tr(ast)
    return code
