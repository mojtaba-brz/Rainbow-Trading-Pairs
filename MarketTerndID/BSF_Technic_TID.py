import numpy as np
import pandas as pd

from Indicators.Fractal import there_is_a_down_fractal_there, there_is_a_up_fractal_there
from MarketTerndID.TrendParams import *

def bsf_trend_estimation(df):
    n = len(df)
    trend = TREND.UNKNOWN
    trend_canlde = None
    for i in range(n-3, 1, -1):
        if (there_is_a_up_fractal_there(df, i) and any(df.high[i] < df.high[i+1:])):
            trend = TREND.UP_TREND
            trend_canlde = df[i+1:][df.high[i] < df.high[i+1:]].iloc[0]
            break
        if there_is_a_down_fractal_there(df, i) and any(df.low[i] > df.low[i+1:]):
            trend = TREND.DOWN_TREND    
            trend_canlde = df[i+1:][df.low[i] > df.low[i+1:]].iloc[0]
            break
    return trend, trend_canlde