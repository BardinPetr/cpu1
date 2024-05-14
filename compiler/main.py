from pprint import pprint

from forth.main import parseAST
from lplib.lexer.tstream import CharStream

from compiler.transformer import ForthISATransformer, ForthLangTransformer

if __name__ == "__main__":
    text = """
        : fizz?  3 mod 0 = dup if ." Fizz" + then ;
        : buzz?  5 mod 0 = dup if ." Buzz" then ;
        : fizz-buzz?  dup fizz? swap buzz? or invert ;
        : do-fizz-buzz  25 1 do cr i fizz-buzz? if i . then loop ;
        : test_while begin key dup . 32 = until ;
        variable vars
        3 constant const
        123 vars !
        vars @
        do-fizz-buzz
        . key 
        : if1 cmd1 if cmd2 else cmd3 then ;
        : if2 cmd1 if cmd2 then ;
        : if4 cmd1 if if cmd2 cmd21 else if cmd3 cmd31 else cmd4 cmd41 then then then ;
        21 + / < emit @
        variable arr 4 cells allot
        : asasdas ( n1 n3 -- n2 ) asd ;
        \\ hey its a comment
        abc \\ no_abc
    """

    stream = CharStream(text)
    ast = parseAST(stream)

    ast = ForthISATransformer()(ast)
    # ast = ForthLangTransformer()(ast)

    pprint(ast)