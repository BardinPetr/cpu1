from src.machine.arch import *  # noqa F403

enums = extract_enums()  # noqa F405

for name, vals in enums.items():
    print(name)
    print(*vals, sep="\n")

res = "\n".join(
    f"{name.upper()}: " + " | ".join([f'"{i}"' for i in vals.keys()])
    for name, vals in enums.items()
)

print(res)
