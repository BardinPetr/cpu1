enums = {'PSFlags':                 {'Z':   0, 'N': 1, 'C': 2, 'V': 3, 'RUN': 4, 'INT': 5,
                                     'IEN': 6},
         'RegFileIdCtrl':           {'XX': 0, 'IP': 1, 'CR': 2, 'YY': 3}, 'RegisterIdCtrl': {'CR': 0},
         'BusInCtrl':               {'IGNORE': 0, 'PS': 1, 'DRR': 2, 'SRC_3': 3, 'RF_XX': 4, 'RF_IP': 5, 'RF_CR': 6,
                                     'RF_YY':  7},
         'BusOutCtrl':              {'IGNORE': 0, 'PS': 1, 'DRW': 2, 'AR': 3, 'RF_XX': 4, 'RF_IP': 5, 'RF_CR': 6,
                                     'RF_YY':  7},
         'RegFileOrNormalRegister': {'NR': 0, 'RF': 1}, 'MemCtrl': {'IGN': 0, 'WR': 1},
         'ALUCtrl':                 {'ZERO': 0, 'PASSA': 1, 'PASSB': 2, 'AND': 3, 'OR': 4, 'ADD': 5, 'ADC': 6, 'SHL': 7,
                                     'SHR':  8,
                                     'ASL':  9, 'ASR': 10, 'ROL': 11, 'ROR': 12},
         'ALUPortCtrl':             {'PASS': 0, 'NOT': 1, 'INC': 2, 'SXT8': 4, 'SXT16': 8},
         'ALUFlagCtrl':             {'SETZ': 1, 'SETN': 2, 'SETV': 8, 'SETC': 4}}

res = "\n".join(
    f'{name.upper()}: ' + " | ".join([f'"{i}"' for i in vals.keys()])
    for name, vals in enums.items()
)

print(res)
