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
этот журнал по завершении выводится в текстовом формате markdown а также в формате VCD с таймингами.

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

```forth
: cat begin
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

Вывод симулятора

```

```

Выходные данные

```shell
$ cat cat.out
Hello
```

<details>
<summary>Листинг журналов</summary>


Журнал исполнения потактово (фрагмент)

```

```

Журнал исполнения по инструкциям

```

```

</details>

### Задача hello

[Golden-test](test/golden/golden_def/hello.yml)

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



