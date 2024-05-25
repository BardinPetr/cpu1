import pathlib
from typing import List

from mcasm.transformers.CodeTransformer import CompiledMC
from src.mcasm.parse import mc_compile


def _load():
    file = (pathlib.Path(__file__)
            .parent
            .resolve()
            .joinpath("main.mcasm"))
    with open(file, "r") as f:
        text = f.read()
    return mc_compile(text)


MICROCODE: CompiledMC = _load()
ROM: List[int] = MICROCODE.compiled
