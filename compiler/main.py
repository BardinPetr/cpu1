from pprint import pprint

from forth.main import parseAST
from lplib.lexer.tstream import CharStream

from compiler.transformer import ForthTransformer

if __name__ == "__main__":
    text = """
        : fizz?  3 mod 0 = dup if ." Fizz" + then ;
        : buzz?  5 mod 0 = dup if ." Buzz" then ;
        : fizz-buzz?  dup fizz? swap buzz? or invert ;
        : do-fizz-buzz  25 1 do cr i fizz-buzz? if i . then loop ;
        : test_while begin key dup . 32 = until ;
        variable vars
        3234 constant const
        123 vars !
        vars @
        do-fizz-buzz
        . key 
        : if1 cmd1 if cmd2 else cmd3 then ;
        : if2 cmd1 if cmd2 then ;
        : if4 cmd1 if if cmd2 cmd21 else if cmd3 cmd31 else cmd4 cmd41 then then then ;
        21 + / < emit @
        variable arr 4 cells allot
        variable v2
        : asasdas ( n1 n3 -- n2 ) asd ;
        \\ hey its a comment
        abc \\ no_abc
        vars ! vars @
        const
        arr
        v2
        ." dsads"
        s" sadadasd sad as"
        ." dsads"
        : print-keycode begin key 33 = invert while key emit repeat ;
        : print-keycode-do  begin key dup . 32 = until ;
    """

    stream = CharStream(text)
    ast = parseAST(stream)

    # print(ast.print())

    ast = ForthTransformer()(ast)
    # ast = ForthLangTransformer()(ast)

    pprint(ast)
    # TODO cells in lexer&parser
