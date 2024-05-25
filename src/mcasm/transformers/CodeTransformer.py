from dataclasses import dataclass
from typing import List, Dict

from lark import Transformer, Token

from src.machine.mc.mcinstr import MCInstruction


@dataclass
class CompiledMC:
    commands: List[MCInstruction]
    labels: Dict[str, int]

    def __post_init__(self):
        self.compiled = [i.compile() for i in self.commands]


class CodeTransformer(Transformer):

    def line(self, line: List[Token]):
        return line[-1]

    def start(self, lines):
        return CompiledMC(lines, {})
