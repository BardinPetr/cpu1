from enum import IntEnum, auto


class PSFlags(IntEnum):
    Z = 0
    N = 1
    C = 2
    V = 3


class RegFileIdCtrl(IntEnum):
    XX = 0
    IP = auto()
    CR = auto()
    DR = auto()


class RegisterIdCtrl(IntEnum):
    CR = 0


class MainBusInCtrl(IntEnum):
    """
    Format:
    0xx - xx is classic source
    1xx - xx is regfile ID
    """
    IGNORE = 0b000
    SRC_1 = 0b001
    SRC_2 = 0b010
    SRC_3 = 0b011
    RF_XX = 0b100 + RegFileIdCtrl.XX
    RF_IP = 0b100 + RegFileIdCtrl.IP
    RF_CR = 0b100 + RegFileIdCtrl.CR
    RF_DR = 0b100 + RegFileIdCtrl.DR


class MainBusOutCtrl(IntEnum):
    """
    Format:
    0xx - xx is classic source
    1xx - xx is regfile ID
    """
    IGNORE = 0b000
    SRC_1 = 0b001
    SRC_2 = 0b010
    SRC_3 = 0b011
    RF_XX = 0b100 + RegFileIdCtrl.XX
    RF_IP = 0b100 + RegFileIdCtrl.IP
    RF_CR = 0b100 + RegFileIdCtrl.CR
    RF_DR = 0b100 + RegFileIdCtrl.DR
