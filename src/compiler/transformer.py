import re
from typing import Dict, List, Optional

from forth.main import parseAST
from lplib.lexer.tokens import Token
from lplib.lexer.tstream import CharStream
from lplib.parser.models import PNode
from lplib.parser.transformer import Transformer

from compiler.forthlib.stdlib import stdlib
from compiler.utils.funclib import FunctionLibrary
from compiler.utils.models import ForthVariable, ForthCode, Instructions
from compiler.utils.synthetic import Synthetic, const_string_var_name, unwrap_code, Syn
from isa.main import Opcode
from isa.model.instructions import Instr, ImmInstr, IPRelImmInstr, AbsImmInstr


class ForthTransformer(Transformer):
    SLOT_SIZE = 1

    def __init__(self, funclib: Optional[FunctionLibrary] = None):
        super().__init__()

        self.__functions: FunctionLibrary = FunctionLibrary()
        if funclib:
            self.__functions += funclib

        self.__storage_mem_pos = 0
        self.__constants: Dict[str, int] = {}
        self.__variables: Dict[str, ForthVariable] = {}

    def __is_name_exists(self, name) -> bool:
        return name in self.__variables or name in self.__functions or name in self.__constants

    def __create_variable(self, name, slots=1, init_value: Optional[List[int] | bytes] = None) -> ForthVariable:
        """
        Create name variable of given size
        :return: created variable
        """
        if self.__is_name_exists(name):
            raise Exception(f"Variable {name} redefined")

        if init_value:
            if isinstance(init_value, bytes):
                init_value = [i for i in init_value]
            slots = len(init_value)
        var = ForthVariable(name, self.__storage_mem_pos, slots, init_value)
        self.__variables[name] = var
        self.__storage_mem_pos += slots
        return var

    def cmd_push(self, value: int) -> Synthetic:
        return Syn.one(ImmInstr(Opcode.ISTKPSH, imm=value))

    """ Strings """

    def cmd_str(self, token: Token) -> Synthetic:
        """
        For defining const string and returning its address
        String is stored as [length_byte, *data_bytes]
        """
        text = token.value
        text_enc = text.encode('ascii')
        data = [len(text_enc), *text_enc]

        name = const_string_var_name(text)
        if not (var := self.__variables.get(name, None)):
            var = self.__create_variable(name, init_value=data)

        return self.cmd_call(var.name)  # pull var address in valid form

    def cmd_io_str(self, token: Token) -> Synthetic:
        """For inplace print string"""
        return Syn.many(
            self.cmd_str(token),
            self.cmd_call("type")
        )

    """ Definitions """

    def def_const(self, name, value):
        if self.__is_name_exists(name):
            raise Exception(f"Constant {name} redefined")
        self.__constants[name] = value

    def def_var(self, name):
        self.__create_variable(name)

    def def_arr(self, name, count):
        self.__create_variable(name, count + 1)

    """ Word execution """

    def cmd_call(self, word: str) -> Synthetic:
        """
        Parse function calls, and inline word calls, constant and variables evaluation
        """
        if const := self.__constants.get(word, None):
            return self.cmd_push(const)

        if var := self.__variables.get(word, None):
            return Syn.one(
                AbsImmInstr(Opcode.ISTKPSH, imm=var.loc)
            )

        if func := self.__functions[word]:
            if func.is_inline:
                return Syn.many(*func.code)

            # relative address would be substituted in second pass
            return Syn.one(
                IPRelImmInstr(Opcode.RCALL, abs=func.loc)
            )

        raise ValueError(f"Word {word} has no meaning")

    """HERE BEGINS LANGUAGE STRUCTURES PART"""

    """ Control structures """

    def if_expr(self, *branches: Instructions) -> Synthetic:
        """
        IF and IF-ELSE structures.
        Uses inverted conditional jump to minify code
        """
        if len(branches) == 1:
            # if-then
            br_true = branches[0]
            return Syn.many(
                IPRelImmInstr(Opcode.CJMP, rel=len(br_true)),
                *br_true
            )

        # if-else-then
        br_true, br_false = branches
        rel_jump_to_false = len(br_true) + 1
        rel_jump_to_end = len(br_false)
        return Syn.many(
            IPRelImmInstr(Opcode.CJMP, rel=rel_jump_to_false),  # if `FALSE` jump to `label_false`
            *br_true,
            IPRelImmInstr(Opcode.RJMP, rel=rel_jump_to_end),  # jump to `label_end`
            # label_false
            *br_false
            # label_end
        )

    def do_while_expr(self, body: Instructions) -> Synthetic:
        """
        Run body, then jump to body start if stack top is false
        """
        to_beginning = len(body) + 1
        return Syn.many(
            *body,
            IPRelImmInstr(Opcode.CJMP, rel=-to_beginning),
        )

    def while_expr(self, check, body: Instructions) -> Synthetic:
        """
        Run check, if stack top is true continue to body, then jump to check beginning
                   else jump after body
        """
        to_beginning = len(body) + len(check) + 2
        to_outside = len(body) + 1
        return Syn.many(
            *check,
            IPRelImmInstr(Opcode.CJMP, rel=to_outside),
            *body,
            IPRelImmInstr(Opcode.RJMP, rel=-to_beginning),
        )

    def for_expr(self, body: Instructions) -> Synthetic:
        """
        For loop.
        Uses R-stack to store current index and end index [end, cur].
        `i` word is just peek from R-stack to D-stack.
        On init copies range to R-stack is same order.
        After body increases R TOP, and compares with end. If not equal, jump to body beginning.
        Else, on exit clear R-stack.
        """
        post = [
            Instr(Opcode.STKMV, stack=1),
            Instr(Opcode.INC),  # move cur and inc to D
            Instr(Opcode.STKCP, stack=1),  # copy end to D
            Instr(Opcode.STKOVR, stack=0),
            Instr(Opcode.STKMV, stack=0),  # copy new cur to R
            Instr(Opcode.CEQ),
        ]
        to_body = len(body) + len(post) + 1  # 1 for CJMP
        return Syn.many(
            Instr(Opcode.STKMV),
            Instr(Opcode.STKMV),
            Instr(Opcode.STKSWP, stack=1),
            *body,
            *post,
            IPRelImmInstr(Opcode.CJMP, rel=-to_body),
            Instr(Opcode.STKPOP, stack=1),
            Instr(Opcode.STKPOP, stack=1)
        )

    """Functions"""

    def before_function(self, tree: PNode):
        # preallocate function to be able to recurse
        name = tree.values[0]
        self.__functions.add_ext_begin(name)
        return tree

    def function(self, name, lines: Instructions):
        """
        Functions are stored in dictionary, and on creation assigned with their memory location.
        Function is just code segment with ret added to it in the end
        """
        lines.append(Instr(Opcode.RET))
        self.__functions.add_ext_end(name, lines)

    """ Code blocks """

    def func_body(self, *lines) -> Instructions:
        """
        Before passing code block
        to some control structure (which consumes func_body)
        unwind nested synthetic commands to list
        """
        return unwrap_code(lines)

    def program(self, *lines) -> ForthCode:
        lines = unwrap_code(lines)
        return ForthCode(
            lines,
            self.__variables,
            self.__functions.to_memory()
        )


def preprocess_forth(code: str) -> str:
    import_re = re.compile(r"\\import (/?(?:[^/\s]+/)*[^/\s]+)")

    files = set(import_re.findall(code))
    try:
        libs = "\n".join(open(i, "r").read() for i in files)
    except IOError:
        raise ValueError(f"Invalid include paths: {files}")

    return libs + import_re.sub("", code)


def translate_forth(forth_code: str) -> ForthCode:
    ast = parseAST(CharStream(preprocess_forth(forth_code)))
    return ForthTransformer(funclib=stdlib)(ast)
