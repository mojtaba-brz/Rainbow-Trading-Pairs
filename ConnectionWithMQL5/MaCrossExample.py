import numpy as np
from time import sleep

# Local Import ========================================================
from TrBotPYSideClient import TrBotPYSideClient
from typedefs import *

tbc = TrBotPYSideClient(host_addr = "127.0.0.1", host_port = 65333, hello_period = 10)

# wait for params
while True:
    message = tbc.get_algo_params()
    if message:
        break
slow_ma_period, fast_ma_period = tuple(int(x) for x in message.split(';'))

while True:
    rates, _ = tbc.get_market_states_if_available()
    if rates :
        closes = rates.close_array
        slow_ma = np.mean(closes[-slow_ma_period:])
        fast_ma = np.mean(closes[-fast_ma_period:])
        if fast_ma > slow_ma:
            tbc.send_action(TR_ACTIONS.BUY_NOW.value)
        else:
            tbc.send_action(TR_ACTIONS.SELL_NOW.value)
    sleep(.01)

    
