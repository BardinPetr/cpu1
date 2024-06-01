
### Описания управляющих сигналов микрокоманды

<details>

<summary>Листинг</summary>

#### Типы полей:

```python
class BusInCtrl(CEnumS):
    """
    Format:
    0xxx - xx is classic source
    1xxx - xx is regfile ID
    """
    Z = 0  # ноль
    PS = 0b0001  # регистр PS
    DR = 0b0010  # регистр вывода данных из памяти
    IOR = 0b0011  # регистр вывода данных из IO контроллера
    DST = 0b0100  # значение вершины стека D
    DSS = 0b0101  # значение под вершиной стека D
    RST = 0b0110  # значение вершины стека R
    RSS = 0b0111  # значение под вершиной стека R
    IP = 0b1000 + RegFileIdCtrl.IP  # регистр IP
    CR = 0b1000 + RegFileIdCtrl.CR  # регистр CR
```

```python
class BusOutCtrl(CEnumS):
    """
    Format:
    00xx - xx is classic source
    10xx - xx is regfile ID
    """
    Z = 0b0000  # нет записи
    PS = 0b0001  # запись в PS
    DR = 0b0010  # запись во входной регистр данных памяти
    AR = 0b0011  # запись в AR
    DS = 0b0100  # передача входного значения в контроллер стека D
    RS = 0b0101  # передача входного значения в контроллер стека R
    IP = 0b1000 + RegFileIdCtrl.IP  # запись в IP
    CR = 0b1000 + RegFileIdCtrl.CR  # запись в CR
```

```python
class MemCtrl(CEnumS):
    IGN = 0  # нет записи
    WR = 1  # запись в память
```

```python
class ALUCtrl(CEnumS):
    """
    Операции АЛУ
    """
    ZERO = 0
    PASSA = auto()
    AND = auto()
    OR = auto()
    ADD = auto()
    MUL = auto()
    MOD = auto()
    DIV = auto()
    SHL = auto()
    SHR = auto()
```

```python
class ALUPortCtrl(CEnumM):
    """
    Набор операций применяемый к порту АЛУ перед вычислением, множественный выбор
    """
    PASS = 0b0000  # прямая передача аргумента
    NOT = 0b0001  # инверсия бит
    INC = 0b0010  # инкремент
    SXTB = 0b0100  # расширение знака 8->32бит
    SXTW = 0b1000  # расширение знака 16->32бит
    TKB = 0b10000  # взятие младшего байта
    TKW = 0b100000  # взятие младшего слова (16 бит)
```

```python
class ALUFlagCtrl(CEnumS):
    NONE = 0  # не менять PS
    WRITE = 1  # сохранить флаги в PS
```

```python
class StackCtrl(CEnumS):
    """
    биты 0-1 определяют сдвиг вершины стека
    бит 2 отвечает за произведение записи после сдвига в вершину (1 - запись)
    """
    NONE = 0b000  # не менять стек
    PUSH = 0b101  # классический push со сдвигом
    POP = 0b011  # классический pop со сдвигом
    REP = 0b100  # запись в вершину без сдвига
    POPREP = 0b111  # альтернатива последовательным POP и REP
```

```python
class MachineCtrl(CEnumM):
    HALT = 0b1  # остановить исполнение
```

```python
class MachineIOCtrl(CEnumS):
    NONE = 0
    SET_ADDR = 1  # начало взаимодействия, выбрать адрес
    SET_DATA = 2  # записать данные в контроллер перед передачей
    GET_DATA = 3  # получить данные из контроллера после получения
    REQ_READ = 4  # отправить запрос на чтение
    REQ_WRITE = 5  # отправить данные устройству
```

</details>
