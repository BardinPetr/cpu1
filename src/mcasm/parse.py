from lark import Lark

from mcasm.transformers.BaseTransformers import TypeTransformer
from mcasm.transformers.CodeTransformer import CompiledMC, CodeTransformer
from mcasm.transformers.ExecTransformer import ControlInstructionTransformer
from mcasm.transformers.IfTransformer import IfTransformer
from mcasm.transformers.JumpTransformer import JumpInstructionTransformer
from mcasm.transformers.LocationTransformers import LocationResolver
from mcasm.transformers.SwitchTransformer import SwitchTransformer
from src.mcasm.grammar import load_grammar


class MCASMCompiler:
    def __init__(self):
        self._lark = Lark(load_grammar())
        self._location_resolver = LocationResolver()
        self._transform = (
            TypeTransformer()
            * SwitchTransformer()
            * IfTransformer()
            * self._location_resolver
            * ControlInstructionTransformer()
            * JumpInstructionTransformer()
            * CodeTransformer()
        )

    def compile(self, text: str) -> CompiledMC:
        ast = self._lark.parse(text)
        info: CompiledMC = self._transform.transform(ast)
        info.labels = self._location_resolver.labels
        return info


def mc_compile(text: str) -> CompiledMC:
    comp = MCASMCompiler()
    return comp.compile(text)
