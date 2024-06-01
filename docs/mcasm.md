## Ассемблер микрокода

Для удобства написания [микрокода процессора](src/machine/mc/code/main.mcasm)
был разработан язык ассемблера, его парсер и ассемблер.

Примеров кода не будет, проще смотреть сразу микрокод процессора.

Для упрощения задачи используется парсер Lark,
грамматика языка в его формате доступна в [файле](src/mcasm/uasm.lark).

Каждая строка микроассемблера транслируется в одну микрокоманду.

Для работы с АЛУ формат следующий:

`(BUS_A(A_CTRL,...) CTRL BUS_B(B_CTRL,...)) -> BUS_C`

где BUS_A, BUS_B - источники данных для шин А И В, BUS_C - куда записать из шины C,
CTRL - определяет операцию АЛУ, A_CTRL и B_CTRL - операции входов АЛУ.

Для управления стеками предусмотрены команды
`push(x), pop(x), poprep(x), rep(x)` где `x` это буква стека R или D.

Для записи в память есть команда `store`.

Для управления контроллером IO команды `io(x)` где x - операция для КВУ.

Есть метки строк, их можно использовать при выполнении команд `jump`.

Микрокоманда jump описывается следующим образом:

`if <ALU>[<BIT>] == <VAL> jmp <LABEL>`

где ALU это блок управления АЛУ как выше, но без записи,
BIT и VAL - условия сравнения, LABEL - метка для перехода

Присутствуют макросы для структур `if` и `switch`.
`switch` разворачивается во вложенные `if`, а `if` в два блока кода и условный переход.
`switch` позволяет проверить не один бит, а сразу диапазон бит,
и перейти в нужную ветку уже по выбранному числовому, а не битовому значению.

### CLI микроассемблера

```shell
$ ./src/mcasm/mccompile.py --help
usage: mccompile.py [-h] [-p] [-b] [-j JSON] input_file

Microcode ASM parser & compiler

positional arguments:
  input_file            ASM file path

options:
  -h, --help            show this help message and exit
  -p, --parse           Only parse and print source microcommands as Python objects
  -b, --bin             Compile print binary encoded instructions
  -j JSON, --json JSON  Compile and output binary to file
```