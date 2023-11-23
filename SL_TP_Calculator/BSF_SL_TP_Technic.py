import numpy as np
import pandas as pd
from Indicators.Pivot_Point import calc_current_classic_pivot_point_levels
from TR_Bots.TRBotsParams import Modes
from Indicators.Fractal import there_is_a_down_fractal_there, there_is_a_up_fractal_there
from TR_Bots.BotsCommonClass import BotsCommonClass
from Market.MarketTools import *

def calc_tp(last_daily_candle,
            symbol_digits,
            buy_stop_pos = -1, 
            sell_stop_pos = -1,
            big_value = BotsCommonClass.big_value):
    buy_stop_TP_pos = -1
    sell_stop_TP_pos = -1
    pp_levels = calc_current_classic_pivot_point_levels(last_daily_candle)
    if(buy_stop_pos > 0 and buy_stop_pos < big_value and len(pp_levels[pp_levels > (buy_stop_pos * 1.0005)])>0):
        buy_stop_TP_pos = min(pp_levels[pp_levels > (buy_stop_pos * 1.0005)])
        pow = symbol_digits
        if(pow == 5):
            buy_stop_TP_pos = float('%.5f'%(buy_stop_TP_pos))
        elif(pow == 3):
            buy_stop_TP_pos = float('%.3f'%(buy_stop_TP_pos))
        else:
            buy_stop_TP_pos = round(buy_stop_TP_pos*(10**pow))/(10**pow)
    elif(sell_stop_pos > 0 and sell_stop_pos < big_value and len(pp_levels[pp_levels < (sell_stop_pos * 0.9995)])>0):
        sell_stop_TP_pos = max(pp_levels[pp_levels < (sell_stop_pos * 0.9995)])
        pow = symbol_digits
        if(pow == 5):
            sell_stop_TP_pos = float('%.5f'%(sell_stop_TP_pos))
        elif(pow == 3):
            sell_stop_TP_pos = float('%.3f'%(sell_stop_TP_pos))
        else:
            sell_stop_TP_pos = round(sell_stop_TP_pos*(10**pow))/(10**pow)
    return buy_stop_TP_pos, sell_stop_TP_pos

def look_for_sell_stop_loss_pos(mode, df_m5_rates, m30_trend_canlde, sell_stop_pos, bid_price, pre_sl):
    n = len(df_m5_rates)
    for i in range(n-3, 1, -1):
        if(df_m5_rates.time[i] <= m30_trend_canlde.time):
            return pre_sl
        if (there_is_a_up_fractal_there(df_m5_rates, i) and  
            ((df_m5_rates.high[i] > sell_stop_pos * (1+0.0005) and mode == Modes.SELL_PENDING_ORDER) or
            (df_m5_rates.high[i] > bid_price * (1+0.0005) and mode == Modes.MANAGE_SHORT_POSITION)) and
            all(df_m5_rates.high[i] > df_m5_rates.high[i+1:])):
            return df_m5_rates.high[i]
def look_for_buy_stop_loss_pos(mode, df_m5_rates, m30_trend_canlde, buy_stop_pos, ask_price, pre_sl):
    n = len(df_m5_rates)
    for i in range(n-3, 1, -1):
        if(df_m5_rates.time[i] <= m30_trend_canlde.time):
            return pre_sl
        if(there_is_a_down_fractal_there(df_m5_rates, i) and
            ((df_m5_rates.low[i] < buy_stop_pos * (1-0.0005) and mode == Modes.BUY_PENDING_ORDER) or
            (df_m5_rates.low[i] < ask_price * (1-0.0005) and mode == Modes.MANAGE_LONG_POSITION)) and
            all(df_m5_rates.low[i] < df_m5_rates.low[i+1:])):
            return df_m5_rates.low[i]
    return -1