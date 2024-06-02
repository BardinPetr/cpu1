def load(path):
    return open(path, "r").read()


FILE_ORDER = [
    "arch.md",
    "mcisa/readme.md",
    "enums/readme.md",
    "mcasm.md",
    "isa.md",
    "isa/readme.md",
    "io.md",
    "mem.md",
    "forth.md",
    "sim.md",
]
contents = map(load, FILE_ORDER)
contents = "\n\n".join(contents)

base = load("readme.md.template")
base = base.format(contents)

with open("../readme.md", "w") as f:
    f.write(base)

