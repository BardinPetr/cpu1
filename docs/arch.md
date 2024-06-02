## Обзор архитектуры

### Исполнение микрокода

Микрокоманды исполняются последовательно из ПЗУ микрокода,
в зависимости от бита типа может присутствовать условный переход. Исполнение начинается с нулевого адреса.

Размер микрокоманды всегда 64 бит, но реально используется меньше:

- exec: _42 бит_
- jump: _44 бит_

Формат команд горизонтально-вертикальный, есть поддержка
групп сигналов с множественной активацией (кодируются 1 по биту на сигнал) и
с единичной активацией (кодируются по номеру для уменьшения объема).

Устройство управления по переднему фронту тактового импульса загружает последовательно микрокоманды из ПЗУ,
по заднему фронту происходит либо инкремент MC_PC,
либо для микрокоманд ветвления сравнение шины C с условием перехода и изменение MC_PC.


Типы микрокоманд по представляемым возможностям:
- exec
    1. чтение регистров или памяти в шины А, В
    2. выполнение операции АЛУ, установка значения в шине C
    3. управление стеком
    4. запись в регистры, память или верх стека
    5. управление IO
- jump
    1. выполнение операции на АЛУ с возможностью чтения регистров и памяти, выдача данных на шину C (как пункты 1 и 2 exec)
    2. выполнение условного перехода в микрокоде
        - проверка сравнением одного выбранного бита шины C после АЛУ с булевым значением в команде
        - переход по абсолютному адресу

Микрокод процессора расположен в [файле](src/machine/mc/code/main.mcasm).

<details>

<summary>Листинг микрокода</summary>

