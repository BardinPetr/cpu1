from machine.arch import *

enums = extract_enums()

res = "\n".join(
    f'{name.upper()}: ' + " | ".join([f'"{i}"' for i in vals.keys()])
    for name, vals in enums.items()
)

print(res)
