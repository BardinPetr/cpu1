from typing import List, Optional

from tabulate import tabulate

from isa.main import Opcode


def stack_effect_fmt(x: Optional[List[List[str]]]) -> str:
    if x is None:
        return ""
    jn = lambda i: "; ".join(i)
    return f"[ {jn(x[0])} ] -> [ {jn(x[1])} ]"


def gen_eff(cnt=None, out=None, op=None, names: Optional[List[str]] = None):
    if names is None:
        names = [chr(ord("a") + i) for i in range(0, cnt)]
    else:
        cnt = len(names)

    if cnt is None:
        return tuple(), tuple()

    res = []
    if op is not None:
        if cnt == 1:
            res.append(f"{op}{names[0]}")
        else:
            res.append(op.join(names))
    elif out is not None:
        if isinstance(out, List):
            res += out
        else:
            res.append(out)
    return names, res


DESCRIPTIONS = {
    Opcode.ADD: ["", gen_eff(2, op="+"), None, None],
    Opcode.SUB: ["", gen_eff(2, op="-"), None, None],
    Opcode.DIV: ["", gen_eff(2, op="/"), None, None],
    Opcode.MUL: ["", gen_eff(2, op="*"), None, None],
    Opcode.MOD: ["", gen_eff(2, op="%"), None, None],
    Opcode.AND: ["", gen_eff(2, op="&"), None, None],
    Opcode.OR: ["", gen_eff(2, op="\\|"), None, None],
    Opcode.INV: ["", gen_eff(1, op="~"), None, None],
    Opcode.INC: ["", gen_eff(1, "a+1"), None, None],
    Opcode.DEC: ["", gen_eff(1, "a-1"), None, None],
    Opcode.NEG: ["", gen_eff(1, op="-"), None, None],
    Opcode.CLTU: ["", gen_eff(2, "a<b"), None, "uses C flag, F=0, T=1"],
    Opcode.CGTU: ["", gen_eff(2, "a>b"), None, "same"],
    Opcode.CLTS: ["", gen_eff(2, "a<b"), None, "uses V^C flag, F=0, T=1"],
    Opcode.CGTS: ["", gen_eff(2, "a>b"), None, "same"],
    Opcode.CEQ: ["", gen_eff(2, "a==b"), None, "uses Z flag, F=0, T=1"],
    Opcode.ISTKPSH: ["IMM16, SEL", gen_eff(0, "IMM"), None, None],
    Opcode.STKMV: ["SEL", gen_eff(1, ""), gen_eff(0, "a"), None],
    Opcode.STKCP: ["SEL", gen_eff(1, "a"), gen_eff(0, "a"), None],
    Opcode.STKPOP: ["SEL", gen_eff(1, ""), None, None],
    Opcode.STKOVR: ["SEL", gen_eff(2, ["a", "b", "a"]), None, None],
    Opcode.STKDUP: ["SEL", gen_eff(1, ["a", "a"]), None, None],
    Opcode.STKSWP: ["SEL", gen_eff(2, ["b", "a"]), None, None],
    Opcode.FETCH: ["", gen_eff(names=["addr"], out="val"), None, "val <= MEM[addr]"],
    Opcode.STORE: [
        "",
        gen_eff(names=["val", "addr"], out=""),
        None,
        "MEM[addr] <= val",
    ],
    Opcode.AJMP: ["", gen_eff(names=["addr"]), None, "IP <= addr"],
    Opcode.RJMP: ["IMM16", None, None, "IP <= IP + IMM"],
    Opcode.RCALL: ["IMM16", None, gen_eff(0, out="IPold"), "IP <= IP + IMM"],
    Opcode.CJMP: [
        "IMM16",
        gen_eff(names=["val"]),
        None,
        "if val[0] == 0 then IP <= IP + IMM",
    ],
    Opcode.RET: ["", None, gen_eff(names=["addr"], out=""), "IP <= addr"],
    Opcode.HLT: ["", None, None, "stop machine"],
    Opcode.NOP: ["", None, None, "no operation"],
    Opcode.IN: ["", gen_eff(names=["reg"], out="val"), None, "val <= IO[reg]"],
    Opcode.OUT: ["", gen_eff(names=["val", "reg"], out=""), None, "IO[reg] <= val"],
}

if __name__ == "__main__":
    cmds = sorted(Opcode, key=lambda x: x.identifier)
    cmds = [
        [
            i.group.name,
            i.name,
            f"{i.group:04b}",
            f"{i.alt:04b}",
            DESCRIPTIONS[i][0] or "",
            stack_effect_fmt(DESCRIPTIONS[i][1]),
            stack_effect_fmt(DESCRIPTIONS[i][2]),
            DESCRIPTIONS[i][3] or "",
        ]
        for i in cmds
    ]
    table = tabulate(
        cmds,
        headers=[
            "",
            "",
            "Group",
            "Alt",
            "Params",
            "Base stack eff",
            "Other stack eff",
            "Effect",
        ],
        tablefmt="github",
        stralign="left",
    )

    res = f"""
<details>

<summary>Таблица</summary>

{table}
 
</details>
"""

    with open("readme.md", "w") as f:
        f.write(res)
        print(table)
