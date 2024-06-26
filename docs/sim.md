## Симулятор

Симулятор используется из поставки MyHDL,
он работает потактово имитируя работу тактового генератора,
и вычисляя комбинационные и последовательные схемы исходя в моменты изменения тактового сигнала.
Для этого все модули оформлены в виде либо комбинационных схем (`@always_comb`)
значения которых вычисляются при любых изменениях входных сигналов,
либо последовательных блоков (`@always(clk)`), которые запускаются по фротам синхросигналов.

Для получения отчетов о состоянии процессора на фронте и спаде тактового сигнала
с выбранных элементов процессора снимаются значения через обращения к ним
по древовидной структуре модулей и записываются в журнал,
этот журнал по завершении выводится в текстовом формате markdown а также в формате VCD с таймингами в директорию `dist`.

### Тестирование

В решении представлено 2 вида тестирования:

- unit-тестирование отдельных модулей и CPU в сборе (`test/test_*.py`)
- интеграционного тестирования с golden-тестами для CPU и транслятора языка,
  а также подсистемы ввода-вывода (`test/golden/golden_def`)
    - для тестирования используется сборка процессора
      с контролируемыми внешними устройствами и средствами трассировки `test/golden/testbench.py`

Запуск тестирования

```shell
$ poetry run pytest
```

### Задача cat (подробно)

[Golden-test](test/golden/golden_def/cat.yml)

В бесконечном цикле читаем символ, выводим его.

```forth
: cat 
  begin
    key emit
    true 
  until ;

cat
```

Компиляция:

Запустим компилятор с флагом `--verbose`, чтобы получить не только бинарный файл,
но и текстовое описание декодированных инструкций в нем.

Здесь видно, что была определена функция, и есть ее вызов в точке входа по адресу 0.
Также видна реализация бесконечного цикла через вызов условного перехода при постоянном значении 1.

```shell
$ ./src/compiler/main.py --verbose test/golden/golden_def/cat.fth cat.bin                                                                                                                                                         ─╯
        LoC: 6
        Compiled binary size: 32 bytes
        Compiled instructions: 8 count, 32 bytes 
        
--------------------
MEMORY IMAGE
000h: <RCALL>(I|0)
001h: <ISTKPSH>(I|33)
002h: <IN>
003h: <ISTKPSH>(I|17)
004h: <OUT>
005h: <ISTKPSH>(I|1)
006h: <CJMP>(I|-6)
007h: <RET>
--------------------
STATIC VARIABLES

--------------------
BINARY
000h: 40300000h
001h: 20000021h
002h: 00200000h
003h: 20000011h
004h: 00300000h
005h: 20000001h
006h: 4020fffah
007h: 40400000h
```

Подготовим симуляцию.

Входные данные

```shell
$ cat cat.in
Hello
```

Запустим симуляцию

```shell
$ ./test/golden/cli.py cat.bin -i cat.in -o cat.out -t dist -g
```

По завешении получим в директории `dist` отчеты по симуляции (в markdown формате)
с точностью до инструкции и до такта,
а также их представления в виде VCD файлов, а так как указан ключ `-g`,
то VCD файлы будут открыты в gtkwave, если он присутствует на системе.

Выходные данные

```shell
$ cat cat.out
Hello
```

<details>

<summary>Листинг логов симулятора</summary>

```
3226ms [INFO] (dev_keyboard) READ DEV 20 REG 01 762 0
3226ms [INFO] (io_controller) IOCTRL READ FROM 0021 is 00000048
3249ms [INFO] (dev_printer) at 1302 WRITE DEV 10 REG 01 VAL 00000048
3300ms [INFO] (dev_keyboard) READ DEV 20 REG 01 2622 762
3301ms [INFO] (io_controller) IOCTRL READ FROM 0021 is 00000065
3327ms [INFO] (dev_printer) at 3162 WRITE DEV 10 REG 01 VAL 00000065
3426ms [INFO] (dev_keyboard) READ DEV 20 REG 01 4782 2622
3426ms [INFO] (io_controller) IOCTRL READ FROM 0021 is 0000006c
3450ms [INFO] (dev_printer) at 5322 WRITE DEV 10 REG 01 VAL 0000006c
3510ms [INFO] (dev_keyboard) READ DEV 20 REG 01 6642 4782
3511ms [INFO] (io_controller) IOCTRL READ FROM 0021 is 0000006c
3536ms [INFO] (dev_printer) at 7182 WRITE DEV 10 REG 01 VAL 0000006c
3641ms [INFO] (dev_keyboard) READ DEV 20 REG 01 8802 6642
3642ms [INFO] (io_controller) IOCTRL READ FROM 0021 is 0000006f
3678ms [INFO] (dev_printer) at 9342 WRITE DEV 10 REG 01 VAL 0000006f
4314ms [INFO] (cli) Instructions executed 37
4314ms [INFO] (cli) Ticks executed 499
```

