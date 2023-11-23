import pandas as pd
import numpy as np
import MetaTrader5 as mt5
import matplotlib.pyplot as plt
import os
from termcolor import colored
import colorama
colorama.init()
from enum import Enum
from ..OHLC_data_gathering import time_decomposition
from copy import copy

class SymbolInfo():
    digits = 5
class PairSimulator():
# ====================================================================================================================================
# ============================================== Constants and Initializations =======================================================
# ====================================================================================================================================
    all_days_of_week = 5
    all_time_frames  = ('D1', 'H1', 'H4', 'M5', 'M15', 'M30')
    sim_index        = {'D1' : 0, 'H1' : 0, 'H4' : 0, 'M5' : 0, 'M15' : 0, 'M30' : 0}
    symbol_info = SymbolInfo()
# ===========================================================================================================================================
# ======================================================= Init Functions ==================================================================== 
# ===========================================================================================================================================    
    def __init__(self, symbol_name, main_time_frame = 'M5'):
        # Ex : symbol_name = 'EURUSD'
        self.name = symbol_name
        self.init_pair_simualtor(main_time_frame)
    
    def init_pair_simualtor(self, main_time_frame = 'M5', min_main_time_frame_offset = 100) : # this function should be called on child classs
        self.data_frame = {}
        for time_frame in self.all_time_frames:
            self.file_name = f"{__file__[:-22]}OHLC_Data\\{self.name}_{time_frame}.csv"
            self.data_frame[time_frame] = pd.read_csv(self.file_name).drop(columns=['Unnamed: 0'])
        
        if 'year' not in self.data_frame[main_time_frame]:
            for tf in self.all_time_frames:
                self.data_frame[tf] = time_decomposition(self.data_frame[tf])
        
        min_main_time_frame_offset = max(min_main_time_frame_offset, 100)    
        self.main_time_frame = main_time_frame
        self.main_time_frame_error_handler()
        self.min_main_time_frame_offset = min_main_time_frame_offset
        self.sim_index[self.main_time_frame] = min_main_time_frame_offset-1
        self.set_sim_index_to_starting_time_of_next_monday()
        self.syncronize_indices()

# ===========================================================================================================================================
# ====================================================== Reset Functions ==================================================================== 
# ===========================================================================================================================================            
    def reset(self, reset_index_to = 100):
        self.sim_index = reset_index_to
        self.set_sim_index_to_starting_time_of_next_monday()
        self.syncronize_indices()
# ===========================================================================================================================================
# ====================================================== Simulation Steps =================================================================== 
# ===========================================================================================================================================    
    def get_pair_states(self): # Func ======================================
        time    = self.data_frame.time[self.sim_index].split()
        time[1] = time[1].split(':')
        time[0] = time[0].split('-')
        hour = float(time[1][0])
        min  = float(time[1][1])
        day  = float(self.data_frame.day_of_week[self.sim_index])
        return (day, hour, min) # =====================================

    def pair_sim_step(self):
        self.sim_index[self.main_time_frame] += 1
        self.syncronize_indices()
        
# *******************************************************************************************************************************************
# ****************************************************** Utility Functions ******************************************************************
# *******************************************************************************************************************************************

