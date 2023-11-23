import numpy as np
from time import sleep
from ray.rllib.algorithms.ppo import PPOConfig
import os
def clc():
    os.system('cls' if os.name == 'nt' else 'clear')
    
# Local Import ========================================================
from ConnectionWithMQL5.TrBotPYSideClient import TrBotPYSideClient
from ConnectionWithMQL5.typedefs import *
from Simulator.MetaTraderEnv import MetaTrader5Env

slow_ma_period, fast_ma_period = 10, 5
env = MetaTrader5Env()

action = TR_ACTIONS.DO_NOTHING.value
while True:
    market_states, reward, _, _, _ = env.step(action)
    if market_states :
        clc()
        print(f"profit = {market_states['current position']:>2},   t : {market_states['hour']}")
        closes = market_states["5m timeframe hlc"].close_array
        baseline = np.mean(market_states["30m timeframe hlc"].close_array[-10:]) 
        slow_ma = np.mean(closes[-slow_ma_period:])
        fast_ma = np.mean(closes[-fast_ma_period:])
        if fast_ma > slow_ma and closes[-1] > baseline:
            action = TR_ACTIONS.BUY_NOW.value
        elif fast_ma < slow_ma and closes[-1] < baseline:
            action = TR_ACTIONS.SELL_NOW.value
        else:
            action = TR_ACTIONS.DO_NOTHING.value
    sleep(.01)