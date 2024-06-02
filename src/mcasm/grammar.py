import pathlib


def load_grammar() -> str:
    file = pathlib.Path(__file__).parent.resolve().joinpath("uasm.lark")
    with open(file, "r") as f:
        return f.read()
