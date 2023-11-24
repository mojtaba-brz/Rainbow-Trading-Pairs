# # Forex Trading Beginner Strategy
# source : https://learn.tradimo.com
# 
# in this file I'm in to create a trading robot based on this strategy.   
# this strategy is short term and because of that amount if spread has  
# signaficant effect on it. so I just apply it on those pairs that have   
# spread lower than 2 pips.
# 
# ### Strategy :
# 1- Identify the trend   
# 2- wait for trading opportunaty  
# 3- set buy/sell stop pending order, SL and TP  
# 4- manage your pending order  
# 5- after entering a position, manage the SL  

# ===================================================================================================================================
# ========================================================== Imports ================================================================
# ===================================================================================================================================
from datetime import datetime, timezone
import time
import MetaTrader5 as mt5
import pandas as pd
from enum import Enum
from IPython.display import clear_output
import numpy as np
from threading import Thread
import os
from termcolor import colored
import colorama
colorama.init()
from matplotlib import pyplot as plt
# ===================================================================================================================================
# ======================================================= Local Imports =============================================================
# ===================================================================================================================================
from Market.MarketTools import *
from Simulator.MarketSim.MarketSim import PairSimulator
from MarketTerndID.TrendParams import TREND
from TR_Bots.TRBotsParams import Modes, SimMode
from TR_Bots.BotsCommonClass import BotsCommonClass
from Indicators.Fractal import there_is_a_down_fractal_there, there_is_a_up_fractal_there, plot_fractals_for_a_df_by_index
from MarketTerndID.BSF_Technic_TID import bsf_trend_estimation
from SL_TP_Calculator.BSF_SL_TP_Technic import calc_tp, look_for_sell_stop_loss_pos, look_for_buy_stop_loss_pos
from Simulator.MarketSim.visualization import *
# ===================================================================================================================================
# ========================================================== Configs ================================================================
# ===================================================================================================================================
loop_period_sec = 5. * 60
debug_mode = False
n_steps_of_debug_mode = 3
# ===================================================================================================================================
# ======================================================== Report Funcs =============================================================
# ===================================================================================================================================
def clc():
    clear_output(wait=True)
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(): # this function should give to a parallel thread with main bot thread
    n = 1
    while(True):
        start_time = time.time()
        print(colored("\nsymbol\t\tMode\t\tentry\t\tSL\t\tTP\t\treq_status\t\tMT5 Last Err\n","red"))
    
        if debug_mode:
            n += 1
            if n > n_steps_of_debug_mode:
                break
        
        end_time = time.time()
        time.sleep(-end_time + start_time + loop_period_sec)
        

class BSF_Class(BotsCommonClass):  
# ===========================================================================================================================================
# ======================================================= Init Functions ==================================================================== 
# ===========================================================================================================================================    
    def __init__(self, name, sim_mode = SimMode.SIM_OFF):
        super().__init__()
        self.robot_id = 12345
        self.h4_trend = TREND.UNKNOWN
        self.m30_trend = TREND.UNKNOWN
        self.ban_modes = [Modes.HOLLY_DAY, Modes.WEEKEND, Modes.IN_RANGE, Modes.HIGH_SPREAD]
        self.simulation_mode = sim_mode
        self.name = name
        if sim_mode != SimMode.SIM_ONLY:
            self.real_init()
        if sim_mode != SimMode.SIM_OFF:
            self.sim_init()
            
    def real_init(self):
        self.check_ban_modes()
        if self.mode['real'] in self.ban_modes :
            return
        self.identify_the_trend()
        
        if(self.there_is_no_more_than_one_order_or_position()):
            myOrder = get_orders(self.name)
            myPosition = get_positions(self.name)
            if myOrder == None or myPosition == None:
                print("wrong initialization in", self.name)
            if myOrder != ():
                self.take_my_order()
                self.check_for_trend_change()
            elif myPosition != ():
                self.take_my_position()
                self.check_for_trend_change()
            else:
                self.reset_pos()
    
    def sim_init(self):
        self.trend['sim'] = TREND.UNKNOWN
        self.mode['sim'] = Modes.UNKNOWN
        self.fig, self.axs = plt.subplots(3,1)
        self.fig.set_figwidth(15)
        self.fig.set_figheight(15)
        self.init_pair_simualtor()
        self.init_trade_sim()
        self.identify_the_trend(call_mode= 'sim')