</details>

<details>
<summary>Листинг журналов трассировки</summary>


Журнал исполнения потактово (фрагмент) (`dist/trace_tick.md`)

| TIME | CLK | A        | B        | C        | IP       | CR       | AR       | PS       | DRR      | DRW      | DS_SP | DS_TOP   | DS_PRV   | RS_SP | RS_TOP   | RS_PRV   | IO_RD    |
|------|-----|----------|----------|----------|----------|----------|----------|----------|----------|----------|-------|----------|----------|-------|----------|----------|----------|
| 12   | 1   | 00000000 | 00000000 | 00000000 | 00000000 | 00000000 | 00000000 | 00000000 | 40300000 | 00000000 | 00    | 00000000 | 00000000 | 00    | 00000000 | 00000000 | 00000000 |
| 22   | 0   | 00000000 | 00000000 | 00000000 | 00000000 | 00000000 | 00000000 | 00000000 | 40300000 | 00000000 | 00    | 00000000 | 00000000 | 00    | 00000000 | 00000000 | 00000000 |
| 32   | 1   | 40300000 | 00000000 | 40300000 | 00000000 | 00000000 | 00000000 | 00000000 | 40300000 | 00000000 | 00    | 00000000 | 00000000 | 00    | 00000000 | 00000000 | 00000000 |
| 42   | 0   | 40300000 | 00000000 | 40300000 | 00000000 | 40300000 | 00000000 | 00000000 | 40300000 | 00000000 | 00    | 00000000 | 00000000 | 00    | 00000000 | 00000000 | 00000000 |
| 52   | 1   | 00000000 | 00000000 | 00000001 | 00000000 | 40300000 | 00000000 | 00000000 | 40300000 | 00000000 | 00    | 00000000 | 00000000 | 00    | 00000000 | 00000000 | 00000000 |
| 62   | 0   | 00000001 | 00000000 | 00000001 | 00000001 | 40300000 | 00000000 | 00000000 | 40300000 | 00000000 | 00    | 00000000 | 00000000 | 00    | 00000000 | 00000000 | 00000000 |
| 72   | 1   | 40300000 | 00000000 | 40300000 | 00000001 | 40300000 | 00000000 | 00000000 | 40300000 | 00000000 | 00    | 00000000 | 00000000 | 00    | 00000000 | 00000000 | 00000000 |
| 82   | 0   | 40300000 | 00000000 | 40300000 | 00000001 | 40300000 | 00000000 | 00000000 | 40300000 | 00000000 | 00    | 00000000 | 00000000 | 00    | 00000000 | 00000000 | 00000000 |
| 92   | 1   | 40300000 | 00000000 | 40300000 | 00000001 | 40300000 | 00000000 | 00000000 | 40300000 | 00000000 | 00    | 00000000 | 00000000 | 00    | 00000000 | 00000000 | 00000000 |
| 102  | 0   | 40300000 | 00000000 | 40300000 | 00000001 | 40300000 | 00000000 | 00000000 | 40300000 | 00000000 | 00    | 00000000 | 00000000 | 00    | 00000000 | 00000000 | 00000000 |

Журнал исполнения по инструкциям (`dist/trace_instr.md`)

