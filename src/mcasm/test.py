from pprint import pprint

from src.mcasm.parse import MCASMCompiler

txt = """
start:
(IP PASSA) -> AR;
(DRR PASSA) -> CR;
(IP(INC) PASSA) -> IP;

if (CR PASSA)[31] == 1 {
    (PASSA);
} else {
    (PASSB);
};

jmp start;
"""

comp = MCASMCompiler()
res = comp.compile(txt)
pprint(list(enumerate(res.commands)))
print(res.compiled)
print(res.labels)