# ===========================================================================================================================================
# ====================================================== Reset Functions ==================================================================== 
# ===========================================================================================================================================     
    def reset(self, call_mode = 'real'):
        self.trend[call_mode] = TREND.UNKNOWN
        self.reset_pos(call_mode)
        self.mode[call_mode]  = Modes.UNKNOWN
        self.remove_my_orders(call_mode)
        self.close_my_posiitons(call_mode)
    
    def reset_pos(self, call_mode = 'real'):
        self.sell_stop_pos[call_mode] = -1
        self.buy_stop_pos[call_mode] = -1
        self.buy_stop_SL_pos[call_mode] = -1
        self.sell_stop_SL_pos[call_mode] = -1
        self.buy_stop_TP_pos[call_mode] = -1
        self.sell_stop_TP_pos[call_mode] = -1
# ===========================================================================================================================================
# ====================================================== Trading Bot Steps ================================================================== 
# =========================================================================================================================================== 
    def step(self, report_on = True, call_mode = 'real'):
        if call_mode == 'sim':
            self.pair_sim_step()
            self.update_m5_df_rates(call_mode)
            self.main_data_frame = self.df_m5_rates
            
        if self.mode[call_mode] not in self.ban_modes: 
            self.check_ban_modes(call_mode)
        
        if(self.mode[call_mode] == Modes.UNKNOWN or self.mode[call_mode] in self.ban_modes or self.mode[call_mode] == Modes.TREND_IDENTIFICATION):
            self.identify_the_trend(call_mode)            
            
        if(self.mode[call_mode] == Modes.WAIT_FOR_M5_DOWN_BREAK):
            self.check_if_there_is_a_m5_down_break(call_mode)
        elif(self.mode[call_mode] == Modes.WAIT_FOR_M5_UP_BREAK):
            self.check_if_there_is_a_m5_up_break(call_mode)
        
        if(self.mode[call_mode] == Modes.SELL_PENDING_ORDER):
            self.check_for_trend_change(call_mode)
            self.look_for_sell_stop_pos(call_mode)
            self.update_sell_SL_and_TP(call_mode)
            if call_mode == 'sim':
                self.tranfer_order_to_position_if_possible(self.df_m5_rates)
            self.manage_sell_order(call_mode)
        elif(self.mode[call_mode] == Modes.BUY_PENDING_ORDER):
            self.check_for_trend_change(call_mode)
            self.look_for_buy_stop_pos(call_mode)
            self.update_buy_SL_and_TP(call_mode)
            if call_mode == 'sim':
                self.tranfer_order_to_position_if_possible(self.df_m5_rates)
            self.manage_buy_order(call_mode)
            
        if(self.mode[call_mode] == Modes.MANAGE_SHORT_POSITION):
            self.check_for_trend_change(call_mode)
            self.update_sell_SL_and_TP(call_mode)
            if call_mode == 'sim':
                self.manage_sim_position(self.get_todays_ohlc())
            self.manage_short_position(call_mode)
        elif(self.mode[call_mode] == Modes.MANAGE_LONG_POSITION):
            self.check_for_trend_change(call_mode)
            self.update_buy_SL_and_TP(call_mode)
            if call_mode == 'sim':
                self.manage_sim_position(self.get_todays_ohlc())
            self.manage_long_position(call_mode)

        if report_on :
            if self.mode[call_mode] in self.ban_modes:
                print(colored(f"%s\t%s"%(self.name, self.mode[call_mode].name), "green"))
            else:
                if call_mode == 'real':             
                    try:
                        print(colored(f"%s\t%s\t%s\t%s\t%s\t\t%s\t\t%s"%(self.name, self.mode[call_mode].name,
                            (self.sell_stop_pos[call_mode], self.buy_stop_pos[call_mode]), 
                            (self.sell_stop_SL_pos[call_mode], self.buy_stop_SL_pos[call_mode]), 
                            (self.sell_stop_TP_pos[call_mode], self.buy_stop_TP_pos[call_mode]), 
                            self.order_status[call_mode].comment, market_last_error()), "green"))
                    except:
                        print(colored(f"%s\t%s\t%s\t%s\t%s"%(self.name, self.mode[call_mode].name,
                            (self.sell_stop_pos[call_mode], self.buy_stop_pos[call_mode]), 
                            (self.sell_stop_SL_pos[call_mode], self.buy_stop_SL_pos[call_mode]), 
                            (self.sell_stop_TP_pos[call_mode], self.buy_stop_TP_pos[call_mode])), "green"))
                elif call_mode == 'sim':
                    ohlc = self.get_todays_ohlc()
                    print(colored(f"%s\t%s\t%s\t%s\t%s\t\t%s\t\t%s"%(self.name, self.mode[call_mode].name,
                            (self.sell_stop_pos[call_mode], self.buy_stop_pos[call_mode]), 
                            (self.sell_stop_SL_pos[call_mode], self.buy_stop_SL_pos[call_mode]), 
                            (self.sell_stop_TP_pos[call_mode], self.buy_stop_TP_pos[call_mode]),
                            self.account.balance,
                            (ohlc.open, ohlc.high, ohlc.low, ohlc.close)), "green"))   