| TIME | A        | B        | C        | IP       | CR       | AR       | PS       | DRR      | DRW      | DS_SP | DS_TOP   | DS_PRV   | RS_SP | RS_TOP   | RS_PRV   | IO_RD    |
|------|----------|----------|----------|----------|----------|----------|----------|----------|----------|-------|----------|----------|-------|----------|----------|----------|
| 282  | 00000000 | 00000000 | 00000000 | 00000001 | 40300000 | 00000000 | 00000000 | 40300000 | 00000000 | 00    | 00000000 | 00000000 | 01    | 00000001 | 00000000 | 00000000 |
| 542  | 00000000 | 00000000 | 00000000 | 00000002 | 20000021 | 00000001 | 00000000 | 20000021 | 00000000 | 01    | 00000021 | 00000000 | 01    | 00000001 | 00000000 | 00000000 |
| 802  | 00000000 | 00000000 | 00000000 | 00000003 | 00200000 | 00000002 | 00000000 | 00200000 | 00000000 | 01    | 00000048 | 00000000 | 01    | 00000001 | 00000000 | 00000048 |
| 1062 | 00000000 | 00000000 | 00000000 | 00000004 | 20000011 | 00000003 | 00000000 | 20000011 | 00000000 | 02    | 00000011 | 00000048 | 01    | 00000001 | 00000000 | 00000048 |
| 1342 | 00000000 | 00000000 | 00000000 | 00000005 | 00300000 | 00000004 | 00000000 | 00300000 | 00000000 | 00    | 00000000 | 00000000 | 01    | 00000001 | 00000000 | 00000048 |
| 1602 | 00000000 | 00000000 | 00000000 | 00000006 | 20000001 | 00000005 | 00000000 | 20000001 | 00000000 | 01    | 00000001 | 00000000 | 01    | 00000001 | 00000000 | 00000048 |
| 1882 | 00000000 | 00000000 | 00000000 | 00000007 | 4020fffa | 00000006 | 00000000 | 4020fffa | 00000000 | 00    | 00000000 | 00000000 | 01    | 00000001 | 00000000 | 00000048 |
| 2142 | 00000000 | 00000000 | 00000000 | 00000001 | 40400000 | 00000007 | 00000000 | 40400000 | 00000000 | 00    | 00000000 | 00000000 | 00    | 00000000 | 00000000 | 00000048 |
| 2402 | 00000000 | 00000000 | 00000000 | 00000002 | 20000021 | 00000001 | 00000000 | 20000021 | 00000000 | 01    | 00000021 | 00000000 | 00    | 00000000 | 00000000 | 00000048 |
| 2662 | 00000000 | 00000000 | 00000000 | 00000003 | 00200000 | 00000002 | 00000000 | 00200000 | 00000000 | 01    | 00000065 | 00000000 | 00    | 00000000 | 00000000 | 00000065 |
| 2922 | 00000000 | 00000000 | 00000000 | 00000004 | 20000011 | 00000003 | 00000000 | 20000011 | 00000000 | 02    | 00000011 | 00000065 | 00    | 00000000 | 00000000 | 00000065 |
| 3202 | 00000000 | 00000000 | 00000000 | 00000005 | 00300000 | 00000004 | 00000000 | 00300000 | 00000000 | 00    | 00000000 | 00000000 | 00    | 00000000 | 00000000 | 00000065 |
| 3462 | 00000000 | 00000000 | 00000000 | 00000006 | 20000001 | 00000005 | 00000000 | 20000001 | 00000000 | 01    | 00000001 | 00000000 | 00    | 00000000 | 00000000 | 00000065 |
| 3742 | 00000000 | 00000000 | 00000000 | 00000007 | 4020fffa | 00000006 | 00000000 | 4020fffa | 00000000 | 00    | 00000000 | 00000000 | 00    | 00000000 | 00000000 | 00000065 |
| 4002 | 00000000 | 00000000 | 00000000 | 00000000 | 40400000 | 00000007 | 00000000 | 40400000 | 00000000 | 00    | 00000000 | 00000000 | 00    | 00000000 | 00000000 | 00000065 |
| 4302 | 00000000 | 00000000 | 00000000 | 00000001 | 40300000 | 00000000 | 00000000 | 40300000 | 00000000 | 00    | 00000000 | 00000000 | 01    | 00000001 | 00000000 | 00000065 |
| 4562 | 00000000 | 00000000 | 00000000 | 00000002 | 20000021 | 00000001 | 00000000 | 20000021 | 00000000 | 01    | 00000021 | 00000000 | 01    | 00000001 | 00000000 | 00000065 |
| 4822 | 00000000 | 00000000 | 00000000 | 00000003 | 00200000 | 00000002 | 00000000 | 00200000 | 00000000 | 01    | 0000006c | 00000000 | 01    | 00000001 | 00000000 | 0000006c |
| 5082 | 00000000 | 00000000 | 00000000 | 00000004 | 20000011 | 00000003 | 00000000 | 20000011 | 00000000 | 02    | 00000011 | 0000006c | 01    | 00000001 | 00000000 | 0000006c |
| 5362 | 00000000 | 00000000 | 00000000 | 00000005 | 00300000 | 00000004 | 00000000 | 00300000 | 00000000 | 00    | 00000000 | 00000000 | 01    | 00000001 | 00000000 | 0000006c |
| 5622 | 00000000 | 00000000 | 00000000 | 00000006 | 20000001 | 00000005 | 00000000 | 20000001 | 00000000 | 01    | 00000001 | 00000000 | 01    | 00000001 | 00000000 | 0000006c |
| 5902 | 00000000 | 00000000 | 00000000 | 00000007 | 4020fffa | 00000006 | 00000000 | 4020fffa | 00000000 | 00    | 00000000 | 00000000 | 01    | 00000001 | 00000000 | 0000006c |
| 6162 | 00000000 | 00000000 | 00000000 | 00000001 | 40400000 | 00000007 | 00000000 | 40400000 | 00000000 | 00    | 00000000 | 00000000 | 00    | 00000000 | 00000000 | 0000006c |
| 6422 | 00000000 | 00000000 | 00000000 | 00000002 | 20000021 | 00000001 | 00000000 | 20000021 | 00000000 | 01    | 00000021 | 00000000 | 00    | 00000000 | 00000000 | 0000006c |
| 6682 | 00000000 | 00000000 | 00000000 | 00000003 | 00200000 | 00000002 | 00000000 | 00200000 | 00000000 | 01    | 0000006c | 00000000 | 00    | 00000000 | 00000000 | 0000006c |
| 6942 | 00000000 | 00000000 | 00000000 | 00000004 | 20000011 | 00000003 | 00000000 | 20000011 | 00000000 | 02    | 00000011 | 0000006c | 00    | 00000000 | 00000000 | 0000006c |
| 7222 | 00000000 | 00000000 | 00000000 | 00000005 | 00300000 | 00000004 | 00000000 | 00300000 | 00000000 | 00    | 00000000 | 00000000 | 00    | 00000000 | 00000000 | 0000006c |
| 7482 | 00000000 | 00000000 | 00000000 | 00000006 | 20000001 | 00000005 | 00000000 | 20000001 | 00000000 | 01    | 00000001 | 00000000 | 00    | 00000000 | 00000000 | 0000006c |
| 7762 | 00000000 | 00000000 | 00000000 | 00000007 | 4020fffa | 00000006 | 00000000 | 4020fffa | 00000000 | 00    | 00000000 | 00000000 | 00    | 00000000 | 00000000 | 0000006c |
| 8022 | 00000000 | 00000000 | 00000000 | 00000000 | 40400000 | 00000007 | 00000000 | 40400000 | 00000000 | 00    | 00000000 | 00000000 | 00    | 00000000 | 00000000 | 0000006c |
| 8322 | 00000000 | 00000000 | 00000000 | 00000001 | 40300000 | 00000000 | 00000000 | 40300000 | 00000000 | 00    | 00000000 | 00000000 | 01    | 00000001 | 00000000 | 0000006c |
| 8582 | 00000000 | 00000000 | 00000000 | 00000002 | 20000021 | 00000001 | 00000000 | 20000021 | 00000000 | 01    | 00000021 | 00000000 | 01    | 00000001 | 00000000 | 0000006c |
| 8842 | 00000000 | 00000000 | 00000000 | 00000003 | 00200000 | 00000002 | 00000000 | 00200000 | 00000000 | 01    | 0000006f | 00000000 | 01    | 00000001 | 00000000 | 0000006f |
| 9102 | 00000000 | 00000000 | 00000000 | 00000004 | 20000011 | 00000003 | 00000000 | 20000011 | 00000000 | 02    | 00000011 | 0000006f | 01    | 00000001 | 00000000 | 0000006f |
| 9382 | 00000000 | 00000000 | 00000000 | 00000005 | 00300000 | 00000004 | 00000000 | 00300000 | 00000000 | 00    | 00000000 | 00000000 | 01    | 00000001 | 00000000 | 0000006f |
| 9642 | 00000000 | 00000000 | 00000000 | 00000006 | 20000001 | 00000005 | 00000000 | 20000001 | 00000000 | 01    | 00000001 | 00000000 | 01    | 00000001 | 00000000 | 0000006f |
| 9922 | 00000000 | 00000000 | 00000000 | 00000007 | 4020fffa | 00000006 | 00000000 | 4020fffa | 00000000 | 00    | 00000000 | 00000000 | 01    | 00000001 | 00000000 | 0000006f |

