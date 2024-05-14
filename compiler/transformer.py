from dataclasses import dataclass, field
from hashlib import sha1
from pprint import pprint
from typing import Dict, List, Optional, Tuple

from lplib.lexer.tokens import Token
from lplib.parser.transformer import Transformer

from compiler.isa import ImmInstr, Opcode, Instruction, IPRelInstr, Instr


@dataclass
class ForthVariable:
    name: str
    loc: int
    size_slots: int
    init_value: Optional[List[int]] = None

    def __post_init__(self):
        assert not self.init_value or len(self.init_value) == self.size_slots


@dataclass
class Command:
    pass


@dataclass
class ForthFunction:
    name: str
    loc: int
    code: List[Command]

    def __post_init__(self):
        self.size_slots = len(self.code) * 1


def const_string_var_name(string: str) -> str:
    return "cstr_sha1_" + sha1(string.encode()).digest().hex()


class ForthTransformer(Transformer):
    SLOT_SIZE = 1

    def __init__(self):
        super().__init__()
        self.__constants: Dict[str, int] = {}
        self.__variables: Dict[str, ForthVariable] = {}
        self.__functions: Dict[str, ForthFunction] = {}
        self.__storage_mem_pos = 0
        self.__func_mem_pos = 0

    def __create_variable(self, name, slots=1, init_value: Optional[List[int]] = None) -> ForthVariable:
        """
        Create name variable of given size
        :return: created variable
        """
        if name in self.__variables:
            raise Exception(f"Variable {name} redefined")
        if init_value:
            slots = len(init_value)
        var = ForthVariable(name, self.__storage_mem_pos, slots, init_value)
        self.__variables[name] = var
        self.__storage_mem_pos += slots
        return var

    def cmd_push(self, value: int):
        return ImmInstr(Opcode.IPUSH, imm=value)

    """ Strings """

    def cmd_str(self, token: Token) -> List[Instruction]:
        """For defining const string and returning its (add, len)"""
        text = token.value
        data = text.encode('ascii')
        name = const_string_var_name(text)
        if not (var := self.__variables.get(name, None)):
            var = self.__create_variable(name, init_value=data)
        return [
            self.cmd_push(var.loc),
            self.cmd_push(var.size_slots)
        ]

    def cmd_io_str(self, token: Token) -> List[Instruction]:
        """For inplace print string"""
        return [
            self.cmd_str(token),
            self.cmd_call("type")
        ]

    """ Definitions """

    def def_const(self, name, value):
        if name in self.__constants:
            raise Exception(f"Constant {name} redefined")
        self.__constants[name] = value

    def def_var(self, name):
        self.__create_variable(name)

    def def_arr(self, name, count):
        self.__create_variable(name, count + 1)

    def function(self, name, lines):
        """
        Functions are stored in dictionary, and on creation assigned with their memory location.
        Function is just code segment with ret added to it in the end
        """

        if name in self.__functions:
            raise Exception(f"Function {name} redefined")

        lines.append(Instr(Opcode.RET))

        func = ForthFunction(name, self.__func_mem_pos, lines)
        self.__functions[name] = func
        self.__func_mem_pos += func.size_slots

    """ Control structures """

    def if_expr(self, *branches):
        """
        IF and IF-ELSE structures.
        Uses inverted conditional jump to minify code
        """
        if len(branches) == 1:
            # if-then
            br_true = branches[0]
            return [
                IPRelInstr(Opcode.IJMPF, rel=len(br_true)),
                *br_true
            ]

        # if-else-then
        br_true, br_false = branches
        rel_jump_to_false = len(br_true) + 1
        rel_jump_to_end = len(br_false)
        return [
            IPRelInstr(Opcode.IJMPF, rel=rel_jump_to_false),  # if `FALSE` jump to `label_false`
            *br_true,
            IPRelInstr(Opcode.IJMP, rel=rel_jump_to_end),  # jump to `label_end`
            # label_false
            *br_false
            # label_end
        ]

    def do_while_expr(self, body):
        """
        Run body, then jump to body start if stack top is false
        """
        to_beginning = len(body) + 1
        return [
            *body,
            IPRelInstr(Opcode.IJMPF, rel=-to_beginning),
        ]

    def while_expr(self, check, body):
        """
        Run check, if stack top is true continue to body, then jump to check beginning
                   else jump after body
        """
        to_beginning = len(body) + len(check) + 2
        to_outside = len(body) + 1
        return [
            *check,
            IPRelInstr(Opcode.IJMPF, rel=to_outside),
            *body,
            IPRelInstr(Opcode.IJMP, rel=-to_beginning),
        ]

    def for_expr(self, body):
        """
        For loop.
        Uses R-stack to store current index and end index [end, cur TOP].
        `i` word is just peek from R-stack to D-stack.
        On init copies range to R-stack is same order.
        After body increases R TOP, and compares with end. If not equal, jump to body beginning.
        Else, on exit clear R-stack.
        """
        post = [
            Instr(Opcode.INC, stack=1),
            Instr(Opcode.STKOVR, stack=1),
            Instr(Opcode.STKOVR, stack=1),
            Instr(Opcode.CEQ, stack=1),
        ]
        to_body = len(body) + len(post) + 1
        return [
            Instr(Opcode.STKMV),
            Instr(Opcode.STKMV),
            Instr(Opcode.XCHG, stack=1),
            *body,
            *post,
            IPRelInstr(Opcode.IJMPF, stack=1, rel=-to_body),
            Instr(Opcode.STKPOP, stack=1),
            Instr(Opcode.STKPOP, stack=1)
        ]

    """ Word execution """

    def cmd_call(self, word: str):
        """
        Parse function calls, internal word calls, synthetic word calls, constant and variables evaluation
        Internal word calls translates directly to opcodes, and synthetic to
        """
        if const := self.__constants.get(word, None):
            return self.cmd_push(const)

        if var := self.__variables.get(word, None):
            return self.cmd_push(var.loc)

        if func := self.__functions.get(word, None):
            # relative address would be substituted in second pass
            return IPRelInstr(Opcode.ICALL, abs=func.loc)

        # if internal := self.__
        # raise ValueError(f"Word {word} has no meaning")
        # TODO
        return word

    """ Code blocks """

    # TODO unwind code

    def program(self, *lines):
        pprint(self.__functions)
        return lines  # TODO
