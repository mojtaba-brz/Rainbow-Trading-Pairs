import enum
import numpy as np

# this enum class must be synced with mql side ===================================================
class MESSAGE_TYPE(enum.Enum):
    SAY_HELLO = 0
    ALGO_PARAMS = 1
    MARKET_STATES = 2
    ACTION = 3
    REQUEST_MESSAGE = 4
    CONNECTION_CHECK = 5
    UNKNOWN = 6
    
# this enum class must be synced with mql side
class TR_ACTIONS(enum.Enum):
    BUY_NOW    = 0
    SELL_NOW   = 1
    DO_NOTHING = 2
    CLOSE_POS  = 3

class DefaultMassage():
    def __init__(self, name = None, message_type = None, message = None):
        self.name = name
        self.message_type = message_type
        self.message = message

class POSITION_STATE(enum.Enum):
    NO_POSITION = 0
    LONG_POSITION = 1
    SHORT_POSITION = 2
    MORE_THAN_ONE_POSITION = 3
  

class MarketStates():
    def __init__(self):
        # 5m timeframe hlc  : high;low;close| 50 data
        # 30m timeframe hlc : high;low;close| 50 data
        # 4h timeframe hlc  : high;low;close| 50 data
        # 1d timeframe vol  : vol(0);vol(1);...| 20 data
        self.rates_5m = HLCRates()
        self.rates_30m = HLCRates()
        self.rates_4h = HLCRates()
        self.vol_1d = np.array([], dtype = np.int64)
        # Indicators        : strength of left side currency in 7 other pairs; strength of right side currency in 7 other pairs; daily atr|
        self.daily_atr = np.array([], dtype = np.float32)
        self.left_currency_strength = np.array([], dtype = np.float32)
        self.right_currency_strength = np.array([], dtype = np.float32)
        # time              : day of week;hour|
        self.day_of_week = 0
        self.hour = 0
        # robot status      : current position;current profit|
        self.current_position = POSITION_STATE.NO_POSITION
        self.current_profit = 0.
    
    def append_hlc_rates_5m(self, one_serie_tuple):
        self.rates_5m.append_all(one_serie_tuple)
    def append_hlc_rates_30m(self, one_serie_tuple):
        self.rates_30m.append_all(one_serie_tuple)
    def append_hlc_rates_4h(self, one_serie_tuple):
        self.rates_4h.append_all(one_serie_tuple)

class RewardRawData():
    def __init__(self):
        self.ballance_diff = 0
# ===============================================================================================
class DefaultMessage():
    def __init__(self, name = None, message_type = None, message = None):
        self.reset()
        if not(name is None or message_type is None or message is None):
            self.set_all(name, message_type, message)
               
    def reset(self):
        self.name = ""
        self.message_type = MESSAGE_TYPE.UNKNOWN
        self.message = ""
# Set Functions ===================================================================
# =================================================================================
    def set_all(self, name, message_type, message):
        self.name = name
        self.message_type = message_type
        self.message = message

class HLCRates():
    def __init__(self):
        self.high_array = np.array([], dtype=np.float32)
        self.low_array = np.array([], dtype=np.float32)
        self.close_array = np.array([], dtype=np.float32)

    def append_all(self, one_serie_tuple_string):
        self.high_array = np.append(self.high_array,                    float(one_serie_tuple_string[0]));
        self.low_array = np.append(self.low_array,                      float(one_serie_tuple_string[1]));
        self.close_array = np.append(self.close_array,                  float(one_serie_tuple_string[2]));