# General Functions =======================================================================================================

    def syncronize_indices(self):
        if self.main_time_frame == 'M5':  
            current_minute = self.data_frame['M5'].minute[self.sim_index['M5']]    
            current_hour   = self.data_frame['M5'].hour[self.sim_index['M5']]    
            current_day    = self.data_frame['M5'].day[self.sim_index['M5']]    
            current_mon    = self.data_frame['M5'].mounth[self.sim_index['M5']]    
            current_year   = self.data_frame['M5'].year[self.sim_index['M5']]
            
            current_minute_M15 = (current_minute//15) * 15
            current_minute_M30 = (current_minute//30) * 30
            current_hour_H4    = (current_hour//4) * 4    
            
            temp = self.data_frame['M15']
            self.sim_index['M15'] = temp[current_year == temp.year][current_mon == temp.mounth][current_day == temp.day][current_hour == temp.hour][current_minute_M15 == temp.minute].index.values[0]
            temp = self.data_frame['M30']
            self.sim_index['M30'] = temp[current_year == temp.year][current_mon == temp.mounth][current_day == temp.day][current_hour == temp.hour][current_minute_M30 == temp.minute].index.values[0]
            temp = self.data_frame['H1']
            self.sim_index['H1'] = temp[current_year == temp.year][current_mon == temp.mounth][current_day == temp.day][current_hour == temp.hour].index.values[0]
            temp = self.data_frame['H4']
            self.sim_index['H4'] = temp[current_year == temp.year][current_mon == temp.mounth][current_day == temp.day][current_hour_H4 == temp.hour].index.values[0]
            temp = self.data_frame['D1']
            self.sim_index['D1'] = temp[current_year == temp.year][current_mon == temp.mounth][current_day == temp.day].index.values[0]
        
        elif self.main_time_frame == 'M15':
            current_minute = self.data_frame['M15'].minute[self.sim_index['M15']]    
            current_hour   = self.data_frame['M15'].hour[self.sim_index['M15']]    
            current_day    = self.data_frame['M15'].day[self.sim_index['M15']]    
            current_mon    = self.data_frame['M15'].mounth[self.sim_index['M15']]    
            current_year   = self.data_frame['M15'].year[self.sim_index['M15']]
            
            current_minute_M30 = (current_minute//30) * 30
            current_hour_H4    = (current_hour//4) * 4    
            
            temp = self.data_frame['M30']
            self.sim_index['M30'] = temp[current_year == temp.year][current_mon == temp.mounth][current_day == temp.day][current_hour == temp.hour][current_minute_M30 == temp.minute].index.values[0]
            temp = self.data_frame['H1']
            self.sim_index['H1'] = temp[current_year == temp.year][current_mon == temp.mounth][current_day == temp.day][current_hour == temp.hour].index.values[0]
            temp = self.data_frame['H4']
            self.sim_index['H4'] = temp[current_year == temp.year][current_mon == temp.mounth][current_day == temp.day][current_hour_H4 == temp.hour].index.values[0]
            temp = self.data_frame['D1']
            self.sim_index['D1'] = temp[current_year == temp.year][current_mon == temp.mounth][current_day == temp.day].index.values[0]
        
        elif self.main_time_frame == 'M30':   
            current_hour   = self.data_frame['M30'].hour[self.sim_index['M30']]    
            current_day    = self.data_frame['M30'].day[self.sim_index['M30']]    
            current_mon    = self.data_frame['M30'].mounth[self.sim_index['M30']]    
            current_year   = self.data_frame['M30'].year[self.sim_index['M30']]
            
            current_hour_H4    = (current_hour//4) * 4    
            
            temp = self.data_frame['H1']
            self.sim_index['H1'] = temp[current_year == temp.year][current_mon == temp.mounth][current_day == temp.day][current_hour == temp.hour].index.values[0]
            temp = self.data_frame['H4']
            self.sim_index['H4'] = temp[current_year == temp.year][current_mon == temp.mounth][current_day == temp.day][current_hour_H4 == temp.hour].index.values[0]
            temp = self.data_frame['D1']
            self.sim_index['D1'] = temp[current_year == temp.year][current_mon == temp.mounth][current_day == temp.day].index.values[0]
        
        elif self.main_time_frame == 'H1':   
            current_hour   = self.data_frame['H1'].hour[self.sim_index['H1']]    
            current_day    = self.data_frame['H1'].day[self.sim_index['H1']]    
            current_mon    = self.data_frame['H1'].mounth[self.sim_index['H1']]    
            current_year   = self.data_frame['H1'].year[self.sim_index['H1']]
            
            current_hour_H4    = (current_hour//4) * 4    

            temp = self.data_frame['H4']
            self.sim_index['H4'] = temp[current_year == temp.year][current_mon == temp.mounth][current_day == temp.day][current_hour_H4 == temp.hour].index.values[0]
            temp = self.data_frame['D1']
            self.sim_index['D1'] = temp[current_year == temp.year][current_mon == temp.mounth][current_day == temp.day].index.values[0]
            
        elif self.main_time_frame == 'H4':  
            current_day    = self.data_frame['H4'].day[self.sim_index['H4']]    
            current_mon    = self.data_frame['H4'].mounth[self.sim_index['H4']]    
            current_year   = self.data_frame['H4'].year[self.sim_index['H4']]   

            temp = self.data_frame['D1']
            self.sim_index['D1'] = temp[current_year == temp.year][current_mon == temp.mounth][current_day == temp.day].index.values[0]
        else:
            pass # no syncronization neeeded
    
    def sim_update_df_rates(self, tf):
        return self.data_frame[tf].iloc[self.sim_index[tf]-self.min_main_time_frame_offset+1: self.sim_index[tf]+1].reset_index()
    
    def set_sim_index_to_starting_time_of_next_monday(self):
        i  = self.sim_index[self.main_time_frame]
        df = self.data_frame[self.main_time_frame].iloc[i:]
        self.sim_index[self.main_time_frame]  = df[df.day_of_week == 0][df.hour == 0][df.minute < 10].index.values[0]
        
    def sim_get_symbol_info(self):
        return self.symbol_info
    
    def sim_get_ask(self):
        return (self.data_frame[self.main_time_frame].low.iloc[self.sim_index[self.main_time_frame]+1] + 
                np.random.random() * (self.data_frame[self.main_time_frame].high.iloc[self.sim_index[self.main_time_frame]+1] 
                                    - self.data_frame[self.main_time_frame].low.iloc[self.sim_index[self.main_time_frame]+1]))
    def sim_get_bid(self):
        return (self.data_frame[self.main_time_frame].low.iloc[self.sim_index[self.main_time_frame]+1] + 
                np.random.random() * (self.data_frame[self.main_time_frame].high.iloc[self.sim_index[self.main_time_frame]+1] 
                                    - self.data_frame[self.main_time_frame].low.iloc[self.sim_index[self.main_time_frame]+1]))
    def get_todays_ohlc(self):
        return self.data_frame[self.main_time_frame].iloc[self.sim_index[self.main_time_frame]+1]
# Error Handellers =========================================================================================================
# ========================================================================================================================== 
    def main_time_frame_error_handler(self):
        if self.main_time_frame not in self.all_time_frames:
            print(colored(f"""
====================================================
Main TimeFrame ERROR:
your time frame is {self.main_time_frame} and
it is not in allowed TimeFrames
Allowed TFs are :
{self.all_time_frames}
====================================================\n""", 'red'))
            quit()
# -------------------------------------***************************************************----------------------------------------
# -------------------------------------***************************************************----------------------------------------
# -------------------------------------***************************************************----------------------------------------
# -------------------------------------***************************************************----------------------------------------
# -------------------------------------***************************************************----------------------------------------
# -------------------------------------***************************************************----------------------------------------
class TRADE_SIM_MODE(Enum):
    IDLE = 0
    IN_ORDER = 1
    IN_POSITION = 2      
class AccountInfo():
    def __init__(self) -> None:
        self.leverage = 100
        self.trade_expert = True
        self.currency_digit = 5
        self.profit = 0
        self.equity = 1000
        self.margin = 0
        self.margin_free = 100 * self.leverage
        self.name = ''
class OrderClass():
    def __init__(self):
        self.reset()
    def reset(self):
        self.type       = None
        self.price_open = None
        self.sl         = None
        self.tp         = None
        self.volume     = None
        self.magic      = None
class ErrorMassage():
    def __init__(self):
        self.retcode = 10009 
def get_one_lot_in_dollar(symbol_name):
    return 100000 * get_symbol_price_in_dollar(symbol_name)
def get_symbol_price_in_dollar(symbol_name):
    return 1 # TODO: support all common symbols
class TradeSim():
    # Constants ==============================================================================================================
    buy_orders = {mt5.ORDER_TYPE_BUY, mt5.ORDER_TYPE_BUY_LIMIT, mt5.ORDER_TYPE_BUY_STOP, mt5.ORDER_TYPE_BUY_STOP_LIMIT}
    sell_orders = {mt5.ORDER_TYPE_SELL, mt5.ORDER_TYPE_SELL_LIMIT, mt5.ORDER_TYPE_SELL_STOP, mt5.ORDER_TYPE_SELL_STOP_LIMIT}
    # variables initialization =============================================================================================== 
    def __init__(self) -> None:  
        self.account = AccountInfo()
        self.order = OrderClass()
        self.position = OrderClass()
           
    def init_trade_sim(self, starting_cash = 1000, broker_fee = 0.002, leverage = 100):
        self.starting_cash = starting_cash
        self.broker_fee = broker_fee
        self.account.equity = starting_cash
        self.account.balance = starting_cash
        self.account.leverage = leverage
        self.account.margin_free = 100 * leverage
        self.profit = 0
        self.daily_profit = 0
        self.weekly_profit = 0
        self.mounthly_profit = 0
        self.seasonly_profit = 0
        self.yearly_profit = 0
        self.reset_trade_sim()       
        
    def reset_trade_sim(self):
        self.reset_balance()
        self.reset_order()
        self.reset_position()
        self.trade_mode = TRADE_SIM_MODE.IDLE
# Reset funcs ==============================================================================================================
# ==========================================================================================================================
    def reset_balance(self):
        self.account.balance = self.starting_cash
    def reset_order(self):
        self.order.reset() 
    def reset_position(self):
        self.position.reset()
# Market Order =============================================================================================================
# ==========================================================================================================================   
    def sim_send_order(self, request):
        self.update_trade_mode()
        if self.trade_mode == TRADE_SIM_MODE.IDLE:
            err_massage = self.send_order_error_handeling(request)
            if err_massage.retcode != 10009:
                return err_massage
            
            # pending orders
            if request['action'] == mt5.TRADE_ACTION_PENDING:
                self.order.type       = request['type']
                self.order.price_open = request['price']
                try:
                    self.order.sl         = request['sl']
                except:
                    pass
                try:
                    self.order.tp         = request['tp']
                except:
                    pass
                self.order.volume        = request['volume']
                self.order.magic      = request['magic']
            # Market Deal
            elif request['action'] == mt5.TRADE_ACTION_DEAL:
                assert False, "Market deal action types are not handeled yet"
                # TODO ...
        else:
            assert False, "send order called while mode is not IDLE"
        
        return err_massage
            
    def sim_remove_order(self):
        self.update_trade_mode()
        if self.trade_mode == TRADE_SIM_MODE.IN_ORDER:
            self.reset_order()
            self.trade_mode = TRADE_SIM_MODE.IDLE
    def sim_modify_order(self, entry, sl, tp):
        self.update_trade_mode()
        if self.trade_mode == TRADE_SIM_MODE.IN_ORDER:
            self.order_modify_error_handeling(entry, sl, tp)
            self.order.sl = sl
            self.order.tp = tp
            self.order.price_open = entry
        else:
            assert False, "modify order called while mode is not IN_ORDER"
    
    def tranfer_order_to_position_if_possible(self, ohlc_data):
        self.update_trade_mode()
        if self.trade_mode == TRADE_SIM_MODE.IN_ORDER:
            if self.order.type == mt5.ORDER_TYPE_BUY_STOP:
                if ohlc_data.high.iloc[-1] > self.order.price_open:
                    self.position = copy(self.order)
                    self.reset_order()
                    self.trade_mode = TRADE_SIM_MODE.IN_POSITION
                    self.account.balance -= self.position.price_open * (self.position.volume/self.account.leverage) * get_one_lot_in_dollar(self.name)
            elif self.order.type == mt5.ORDER_TYPE_BUY_LIMIT:
                pass # TODO:
            elif self.order.type == mt5.ORDER_TYPE_SELL_STOP:
                if ohlc_data.low.iloc[-1] < self.order.price_open:
                    self.position = copy(self.order)
                    self.reset_order()
                    self.account.balance -= self.position.price_open * (self.position.volume/self.account.leverage) * get_one_lot_in_dollar(self.name)
                    self.trade_mode = TRADE_SIM_MODE.IN_POSITION
            elif self.order.type == mt5.ORDER_TYPE_SELL_LIMIT:
                pass # TODO:
# Market position =========================================================================================================
# =========================================================================================================================          
    def sim_remove_position(self, ohlc_data, position_close_price):
        self.update_trade_mode()
        if self.trade_mode == TRADE_SIM_MODE.IN_POSITION:
            if self.position.type in self.buy_orders:
                self.account.balance += ((position_close_price - self.position.price_open) + position_close_price/self.account.leverage - self.broker_fee) * self.position.volume * get_one_lot_in_dollar(self.name)
            elif self.position.type in self.sell_orders:
                self.account.balance += ((-position_close_price + self.position.price_open) + position_close_price/self.account.leverage - self.broker_fee) * self.position.volume * get_one_lot_in_dollar(self.name)
            self.reset_position()
            self.trade_mode = TRADE_SIM_MODE.IDLE
    
    def sim_modify_position(self, sl, tp):
        self.update_trade_mode()
        if self.trade_mode == TRADE_SIM_MODE.IN_POSITION:
            self.modify_position_error_handeling(sl, tp)
            self.position.sl = sl
            self.position.tp = tp
        else:
            assert False, "modify position called while mode is not IN_POSITION"  
    
    def manage_sim_position(self, ohlc_data):
        self.update_trade_mode()
        #  Buy Position
        if self.position.type in self.buy_orders:
            if self.position.tp is not None and ohlc_data.high > self.position.tp:
                self.sim_remove_position(ohlc_data, self.position.tp)
            elif self.position.sl is not None and ohlc_data.low < self.position.sl:
                self.sim_remove_position(ohlc_data, self.position.sl)          
        # Sell position
        elif self.position.type in self.sell_orders:
            if self.position.sl is not None and ohlc_data.high > self.position.sl:
                self.sim_remove_position(ohlc_data, self.position.sl)
            elif self.position.tp is not None and ohlc_data.low < self.position.tp:
                self.sim_remove_position(ohlc_data, self.position.tp) 
# Trade ===================================================================================================================
# =========================================================================================================================
    def update_trade_mode(self):
        self.update_trade_mode_error_handeler()
        if self.order.type is not None:
            self.trade_mode = TRADE_SIM_MODE.IN_ORDER
        elif self.position.type is not None:
            self.trade_mode = TRADE_SIM_MODE.IN_POSITION
        else:
            self.trade_mode = TRADE_SIM_MODE.IDLE
# Info ===================================================================================================================
# ========================================================================================================================
    def sim_get_order(self):
        if self.order.type is None:
            return None
        else:
            return self.order
    def sim_get_position(self):
        if self.position.type is None:
            return None
        else:
            return self.position
    def sim_account_info(self):
        return self.account
    
# Error Handling =========================================================================================================
# ========================================================================================================================
    def order_modify_error_handeling(self, entry, sl, tp):
        pass
    def send_order_error_handeling(self, request):
        err = ErrorMassage()
        return err
    def modify_position_error_handeling(self, sl, tp):
        pass
    def update_trade_mode_error_handeler(self):
        pass