```
start:

# fetch instruction from RAM to CR, increase IP
infetch:
(IP ADD) -> AR;
(DR ADD) -> CR;
(IP(INC) ADD) -> IP;

# execute command according to opcode of CR[31:20]
exec:

# group select of CR[31:28]
switch (CR ADD)[30:28] {

  #GIOC
  case 0b000 {
    if (CR ADD)[21] == 0 {
      if (CR ADD)[20] == 1 jmp end; # 0b01 NOP
      # 0b00 HLT
      ctrl(halt);
    } else {
      # IO instructions
      (DST(TKW) ADD) io(set_addr), pop(D);
      if (CR ADD)[20] == 0 {
        # 0b10 IN  [addr] -> [val]
        io(req_read);
        (IOR ADD) io(get_data), push(D);
      } else {
        # 0b11 OUT [val, addr] -> []
        (DST ADD) io(set_data), pop(D);
        io(req_write);
      };
    };
  }

  # GMTH
  case 0b001 {
    switch (CR ADD)[23:20] {
      # ADD
      case 0b0000 { (DSS ADD DST) poprep(D); }
      # SUB
      case 0b0001 { (DSS ADD DST(INC,NOT)) poprep(D); }
      # DIV
      case 0b0010 { (DSS DIV DST) poprep(D); }
      # MUL
      case 0b0011 { (DSS MUL DST) poprep(D); }
      # MOD
      case 0b0100 { (DSS MOD DST) poprep(D); }
      # AND
      case 0b0101 { (DSS AND DST) poprep(D); }
      # OR
      case 0b0110 { (DSS OR DST) poprep(D); }
      # INV (~x)
      case 0b0111 { (DST(NOT) ADD) rep(D); }
      # INC
      case 0b1000 { (DST(INC) ADD) rep(D); }
      # DEC
      case 0b1001 { (DST ADD Z(NOT)) rep(D); }
      # NEG (-x)
      case 0b1010 { (DST(NOT,INC) ADD) rep(D); }
    };
  }

  # GSTK
  case 0b010 {
    # (CR ADD)[16] is stack id (0=D, 1=R),
    # meaning is stack to operate on, or source stack for two-stack operation

    switch (CR ADD)[22:20] {
      # ISTKPSH
      case 0b0000 {
        if (CR ADD)[16] == 0  { (CR(TKW,SXTW) ADD) push(D); }
        else                  { (CR(TKW,SXTW) ADD) push(R); };
      }

      # STKMV src[a];dst[] -> src[];dst[a]   (ctrl/stackid is src)
      case 0b0001 {
        if (CR ADD)[16] == 0  { (DST ADD) push(R), pop(D); }
        else                  { (RST ADD) push(D), pop(R); };
      }

      # STKCP src[a];dst[] -> src[a];dst[a]   (ctrl/stackid is src)
      case 0b0010 {
        if (CR ADD)[16] == 0  { (DST ADD) push(R); }
        else                  { (RST ADD) push(D); };
      }

      # STKPOP [a] -> []
      case 0b0011 {
        if (CR ADD)[16] == 0  { (ZERO) pop(D); }
        else                  { (ZERO) pop(R); };
      }

      # STKDUP [a] -> [a, a]
      case 0b0101 {
        if (CR ADD)[16] == 0  { (DST ADD) push(D); }
        else                  { (RST ADD) push(R); };
      }

      # STKOVR [a,b] -> [a,b,a]
      case 0b0100 {
        if (CR ADD)[16] == 0  { (DSS ADD) push(D); }
        else                  { (RSS ADD) push(R); };
      }

      # STKSWP [a,b] -> [b,a]
      case 0b0110 {
        if (CR ADD)[16] == 0  {
          (DSS ADD) push(R);
          (DST ADD) poprep(D);
          (RST ADD) push(D), pop(R);
        } else {
          (RSS ADD) push(D);
          (RST ADD) poprep(R);
          (DST ADD) push(R), pop(D);
        };
      }
    };
  }

  # GCMP
  # PS is [...VCNZ]
  case 0b011 {
    # bit 20 selects operand order (0 for LTx, 1 for GTx, then GTx is LTx with reversed ops)
    if (CR ADD)[20] == 0  { (DSS ADD DST(NOT,INC)) set(Z,V,C,N); }
    else                  { (DST ADD DSS(NOT,INC)) set(Z,V,C,N); };

    if (CR ADD)[22] == 1 {
      # CEQ (b100)
      (PS AND Z(INC)) poprep(D); # push z flag, it is leftmost
    } else {
      # CLTx, CGTx (b0XX)
      # here implementing only "less" variant

      if (CR ADD)[21] == 0 {
        # Unsigned version
        # C <=> "<"
        if (PS ADD)[2] == 0 { jmp cmp_ltx_exit_poprep_1; }
        else                { jmp cmp_ltx_exit_poprep_0; };
      } else {
        # Signed version
        # V^C <=> "<"
        switch (PS ADD)[4:2] { # extract VC part and implement xor
          case 0b00 { jmp cmp_ltx_exit_poprep_0; }
          case 0b11 { jmp cmp_ltx_exit_poprep_0; }
          case 0b01 { jmp cmp_ltx_exit_poprep_1; }
          case 0b10 { jmp cmp_ltx_exit_poprep_1; }
        };
      };

      # here using jmp to push 0/1 to exit from all nested ifs
      # with only one command instead of sequence to speedup,
      # as there is no optimization currently in flattening process
      cmp_ltx_exit_poprep_0:
      (Z ADD) poprep(D);
      jmp exec_end;

      cmp_ltx_exit_poprep_1:
      (Z(INC) ADD) poprep(D);
    };
  }

  # GJMP
  case 0b100 {
    switch (CR ADD)[22:20] {
      # AJMP
      case 0b000 {
        (DST ADD) -> IP, pop(D);
      }

      # RJMP
      case 0b001 {
        (CR(TKW,SXTW) ADD IP) -> IP;
      }

      # CJMP jump IP-relative if DST==0
      case 0b010 {
        if (DST ADD)[0] == 1 jmp cjmp_end;
        (CR(TKW,SXTW) ADD IP) -> IP;
        cjmp_end:
        pop(D);
      }

      # RCALL
      case 0b011 {
        (IP ADD) push(R);
        (CR(TKW,SXTW) ADD IP) -> IP;
      }

      # RET
      case 0b100 {
        (RST ADD) -> IP, pop(R);
      }
    };
  }

  # GMEM
  case 0b101 {
    switch (CR ADD)[20:20] {
      # FETCH [addr] -> [val]
      case 0b0 {
        (DST(TKW) ADD) -> AR;
        (DR ADD) rep(D);
      }

      # STORE [val,addr] -> []
      case 0b1 {
        (DST(TKW) ADD) -> AR, pop(D);
        (DST ADD) -> DR, pop(D);
        store;
      }
    };
  }
};

exec_end:

# final
end:
jmp start;

```


</details>

Принцип работы микрокода:

- загрузка инструкции по IP в CR
- инкремент IP
- последовательные проверки битов CR для определения команды по opcode
- исполнение микрокода команды
- переход в начало

### Control unit

[Код модуля](src/machine/mc/components/control.py).

Состоит из 2х основных частей:

- MCSequencer
    - по переднему фронту тактирования загружает микрокоманды из памяти в `control_bus`
    - по заднему фронту тактирования меняет счетчик микрокоманд и делает переходы
    - генерация тактирования для datapath (на чтение и на запись)
- набор декодеров (ALUDecoder, RegReadDecoder, RegWriteDecoder, StackDecoder)
    - выделение из `control_bus` сигналов на отдельные компоненты расписанные далее в соответствии с фронтом импульса и
      последовательностью управления

Основные сигналы управления:

| сигналы                                      | описание                          |
|----------------------------------------------|-----------------------------------|
| alu_ctrl                                     | оператор АЛУ                      |
| alu_ctrl_pa, alu_ctrl_pb                     | функции на входе в АЛУ            |
| alu_flag_ctrl, reg_ps_wr                     | установка флагов АЛУ, запись в PS |
| mux_bus_a_reg_in_ctrl, mux_bus_b_reg_in_ctrl | выбор источника для шин А и В     |
| r_stack_shift, r_stack_wr                    | сдвиги запись стека R             |
| d_stack_shift, d_stack_wr                    | сдвиги запись стека D             |
| demux_bus_c_reg_id                           | выбор получателя данных с шины C  |
| ram_a_wr                                     | выполнение записи в память        |