</details>


<details>

<summary>GTKWave</summary>

Полная трассировка (`dist/machine_testbench0.vcd`)

![](docs/media/gtkw_full.png)

Краткая трассировка уровня тактов (`dist/tick_trace.vcd`)

![](docs/media/gtkw_tick.png)

Краткая трассировка уровня инструкций (`dist/instr_trace.vcd`)

![](docs/media/gtkw_instr.png)

</details>

### Задача hello

[Golden-test](test/golden/golden_def/hello.yml)

Определяем строку в статической памяти,
получаем адрес строки, затем вызываем библиотечную функцию печати строки,
для нее документация представлена в [файле](src/compiler/forthlib/iolib.fth) библиотеки.

<details>
<summary>Листинг</summary>

```forth
\import src/compiler/forthlib/iolib.fth

: str_helloworld s" Hello World!" ;
str_helloworld type

halt
```

</details>

### Задача hello_user_name

[Golden-test](test/golden/golden_def/hello_user_name.yml)

Определяем функции для вывода вспомогательных символов,
резервируем в статической памяти буфер под строку,
затем выводим приглашение, читаем строку в буфер,
потом выводим последовательно текст и эту строку.

<details>
<summary>Листинг</summary>

```forth
\import src/compiler/forthlib/iolib.fth

: prompt-out ." > " ;
: prompt-in ." < " cr ;
: print-prompt ( -- )
prompt-out ." What is your name?" cr ;

: print-hello-to ( addr -- )           \ prints "Hello, {str}", where str is pointed by addr
prompt-out ." Hello, " type cr ;

variable name 256 cells allot 

print-prompt 
prompt-in 
name read
name print-hello-to
halt
```

