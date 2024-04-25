from pprint import pprint

from mcasm.parse import MCASMCompiler

txt = open("../test.mcasm", 'r').read()

comp = MCASMCompiler()
res = comp.compile(txt)
pprint(list(enumerate(res.commands)))
print(res.compiled)
print(res.labels)
