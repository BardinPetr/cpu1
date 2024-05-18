| Mnemonics | Operands | DS before | DS after | RS before | RS after | Mem    | Priority |
|-----------|----------|-----------|----------|-----------|----------|--------|----------|
| ADD       |          | A, B      |          |           |          |        | H        |
| ADC       |          | A, B      |          |           |          |        | L        |
| SUB       |          | A, B      |          |           |          |        | H        |
| MUL       |          | A, B      |          |           |          |        | M        |
| DIV       |          | A, B      |          |           |          |        | L        |
| AND       |          | A, B      |          |           |          |        | H        |
| OR        |          | A, B      |          |           |          |        | H        |
| XOR       |          | A, B      |          |           |          |        | L        |
| ASL       |          | A, B      |          |           |          |        | M        |
| ASR       |          | A, B      |          |           |          |        | M        |
| ROL       |          | A, B      |          |           |          |        | M        |
| ROR       |          | A, B      |          |           |          |        | M        |
| NOT       |          | A         |          |           |          |        | H        |
| NEG       |          | A         |          |           |          |        | H        |
|           |          |           |          |           |          |        | H        |
| DPUSH     | IMM      |           | IMM      |           |          |        | H        |
| RPUSH     | IMM      |           |          |           | IMM      |        | H        |
| LD        |          | A         | MEM(A)   |           |          |        | H        |
| ST        |          | A, B      |          |           |          | A -> B | H        |
| D2R       |          | A         |          |           | A        |        | H        |
| R2D       |          |           | B        | B         |          |        | H        |
|           |          |           |          |           |          |        | H        |
|           |          |           |          |           |          |        | H        |
|           |          |           |          |           |          |        | H        |
|           |          |           |          |           |          |        | H        |
|           |          |           |          |           |          |        | H        |
|           |          |           |          |           |          |        | H        |
|           |          |           |          |           |          |        | H        |
|           |          |           |          |           |          |        | H        |
|           |          |           |          |           |          |        | H        |
|           |          |           |          |           |          |        | H        |
| NOP       |          |           |          |           |          |        | H        |
| HLT       |          |           |          |           |          |        | H        |

#

| ABBR | VAR      | SIZE      |
|------|----------|-----------|
| SID  | D,R      | 2b        |
| REG  | PS,IP,?? | 2b        |
| IMMV |          | 8b        |
| IMMA |          | ADDR_BITS |

## LD(SID, SRC)

Semantics: stacks[SID].push(fetch(SRC))

### LDI IMMV

fetch(SRC) eq IMMV

### LDR REG

fetch(SRC) eq registers.read(REG)

### LDM IMMA

fetch(SRC) eq ram.read(IMMA)

## ST(SID, DST)

Semantics: DST <- stacks[SID].pop()

## JCP CMODE REL

if DTOS CMODE DSOS then jump (IP+REL)

    FOR
    WHILE

    IO_IN = "key"
    IO_OUT_STR = ".\""
    IO_OUT_INT = "."
    IO_OUT_CHAR = "emit"
    IO_OUT_CR = "cr"