### Datapath

[Код модуля](src/machine/datapath/datapath.py).

Основой процессора является АЛУ, которое подключено к системным шинам A, B - входным, и С - выходной.

При выполнении микрокоманды первый этап - по переднему фронту загрузка операндов в шины A, B,
для этого в соответствии с `mux_bus_*_reg_in_ctrl` ([BusInCtrl](src/machine/arch.py)) мультиплексируются в шины A и B
выходы регистров, значений со стека (по 2 верхних значения каждого стека выдаются всегда из модуля стека),
и из памяти (по переднему фронту в выходном регистре данных памяти всегда данные по адресу AR).

По заднему фронту защелкиваются защелки на входных шинах перед АЛУ,
его операция определяется `alu_ctrl` ([ALUCtrl](src/machine/arch.py)), при этом перед вычислением основной функции
над каждым операндом можно провести предварительно набор операций `alu_ctrl_p*` ([ALUPortCtrl](src/machine/arch.py)).

Далее все по заднему фронту синхроимпульса записи, значение с шины С нужно демультиплексором
по `demux_bus_c_reg_id` ([BusOutCtrl](src/machine/arch.py)) передать
либо на входы регистров, либо на модули стеков, либо в КВУ.
Установка `demux_bus_c_reg_wr` позволяет выполнить запись в регистры,
`ram_a_wr` - в память (если в AR уже установлен адрес в прошлых команде и
в этой команде выход шины С выбран на регистр данных модуля памяти).
Сигналы `*_stack_wr` и `*_stack_shift` напрямую передаются модулям стека, о нем в следующем разделе.
АЛУ также выдает флаги, которые при установке `alu_flag_ctrl` и `reg_ps_wr` записываются в PS.

Основные сигналы данных:

| сигналы                 | описание                                                                      |
|-------------------------|-------------------------------------------------------------------------------|
| bus_*                   | шины A, B, C                                                                  |
| alu_*_in                | входы с шин A, B с регистра перед АЛУ                                         |
| reg_\<name>_*           | сигналы входа, выхода и записи в регистр                                      |
| reg_drw_*, ram_drr      | входной и выходной регистр данных памяти                                      |
| \<name>_stack_tos\<pos> | выходы со стека \<name> верхнего (pos=0) или второго с верху (pos=1) значения |
| \<name>_stack_in        | вход данных в модуль стека \<name>                                            |
| io_ctrl_data_output     | выходной регистр данных КВУ                                                   |

### Функционирование модуля памяти

[Код модуля](src/machine/components/RAM.py).

По переднему фронту модуль выставляет на шину данных значение из памяти по адресу на шине адреса.

По заднему фронту модуль записывает в память значение
с шины данных по адресу на шине адреса при установке разрешающего сигнала.

### Функционирование модуля стека

[Код модуля](src/machine/components/ExtendedStack.py).

Выводы tos0, tos1 отображают 2 значения от вершины стека из регистрового файла при изменении указателя стека,
выводы full и empty соответственно показывают факт заполнения стека до максимума и его пустоту.

Сдвиг происходит при установке значения `in_shift` допускающего сдвиги +1, -1 и 0.
Запись в регистры проходит только в верх стек после сдвигов по заднему фронту при установленном `wr_top`.

### Схемы

Схемы сделаны при помощи ПО Logisim Evolution, проект прилагается.

Все логические компоненты напрямую отражаются в идентичные в коде модели.
На схемах представлены только основные модули системы,
в частности, не присутствуют те, в которых для симуляции есть несинтезируемые операции из Python.
Сигналы на схемах заименованы в соответствии с моделью.

<details>

<summary>Схемы</summary>

#### Control unit

Загрузка микрокоманд и переходы

![ctrl_instr.png](media/Fctrl_instr.png)

Предварительное декодирование микрокоманды

![ctrl_in.png](docs/media/ctrl_in.png)

Декодеры управления стеком

![ctrl_stack.png](docs/media/ctrl_stack.png)

Декодеры управления памятью и регистрами

![ctrl_reg.png](docs/media/ctrl_reg.png)

#### Datapath

Основной вычислительный модуль, обвязка АЛУ

![dp_alu.png](docs/media/dp_alu.png)

Входной мультиплексор АЛУ (две симметричные схемы, в именах Х соответствует шине А или В)

![dp_mux.png](docs/media/dp_mux.png)

Базовые регистры и управление флагами PS

![dp_reg.png](docs/media/dp_reg.png)

Модуль памяти, его регистровая обвязка и модуль контроллера IO

![dp_mem.png](docs/media/dp_mem.png)

Модули стека

![dp_stack.png](docs/media/dp_stack.png)


</details>


