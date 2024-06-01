import re

SELECTED = [
    "MCType",
    "ALUCtrl", "ALUPortCtrl", "ALUFlagCtrl",
    "BusInCtrl", "BusOutCtrl",
    "MemCtrl", "StackCtrl",
    "MachineCtrl", "MachineIOCtrl"
]

template = """
<details>

<summary>Описания управляющих сигналов микрокоманды</summary>

#### Типы полей:

{}

</details>
"""

if __name__ == "__main__":
    source = open("arch.py", "r").read()
    classes = re.finditer(r"^class (\w+).*?\n\n", source, re.DOTALL | re.MULTILINE)
    classes = [
        f"```python\n{i.group(0).strip()}\n```"
        for i in classes
        if i.group(1) in SELECTED
    ]
    classes = '\n\n'.join(classes)

    res = template.format(classes)
    with open("readme.md", "w") as f:
        f.write(res)
        print(res)
