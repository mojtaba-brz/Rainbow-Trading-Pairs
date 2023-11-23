import MetaTrader5 as mt5

from MarketTerndID.TrendParams import TREND
from TR_Bots.TRBotsParams import Modes
from Simulator.MarketSim.MarketSim import PairSimulator, TradeSim
from Market.MarketTools import *

class BotsCommonClass(PairSimulator, TradeSim):
    big_value = 100000000000
# ===========================================================================================================================================
# ======================================================= Main Functions ==================================================================== 
# ===========================================================================================================================================    
    def __init__(self):
        ##### Warning ####### this should be called in each bot ############## Warning #####################
# ====================================================================================================================================
# ============================================== Constants and Initializations =======================================================
# ====================================================================================================================================
    # variables
        self.order_status = None 
        self.robot_id = None #### Warning ######## this should be defined in each bot ################### Warning ################
        self.main_data_frame = None #### Warning ######## this should be defined in each bot ################### Warning ################
        # dictionaries
        self.trend            = {'real':TREND.UNKNOWN, 'sim':TREND.UNKNOWN}
        self.m30_trend_canlde = {'real':None, 'sim':None}
        self.mode             = {'real':Modes.UNKNOWN, 'sim':Modes.UNKNOWN}
        self.sell_stop_pos    = {'real':-1, 'sim':-1}
        self.buy_stop_pos     = {'real':-1, 'sim':-1}
        self.buy_stop_SL_pos  = {'real':-1, 'sim':-1}
        self.sell_stop_SL_pos = {'real':-1, 'sim':-1}
        self.buy_stop_TP_pos  = {'real':-1, 'sim':-1}
        self.sell_stop_TP_pos = {'real':-1, 'sim':-1}
        self.order_status     = {'real':-1, 'sim':-1}
        #lists
        self.ban_modes = None ##### Warning ####### this should be defined in each bot ############## Warning #####################
    def reset(self):
        ##### Warning ####### this should be defined in each bot ############## Warning #####################
        pass
    def step(self):
        ##### Warning ####### this should be defined in each bot ############## Warning #####################
        pass
