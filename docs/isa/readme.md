
<details>

<summary>Таблица</summary>

|      |         |   Group |   Alt | Params     | Base stack eff          | Other stack eff   | Effect                             |
|------|---------|---------|-------|------------|-------------------------|-------------------|------------------------------------|
| GIOC | HLT     |    0000 |  0000 |            |                         |                   | stop machine                       |
| GIOC | NOP     |    0000 |  0001 |            |                         |                   | no operation                       |
| GIOC | IN      |    0000 |  0010 |            | [ reg ] -> [ val ]      |                   | val <= IO[reg]                     |
| GIOC | OUT     |    0000 |  0011 |            | [ val; reg ] -> [  ]    |                   | IO[reg] <= val                     |
| GMTH | ADD     |    0001 |  0000 |            | [ a; b ] -> [ a+b ]     |                   |                                    |
| GMTH | SUB     |    0001 |  0001 |            | [ a; b ] -> [ a-b ]     |                   |                                    |
| GMTH | DIV     |    0001 |  0010 |            | [ a; b ] -> [ a/b ]     |                   |                                    |
| GMTH | MUL     |    0001 |  0011 |            | [ a; b ] -> [ a*b ]     |                   |                                    |
| GMTH | MOD     |    0001 |  0100 |            | [ a; b ] -> [ a%b ]     |                   |                                    |
| GMTH | AND     |    0001 |  0101 |            | [ a; b ] -> [ a&b ]     |                   |                                    |
| GMTH | OR      |    0001 |  0110 |            | [ a; b ] -> [ a\|b ]    |                   |                                    |
| GMTH | INV     |    0001 |  0111 |            | [ a ] -> [ ~a ]         |                   |                                    |
| GMTH | INC     |    0001 |  1000 |            | [ a ] -> [ a+1 ]        |                   |                                    |
| GMTH | DEC     |    0001 |  1001 |            | [ a ] -> [ a-1 ]        |                   |                                    |
| GMTH | NEG     |    0001 |  1010 |            | [ a ] -> [ -a ]         |                   |                                    |
| GSTK | ISTKPSH |    0010 |  0000 | IMM16, SEL | [  ] -> [ IMM ]         |                   |                                    |
| GSTK | STKMV   |    0010 |  0001 | SEL        | [ a ] -> [  ]           | [  ] -> [ a ]     |                                    |
| GSTK | STKCP   |    0010 |  0010 | SEL        | [ a ] -> [ a ]          | [  ] -> [ a ]     |                                    |
| GSTK | STKPOP  |    0010 |  0011 | SEL        | [ a ] -> [  ]           |                   |                                    |
| GSTK | STKOVR  |    0010 |  0100 | SEL        | [ a; b ] -> [ a; b; a ] |                   |                                    |
| GSTK | STKDUP  |    0010 |  0101 | SEL        | [ a ] -> [ a; a ]       |                   |                                    |
| GSTK | STKSWP  |    0010 |  0110 | SEL        | [ a; b ] -> [ b; a ]    |                   |                                    |
| GCMP | CLTU    |    0011 |  0000 |            | [ a; b ] -> [ a<b ]     |                   | uses C flag, F=0, T=1              |
| GCMP | CGTU    |    0011 |  0001 |            | [ a; b ] -> [ a>b ]     |                   | same                               |
| GCMP | CLTS    |    0011 |  0010 |            | [ a; b ] -> [ a<b ]     |                   | uses V^C flag, F=0, T=1            |
| GCMP | CGTS    |    0011 |  0011 |            | [ a; b ] -> [ a>b ]     |                   | same                               |
| GCMP | CEQ     |    0011 |  0100 |            | [ a; b ] -> [ a==b ]    |                   | uses Z flag, F=0, T=1              |
| GJMP | AJMP    |    0100 |  0000 |            | [ addr ] -> [  ]        |                   | IP <= addr                         |
| GJMP | RJMP    |    0100 |  0001 | IMM16      |                         |                   | IP <= IP + IMM                     |
| GJMP | CJMP    |    0100 |  0010 | IMM16      | [ val ] -> [  ]         |                   | if val[0] == 0 then IP <= IP + IMM |
| GJMP | RCALL   |    0100 |  0011 | IMM16      |                         | [  ] -> [ IPold ] | IP <= IP + IMM                     |
| GJMP | RET     |    0100 |  0100 |            |                         | [ addr ] -> [  ]  | IP <= addr                         |
| GMEM | FETCH   |    0101 |  0000 |            | [ addr ] -> [ val ]     |                   | val <= MEM[addr]                   |
| GMEM | STORE   |    0101 |  0001 |            | [ val; addr ] -> [  ]   |                   | MEM[addr] <= val                   |
 
</details>
