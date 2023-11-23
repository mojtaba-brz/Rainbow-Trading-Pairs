from enum import Enum

class Modes(Enum):
    UNKNOWN = -1
    TREND_IDENTIFICATION = 0
    WAIT_FOR_M5_UP_BREAK = 1
    WAIT_FOR_M5_DOWN_BREAK = 2
    SELL_PENDING_ORDER = 3
    BUY_PENDING_ORDER = 4
    MANAGE_SHORT_POSITION = 5
    MANAGE_LONG_POSITION = 6
    IN_RANGE = 7
    NEWS_COMMING = 8
    HOLLY_DAY = 9
    WEEKEND = 10
    HIGH_SPREAD = 11
class SimMode(Enum):
    SIM_OFF = 0
    SIM_ONLY = 1
    SIM_AND_REAL_TIME_TRADE = 2