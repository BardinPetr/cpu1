from mcasm.parse import MCASMCompiler

txt = """
label1:
(RF_IP(NOT) PASSA IGNORE(INC)) -> PS, set(Z N C V) store;
(RF_IP PASSA IGNORE(INC NOT)) -> PS, set(Z N C V) store;
label3:  (RF_IP PASSA) -> PS set(Z,N,C,V) store;
(PASSA) -> PS set(V);
(PASSA) set(V);
(ZERO);
label5:
jump 0x3;
JmP 3;
jump label1;
if (RF_IP PASSA)[10] == 0 jump label3;
"""

comp = MCASMCompiler()
res = comp.compile(txt)
print(res.commands)
print(res.compiled)
