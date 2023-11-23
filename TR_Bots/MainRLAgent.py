import numpy as np
from time import sleep

# Local Import ========================================================
from ConnectionWithMQL5.TrBotPYSideClient import TrBotPYSideClient
from typedefs import *

tbc = TrBotPYSideClient()
slow_ma_period, fast_ma_period = 10, 5

while True:
    market_states, _ = tbc.get_market_states_if_available()
    print(market_states)
    if market_states :
        closes = market_states.rates.close_array
        slow_ma = np.mean(closes[-slow_ma_period:])
        fast_ma = np.mean(closes[-fast_ma_period:])
        if fast_ma > slow_ma:
            tbc.send_action(TR_ACTIONS.BUY_NOW.value)
        else:
            tbc.send_action(TR_ACTIONS.SELL_NOW.value)
    sleep(.01)

    
