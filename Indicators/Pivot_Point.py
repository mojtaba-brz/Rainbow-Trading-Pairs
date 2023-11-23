import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
from datetime import datetime

def calc_current_classic_pivot_point_levels(last_daily_candle):
    H = last_daily_candle.high
    L = last_daily_candle.low
    C = last_daily_candle.close
    
    P =  (H + L + C) / 3
    R1 = 2*P - L
    S1 = 2*P - H
    R2 = P + (H-L)
    S2 = P - (H - L)
    R3 = R1 + (H - L)
    S3 = S1 - (H - L)
    
    pp_level = [
        P,
        
        R1,
        R2,
        R3,
        
        S1,
        S2,
        S3
    ]

    return np.array(pp_level)
    
# print(calc_current_classic_pivot_point_levels("EURUSD"))