</details>

### Задача prob1

[Golden-test](test/golden/golden_def/prob1.yml)

Сначала в переменную `sum` функцией `add-all-dividing` суммируем все числа,
делящиеся на 3, потом на 5, затем вычитаем те, что были посчитаны дважды,
то есть те что делятся на 5.
Вместо проверки делимости просто перебираем числа с фиксированным шагом.

<details>
<summary>Листинг</summary>

```forth
1001 constant upper-bound
variable sum

: add-all-dividing ( delta -- )   \ add all numbers from delta to 1001 to variable sum, 
                                \ increasing current by delta (i.e. for 5: 5 10 15 ... 1000)
dup             \ store as [delta, current]
begin 
  dup upper-bound <    \ while current < 1000 
while 
  dup sum +!    \ sum += current
  over +        \ current += delta
repeat
;

: sub-all-dividing ( delta -- )   \ same as add-all-dividing, but decreases sum var
dup           
begin 
  dup upper-bound <    
while 
  dup negate sum +!             \ sum -= current
  over +        
repeat
;

3 add-all-dividing 
5 add-all-dividing
15 sub-all-dividing

sum @ .

halt
```

</details>

#### Дополнительные тесты

- math.yml - проверка математических операций
- comp.yml - проверка операторов сравнения
- stack.yml - проверка функций преобразования d-стека
- if.yml - проверка условных операторов и их вложенности
- varconst.yml - проверка создание переменных и констант
- arr.yml - проверка создания, чтения и записи в статические массивы
- dowhile.yml - проверка цикла формата do-while
- while.yml - проверка цикла формата while
- for.yml - проверка цикла формата for
- func.yml - проверка создания и вызова функций, включая функции из функций
- io.yml - проверка базового ввода-вывода

### CLI Симулятора

```shell
$ ./test/golden/cli.py --help
usage: cli.py [-h] [-i STDIN] [-o STDOUT] [-t TRACE] [-g] ram_file

CLI machine integration test runner

positional arguments:
  ram_file              RAM image binary file

options:
  -h, --help            show this help message and exit
  -i STDIN, --stdin STDIN
                        Input text source file
  -o STDOUT, --stdout STDOUT
                        File to which to store model output
  -t TRACE, --trace TRACE
                        Directory path where would be placed instruction- and tick-level traces and VCD files
  -g, --gtkwave         Launch gtkwave with traces

```