# ===========================================================================================================================================
# ======================================================== Loop Functions =================================================================== 
# ===========================================================================================================================================   
    def run(self):
        n = 1
        while(True):
            start_time = time.time()
            self.step()
            
            if debug_mode:
                n += 1
                if n > n_steps_of_debug_mode:
                    break
                
            end_time = time.time()
            time.sleep(end_time - start_time + loop_period_sec)
            
# ===========================================================================================================================================
# ===================================================== Utility Functions =================================================================== 
# ===========================================================================================================================================    
    def update_h4_df_rates(self, call_mode = 'real'):
        if call_mode == 'sim' :
            self.df_h4_rates = self.sim_update_df_rates(TF='H4')
        elif call_mode == 'real' :
            self.df_h4_rates = get_rates(self.name, timeframe=mt5.TIMEFRAME_H4)   
    def update_m30_df_rates(self, call_mode = 'real'):
        if call_mode == 'sim' :
            self.df_m30_rates = self.sim_update_df_rates(TF='M30')
        elif call_mode == 'real' :
            self.df_m30_rates = get_rates(self.name, timeframe=mt5.TIMEFRAME_M30)
    def update_m5_df_rates(self, call_mode = 'real'):
        if call_mode == 'sim' :
            self.df_m5_rates = self.sim_update_df_rates(TF='M5')
        elif call_mode == 'real' :
            self.df_m5_rates = get_rates(self.name, timeframe=mt5.TIMEFRAME_M5)
    def update_d1_df_rates(self, call_mode = 'real'):
        if call_mode == 'sim' :
            self.df_d1_rates = self.sim_update_df_rates(TF='D1')
        elif call_mode == 'real' :
            self.df_d1_rates = get_rates(self.name, timeframe=mt5.TIMEFRAME_D1)
    
    def get_last_daily_candle(self, call_mode = 'real'):
        self.update_d1_df_rates(call_mode)
        return self.df_d1_rates.tail(1)
        
    def identify_the_trend(self, call_mode = 'real'):
        self.update_m30_df_rates(call_mode)
        self.update_h4_df_rates(call_mode)
        
        self.m30_trend, self.m30_trend_canlde[call_mode] = bsf_trend_estimation(self.df_m30_rates)
        self.h4_trend , _                                = bsf_trend_estimation(self.df_h4_rates)    
            
        if self.h4_trend == self.m30_trend:
            self.trend[call_mode] = self.m30_trend
            if self.mode[call_mode] == Modes.UNKNOWN:
                if self.m30_trend == TREND.UP_TREND:
                    self.mode[call_mode] = Modes.WAIT_FOR_M5_DOWN_BREAK
                elif self.m30_trend == TREND.DOWN_TREND:
                    self.mode[call_mode] = Modes.WAIT_FOR_M5_UP_BREAK
        else:
            self.trend[call_mode] = TREND.UNKNOWN
                 
    def check_if_there_is_a_m5_down_break(self, call_mode = 'real'):
        self.update_m5_df_rates(call_mode)
        n = len(self.df_m5_rates)
        for i in range(n-3, 1, -1):
            if(self.df_m5_rates.time[i] <= self.m30_trend_canlde[call_mode].time):
                break
            if there_is_a_down_fractal_there(self.df_m5_rates, i) and any(self.df_m5_rates.low[i] > self.df_m5_rates.low[i+1:]):
                self.mode[call_mode] = Modes.BUY_PENDING_ORDER
                break
    def check_if_there_is_a_m5_up_break(self, call_mode = 'real'):
        self.update_m5_df_rates(call_mode)
        n = len(self.df_m5_rates)
        for i in range(n-3, 1, -1):
            if(self.df_m5_rates.time[i] <= self.m30_trend_canlde[call_mode].time):
                break
            if there_is_a_up_fractal_there(self.df_m5_rates, i) and any(self.df_m5_rates.high[i] < self.df_m5_rates.high[i+1:]):
                self.mode[call_mode] = Modes.SELL_PENDING_ORDER
                break
    
    def look_for_sell_stop_pos(self, call_mode = 'real'):
        self.update_m5_df_rates(call_mode)
        n = len(self.df_m5_rates)
        pre_value = self.sell_stop_pos[call_mode]
        self.sell_stop_pos[call_mode] = -100
        if call_mode == 'real':
            bid = get_bid(self.name) * 0.9999
        else:
            bid = self.big_value # just to get rid of it for now
        for i in range(n-3, 1, -1):
            if(self.df_m5_rates.time[i] <= self.m30_trend_canlde[call_mode].time):
                break
            if (there_is_a_down_fractal_there(self.df_m5_rates, i) and 
                any(self.df_m5_rates.low[i] > self.df_m5_rates.low[i+1:])):
                break
            if(there_is_a_down_fractal_there(self.df_m5_rates, i) and 
                any(self.df_m5_rates.low[i] < self.df_m5_rates.low[i+1:]) and 
                self.df_m5_rates.low[i] < bid):
                self.sell_stop_pos[call_mode] = max(self.sell_stop_pos[call_mode], self.df_m5_rates.low[i]) 
        if(pre_value > 0 and pre_value < self.big_value and
           self.sell_stop_pos[call_mode] < 0):
            self.sell_stop_pos[call_mode] = pre_value
                  
    def look_for_buy_stop_pos(self, call_mode = 'real'):
        self.update_m5_df_rates(call_mode)
        n = len(self.df_m5_rates)
        pre_value = self.buy_stop_pos[call_mode]
        self.buy_stop_pos[call_mode] = self.big_value
        if call_mode == 'real':
            ask = get_ask(self.name) * 1.0001
        else:
            ask = self.df_m5_rates.low.iloc[-1] + np.random.random() * (self.df_m5_rates.high.iloc[-1] - self.df_m5_rates.low.iloc[-1])
        for i in range(n-3, 1, -1):
            if(self.df_m5_rates.time[i] <= self.m30_trend_canlde[call_mode].time):
                break
            if (there_is_a_up_fractal_there(self.df_m5_rates, i) and 
                any(self.df_m5_rates.high[i] < self.df_m5_rates.high[i+1:])):
                break
            if(there_is_a_up_fractal_there(self.df_m5_rates, i) and 
               any(self.df_m5_rates.high[i] > self.df_m5_rates.high[i+1:]) and 
               self.df_m5_rates.high[i] > ask):
               self.buy_stop_pos[call_mode] = min(self.buy_stop_pos[call_mode], self.df_m5_rates.high[i])
        if(pre_value > 0 and pre_value < self.big_value and
           self.buy_stop_pos[call_mode] == self.big_value):
            self.buy_stop_pos[call_mode] = pre_value

    def update_buy_SL_and_TP(self, call_mode = 'real'):
        self.update_m5_df_rates(call_mode)
        self.buy_stop_SL_pos[call_mode] = look_for_buy_stop_loss_pos(self.mode[call_mode], self.df_m5_rates, 
                                    self.m30_trend_canlde[call_mode], self.buy_stop_pos[call_mode], self.sim_get_ask() if call_mode == 'sim' else get_ask(self.name),
                                    self.buy_stop_SL_pos[call_mode])
        if call_mode == 'sim':
            self.buy_stop_TP_pos[call_mode], _ =  calc_tp(self.get_last_daily_candle(call_mode), 
                                                        self.sim_get_symbol_info().digits, 
                                                        self.buy_stop_pos[call_mode], self.sell_stop_pos[call_mode],
                                                        self.big_value)
        else :
            self.buy_stop_TP_pos[call_mode], _ =  calc_tp(self.get_last_daily_candle(call_mode), 
                                                        get_symbol_info(self.name).digits, 
                                                        self.buy_stop_pos[call_mode], self.sell_stop_pos[call_mode],
                                                        self.big_value)
    def update_sell_SL_and_TP(self, call_mode = 'real'):
        self.update_m5_df_rates(call_mode)
        self.sell_stop_SL_pos[call_mode] = look_for_sell_stop_loss_pos(self.mode[call_mode], self.df_m5_rates, 
                                    self.m30_trend_canlde[call_mode], self.sell_stop_pos[call_mode], self.sim_get_bid() if call_mode == 'sim' else get_bid(self.name),
                                    self.sell_stop_SL_pos[call_mode])
        if call_mode == 'sim':
            _, self.sell_stop_TP_pos[call_mode] =  calc_tp(self.get_last_daily_candle(call_mode), 
                                                    self.sim_get_symbol_info().digits, 
                                                    self.buy_stop_pos[call_mode], self.sell_stop_pos[call_mode],
                                                    self.big_value)
        else :
            _, self.sell_stop_TP_pos[call_mode] =  calc_tp(self.get_last_daily_candle(call_mode), 
                                                    get_symbol_info(self.name).digits, 
                                                    self.buy_stop_pos[call_mode], self.sell_stop_pos[call_mode],
                                                    self.big_value)

    def check_for_trend_change(self, call_mode = 'real'):
        pre_trend = self.trend[call_mode]
        self.identify_the_trend(call_mode)
        if(pre_trend != self.trend[call_mode]):
            self.reset(call_mode)
    
    def check_if_in_range(self, call_mode = 'real'):
        self.identify_the_trend(call_mode)
        if self.trend[call_mode] == TREND.RANGE:
            self.mode[call_mode] = Modes.IN_RANGE
    
    def check_ban_modes(self, call_mode = 'real'):
        if call_mode != 'real':
            return
        current_time_struct = time.gmtime()
        if (current_time_struct.tm_wday == 5 or
            (current_time_struct.tm_wday == market_open_time.tm_wday and current_time_struct.tm_hour < market_open_time.tm_hour) or
            (current_time_struct.tm_wday == market_close_time.tm_wday and current_time_struct.tm_hour >= market_close_time.tm_hour)):
            self.mode[call_mode] = Modes.WEEKEND
            return
        elif get_spread(self.name) > 20 and self.mode[call_mode] != Modes.MANAGE_LONG_POSITION and self.mode[call_mode] != Modes.MANAGE_SHORT_POSITION:
            self.reset(call_mode)
            self.mode[call_mode] = Modes.HIGH_SPREAD
            return
        self.check_if_in_range()
        
    def sim_render(self, delay_s = 0.1):
        self.update_m5_df_rates('sim')
        self.axs[0].clear()
        draw_candle_stick_by_index(self.df_m5_rates, self.axs[0])
        plot_fractals_for_a_df_by_index(self.df_m5_rates, self.axs[0])
        temp_text = f"""time : {self.data_frame['M5'].time.iloc[self.sim_index['M5']]}   Mode  : {self.mode['sim']}      
Trend : {self.trend['sim']}
M30 Trend : {self.m30_trend}        H4 Trend : {self.h4_trend}"""
        write_text_on_chart_by_index(temp_text, "left", self.axs[0])
        if self.order.type is not None:
            draw_order_on_chart_by_index(self.order, self.axs[0])
            temp_text = f"entry : {self.order.price_open}\nsl : {self.order.sl}, tp : {self.order.tp}"
            write_text_on_chart_by_index(temp_text, 'right', self.axs[0])
        elif self.position.type is not None:
            draw_order_on_chart_by_index(self.position, self.axs[0])
            temp_text = f"entry : {self.position.price_open}\nsl : {self.position.sl}, tp : {self.position.tp}\nbalance : {self.account.balance}"
            write_text_on_chart_by_index(temp_text, 'right', self.axs[0])
        self.axs[0].set_title("M5 OHLC")
        self.axs[0].set_xlabel("Index")
        self.axs[0].set_ylabel(self.name)

        self.update_m30_df_rates('sim')
        self.axs[1].clear()
        draw_candle_stick_by_index(self.df_m30_rates, self.axs[1])
        plot_fractals_for_a_df_by_index(self.df_m30_rates, self.axs[1])
        self.axs[1].set_title("M30 OHLC")
        self.axs[1].set_xlabel("Index")
        self.axs[1].set_ylabel(self.name)

        self.update_h4_df_rates('sim')
        self.axs[2].clear()
        draw_candle_stick_by_index(self.df_h4_rates, self.axs[2])
        plot_fractals_for_a_df_by_index(self.df_h4_rates, self.axs[2])
        self.axs[2].set_title("H4 OHLC")
        self.axs[2].set_xlabel("Index")
        self.axs[2].set_ylabel(self.name)
        plt.pause(delay_s)        