# ===========================================================================================================================================
# ===================================================== Utility Functions =================================================================== 
# ===========================================================================================================================================   
    def there_is_no_more_than_one_order_or_position(self):
        counter = 0
        for order in get_orders(self.name):
            if order.magic == self.robot_id:
                counter += 1
        for position in get_positions(self.name):
            if position.magic == self.robot_id:
                counter += 1
        if(counter > 1):
            print("check", self.name,". more than one order or position have found.")
            return False
        else:
            return True
    
    def take_my_order(self):
        call_mode = 'real' #only
        myOrder = self.get_my_order()
        if myOrder != ():
            if myOrder.type == mt5.ORDER_TYPE_BUY_STOP:
                self.mode[call_mode] = Modes.BUY_PENDING_ORDER
                self.trend[call_mode] = TREND.UP_TREND
                self.sell_stop_pos[call_mode] = -1
                self.buy_stop_pos[call_mode] = myOrder.price_open
                self.buy_stop_SL_pos[call_mode] = -int(myOrder.sl == 0) + myOrder.sl
                self.sell_stop_SL_pos[call_mode] = -1
                self.buy_stop_TP_pos[call_mode] = -int(myOrder.tp == 0) + myOrder.tp
                self.sell_stop_TP_pos[call_mode] = -1
            elif myOrder.type == mt5.ORDER_TYPE_SELL_STOP:
                self.mode[call_mode] = Modes.SELL_PENDING_ORDER
                self.trend[call_mode] = TREND.DOWN_TREND
                self.sell_stop_pos[call_mode] = myOrder.price_open
                self.buy_stop_pos[call_mode] = -1
                self.buy_stop_SL_pos[call_mode] = -1
                self.sell_stop_SL_pos[call_mode] = -int(myOrder.sl == 0) + myOrder.sl
                self.buy_stop_TP_pos[call_mode] = -1
                self.sell_stop_TP_pos[call_mode] = -int(myOrder.tp == 0) + myOrder.tp
            else:
                print("check", self.name,". Order Type Error")
        
    def take_my_position(self):
        call_mode = 'real' #only
        myPosition = self.get_my_position()
        if myPosition != ():
            if myPosition.type == mt5.POSITION_TYPE_BUY:
                self.mode[call_mode] = Modes.MANAGE_LONG_POSITION
                self.trend[call_mode] = TREND.UP_TREND
                self.sell_stop_pos[call_mode] = -1
                self.buy_stop_pos[call_mode] = myPosition.price_open
                self.buy_stop_SL_pos[call_mode] = -int(myPosition.sl == 0) + myPosition.sl
                self.sell_stop_SL_pos[call_mode] = -1
                self.buy_stop_TP_pos[call_mode] = -int(myPosition.tp == 0) + myPosition.tp
                self.sell_stop_TP_pos[call_mode] = -1
            elif myPosition.type == mt5.POSITION_TYPE_SELL:
                self.mode[call_mode] = Modes.MANAGE_SHORT_POSITION
                self.trend[call_mode] = TREND.DOWN_TREND
                self.sell_stop_pos[call_mode] = myPosition.price_open
                self.buy_stop_pos[call_mode] = -1
                self.buy_stop_SL_pos[call_mode] = -1
                self.sell_stop_SL_pos[call_mode] = -int(myPosition.sl == 0) + myPosition.sl
                self.buy_stop_TP_pos[call_mode] = -1
                self.sell_stop_TP_pos[call_mode] = -int(myPosition.tp == 0) + myPosition.tp
            else:
                print("check", self.name,". Position Type Error")
        
    def remove_my_orders(self, call_mode = 'real'):
        if call_mode == 'sim':
            self.sim_remove_order()
        else:
            orders = get_orders(self.name)
            for order in orders:
                if(order.magic == self.robot_id):
                    order_remove(order)
        
    def close_my_posiitons(self, call_mode = 'real'):
        if call_mode == 'sim':
            self.sim_remove_position(self.main_data_frame, self.sim_get_ask())
        else:
            positions = get_positions(self.name)
            for position in positions:
                if(position.magic == self.robot_id):
                    close_position(position)
    
    def there_is_only_one_position(self):
        positions = get_positions(self.name)
        counter = 0
        for position in positions:
            if position.magic == self.robot_id:
                counter += 1
        if(counter == 1):
            return True
        else:
            print("there are more than one position in", self.name)
            return False
    
    def in_a_position(self, call_mode = 'real'):
        if call_mode == 'sim' :
            positions = self.sim_get_position()
        else:
            positions = get_positions(self.name)
        if(positions != () and positions is not None):
            if(self.mode[call_mode] == Modes.BUY_PENDING_ORDER):
                self.mode[call_mode] = Modes.MANAGE_LONG_POSITION
            else:
                self.mode[call_mode] = Modes.MANAGE_SHORT_POSITION
            return True
        return False

    def get_my_order(self, call_mode = 'real'):
        if self.there_is_no_more_than_one_order_or_position():
            for order in get_orders(self.name):
                if order.magic == self.robot_id:
                    return order
    
    def manage_sell_order(self, call_mode = 'real'):
        if(self.sell_stop_pos[call_mode] > 0 and 
           self.sell_stop_SL_pos[call_mode] < self.big_value and
           self.sell_stop_SL_pos[call_mode] > 0):
            
            if call_mode == 'sim':
                my_order = self.sim_get_order()
                balance  = self.sim_account_info().balance
            else:
                my_order = self.get_my_order()
                balance = account_info().balance
            if self.in_a_position(call_mode):
                pass
            elif my_order == () or my_order == None:
                if call_mode == 'sim':
                    request = {
                        "action"       : mt5.TRADE_ACTION_PENDING,
                        "magic"        : self.robot_id,
                        "symbol"       : self.name,
                        "volume"       : int(balance/100)/100.,
                        "price"        : self.sell_stop_pos[call_mode],
                        "sl"           : self.sell_stop_SL_pos[call_mode],
                        "deviation"    : 5,
                        "type"         : mt5.ORDER_TYPE_SELL_STOP,
                        "type_time"    : mt5.ORDER_TIME_GTC,
                    }
                    self.sim_send_order(request)
                else:
                    request = {
                        "action"       : mt5.TRADE_ACTION_PENDING,
                        "magic"        : self.robot_id,
                        "symbol"       : self.name,
                        "volume"       : int(balance/100)/100.,
                        "price"        : self.sell_stop_pos[call_mode],
                        "sl"           : self.sell_stop_SL_pos[call_mode],
                        "deviation"    : 5,
                        "type"         : mt5.ORDER_TYPE_SELL_STOP,
                        "type_filling" : get_symbol_info(self.name).filling_mode,
                        "type_time"    : mt5.ORDER_TIME_GTC,
                        "position"     : 0,
                        "position_by"  : 0,
                    }
                    self.order_status[call_mode] = send_order(request)


            elif(self.sell_stop_SL_pos[call_mode] != my_order.sl or
                 self.sell_stop_pos[call_mode] != my_order.price_open or
                 self.sell_stop_TP_pos[call_mode] != my_order.tp):
                if call_mode == 'sim':
                    self.sim_modify_order(self.sell_stop_pos[call_mode], self.sell_stop_SL_pos[call_mode], self.sell_stop_TP_pos[call_mode])
                else:
                    self.order_status[call_mode] = modify_order(my_order, self.sell_stop_pos[call_mode], self.sell_stop_SL_pos[call_mode], self.sell_stop_TP_pos[call_mode])
                if(self.order_status[call_mode].retcode != 10009):
                    print(self.name, self.order_status[call_mode].comment)
                    print("order status :\n", self.order_status[call_mode], "\n")
                    print("current order :\n", self.get_my_order(), "\n")
            
    def manage_buy_order(self, call_mode = 'real'):
        if(self.buy_stop_SL_pos[call_mode] > 0 and 
           self.buy_stop_pos[call_mode] < self.big_value and
           self.buy_stop_pos[call_mode] > 0):
            if call_mode == 'sim':
                my_order = self.sim_get_order()
                balance  = self.sim_account_info().balance
            else:
                my_order = self.get_my_order()
                balance = account_info().balance
            if self.in_a_position(call_mode):
                pass
            elif my_order == () or my_order is None:
                if call_mode == 'sim':
                    request = {
                        "action"       : mt5.TRADE_ACTION_PENDING,
                        "magic"        : self.robot_id,
                        "symbol"       : self.name,
                        "volume"       : int(balance/100)/100.,
                        "price"        : self.buy_stop_pos[call_mode],
                        "sl"           : self.buy_stop_SL_pos[call_mode],
                        "deviation"    : 5,
                        "type"         : mt5.ORDER_TYPE_BUY_STOP,
                        "type_time"    : mt5.ORDER_TIME_GTC,
                    }
                    self.order_status[call_mode] = self.sim_send_order(request)
                else:
                    request = {
                        "action"       : mt5.TRADE_ACTION_PENDING,
                        "magic"        : self.robot_id,
                        "symbol"       : self.name,
                        "volume"       : int(balance/100)/100.,
                        "price"        : self.buy_stop_pos[call_mode],
                        "sl"           : self.buy_stop_SL_pos[call_mode],
                        "deviation"    : 5,
                        "type"         : mt5.ORDER_TYPE_BUY_STOP,
                        "type_filling" : get_symbol_info(self.name).filling_mode,
                        "type_time"    : mt5.ORDER_TIME_GTC,
                        "position"     : 0,
                        "position_by"  : 0,
                    }
                    self.order_status[call_mode] = send_order(request)
                
            elif(self.buy_stop_SL_pos[call_mode] != my_order.sl or
                self.buy_stop_pos[call_mode] != my_order.price_open or
                self.buy_stop_TP_pos[call_mode] != my_order.tp):
                if call_mode == 'sim':
                    self.sim_modify_order(self.buy_stop_pos[call_mode], self.buy_stop_SL_pos[call_mode], self.buy_stop_TP_pos[call_mode])
                else:
                    self.order_status[call_mode] = modify_order(my_order, self.buy_stop_pos[call_mode], self.buy_stop_SL_pos[call_mode], self.buy_stop_TP_pos[call_mode])  
                if(self.order_status[call_mode].retcode != 10009):
                    print(self.name, self.order_status[call_mode].comment)
                    print("order status :\n", self.order_status[call_mode], "\n")
                    print("current order :\n", self.get_my_order(), "\n")
                    
    def get_my_position(self, call_mode = 'real'):
        if self.there_is_no_more_than_one_order_or_position():
            for position in get_positions(self.name):
                if position.magic == self.robot_id:
                    return position
                  
    def manage_short_position(self, call_mode = 'real'):
        if call_mode == 'sim':
            my_pos = self.sim_get_position()
        else:
            my_pos = self.get_my_position()
        if(my_pos == () or my_pos is None):
            self.reset(call_mode)
            print(self.name, "reseted !  (manage short pos step)")
        elif(self.sell_stop_SL_pos[call_mode] < my_pos.sl or
             self.sell_stop_TP_pos[call_mode] != my_pos.tp):
            if call_mode == 'sim':
                self.sim_modify_position(self.sell_stop_SL_pos[call_mode], self.sell_stop_TP_pos[call_mode])
            else:
                modify_position(self.get_my_position(), self.sell_stop_SL_pos[call_mode], self.sell_stop_TP_pos[call_mode])
    def manage_long_position(self, call_mode = 'real'):
        if call_mode == 'sim':
            my_pos = self.sim_get_position()
        else:
            my_pos = self.get_my_position()
        if(my_pos == () or my_pos == None):
            self.reset(call_mode)
            print(self.name, "reseted !  (manage long pos step)")
        elif(self.buy_stop_SL_pos[call_mode] > my_pos.sl or
             self.buy_stop_TP_pos[call_mode] != my_pos.tp):
            if call_mode == 'sim':
                self.sim_modify_position(self.buy_stop_SL_pos[call_mode], self.buy_stop_TP_pos[call_mode])
            else:
                modify_position(self.get_my_position(), self.buy_stop_SL_pos[call_mode], self.buy_stop_TP_pos[call_mode])   