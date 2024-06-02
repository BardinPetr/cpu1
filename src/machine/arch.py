import enum
import inspect
from enum import auto
from typing import Union, Dict

from src.machine.utils.enums import CEnumM, CEnumS, CtrlEnum


class PSFlags(CEnumM):
    Z = 0
    N = 1
    C = 2
    V = 3

    @staticmethod
    def decode_flags(val: Union["PSFlags", int]) -> dict:
        val = int(val)
        return {i.name: bool(val & (1 << i.value)) for i in PSFlags}

    @staticmethod
    def print_flags(val: Union["PSFlags", int]) -> str:
        decoded = PSFlags.decode_flags(val)
        decoded = sorted(decoded.items(), key=lambda x: -PSFlags[x[0]].value)
        return "".join((n if v else "-") for n, v in decoded)


class BusInCtrl(CEnumS):
    Z = 0  # ноль
    PS = 0b0001  # регистр PS
    DR = 0b0010  # регистр вывода данных из памяти
    IOR = 0b0011  # регистр вывода данных из IO контроллера
    DST = 0b0100  # значение вершины стека D
    DSS = 0b0101  # значение под вершиной стека D
    RST = 0b0110  # значение вершины стека R
    RSS = 0b0111  # значение под вершиной стека R
    IP = 0b1000  # регистр IP
    CR = 0b1001  # регистр CR


class BusOutCtrl(CEnumS):
    Z = 0b000  # нет записи
    PS = 0b001  # запись в PS
    DR = 0b010  # запись во входной регистр данных памяти
    AR = 0b011  # запись в AR
    DS = 0b100  # передача входного значения в контроллер стека D
    RS = 0b101  # передача входного значения в контроллер стека R
    IP = 0b110  # запись в IP
    CR = 0b111  # запись в CR


class MemCtrl(CEnumS):
    IGN = 0  # нет записи
    WR = 1  # запись в память


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


class ALUFlagCtrl(CEnumS):
    NONE = 0  # не менять PS
    WRITE = 1  # сохранить флаги в PS


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


class MachineCtrl(CEnumM):
    HALT = 0b1  # остановить исполнение


class MachineIOCtrl(CEnumS):
    NONE = 0
    SET_ADDR = 1  # начало взаимодействия, выбрать адрес
    SET_DATA = 2  # записать данные в контроллер перед передачей
    GET_DATA = 3  # получить данные из контроллера после получения
    REQ_READ = 4  # отправить запрос на чтение
    REQ_WRITE = 5  # отправить данные устройству


class IOBusCtrl(CEnumM):
    WR = 0b001
    RD = 0b010
    TXE = 0b100


def extract_enums() -> Dict[str, Dict[str, int]]:
    external_frame = inspect.getouterframes(inspect.currentframe())[1]
    f_locals = external_frame.frame.f_locals
    return {
        k: {e(e_k).name: e_k.value for e_k in e}
        for k, e in f_locals.items()
        if type(e) == enum.EnumType and issubclass(e, CtrlEnum) and len(e) > 0
    }
