from pprint import pprint

from compiler.memory import linker, pack_binary
from src.compiler.translator.main import translate_forth


def compile_forth(text: str) -> bytes:
    code = translate_forth(text)
    flat = linker(code)
    _, binary = pack_binary(flat)
    return binary


if __name__ == "__main__":
    text = """

        variable vars
        3234 constant const
        123 vars !
        vars @
        do-fizz-buzz
        . key 
        : if1 1 if 0 else 1 then ;
        : if2 1 if 0 then ;
        : if4 1 if if 0 1 else if 1 3 else 4 5 then then then ;
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
        : loop-test  10 0 do i . loop ;
        """

    text = """
        : fizz?  3 mod 0 = dup if ." Fizz" + then ;
        : buzz?  5 mod 0 = dup if ." Buzz" then ;
        : fizz-buzz?  dup fizz? swap buzz? or invert ;
        : do-fizz-buzz  25 1 do cr i fizz-buzz? if i . then loop ;
        : test_while begin key dup . 32 = until ;
    test_while
    do-fizz-buzz
    
    
    ." Hello"
    1 2 3 4 5 + * - /
    """

    text = """
    : test 1 test ;
    : test2 1 test ;
    test
    12 3123 14212
    """

    code = translate_forth(text)
    flat = linker(code)
    words, binary = pack_binary(flat)
    # words = unpack_binary(binary)

    pprint(code)
    print(*flat, sep='\n')
    print(words)
    print(binary)
