from pprint import pprint

from src.mcasm.parse import MCASMCompiler

txt = """
if (CR PASSA)[30] == 0 {
    if (CR PASSA)[29] == 0 {
        if (CR PASSA)[28] == 0 {
            # group 0000 : GMTH
            jmp 0;
        } else {
            # group 0001 : GSTK
            jmp 1;
        };
    } else {
        if (CR PASSA)[28] == 0 {
            jmp 2;
        } else {
            jmp 3;
        };
    };
} else {
    if (CR PASSA)[29] == 0 {
        if (CR PASSA)[28] == 0 {
            jmp 4;
        } else {
            jmp 5;
        };
    } else {
        if (CR PASSA)[28] == 0 {
            jmp 6;
        } else {
            jmp 7;
        };
    };
};
"""

txt = """
#         if (CR PASSA)[28] == 0 {
#             jmp 66;
#         } else {
#             jmp 77;
#         };
#         
# switch (CR PASSA)[21:20] {
#     case 0b0 {
#         if (CR PASSA)[28] == 0 {
#             jmp 66;
#         } else {
#             jmp 77;
#         };
#     }
#     case 0b1 {
#         jmp 1;
#     }
# };
switch (CR PASSA)[30:28] {
    case 0b000 {
        if (CR PASSA)[28] == 0 {
            jmp 66;
        } else {
            jmp 77;
        };
            }
    case 0b001 {
        jmp 1;
    }
    case 0b010 {
        jmp 2;
    }
    case 0b011 {
        jmp 3;
    }
    case 0b100 {
        jmp 4;
    }
    case 0b101 {
        jmp 5;
    }
    case 0b110 {
        jmp 6;
    }
    case 0b111 {
        jmp 7;
    }
};
"""

comp = MCASMCompiler()
res = comp.compile(txt)
pprint(list(enumerate(res.commands)))
print(res.compiled)
print(res.labels)
