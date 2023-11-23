import MetaTrader5 as mt5
import pandas as pd
import time
from datetime import datetime 
from enum import Enum

market_open_time = time.struct_time((0, 0, 0, 22, 0, 0, 6, 0, 0))

market_close_time = time.struct_time((0, 0, 0, 22, 0, 0, 4, 0, 0))

def find_low_spread_pairs(spread_limit):
    if(not mt5.terminal_info()):
        if mt5.initialize():
            print("MetaTrader 5 Initialized succesfully")
        else:
            print("initialize() failed, error code =",mt5.last_error())
            quit()

    my_targets = ["USD", "EUR", "JPY","GBP", "AUD", "NZD", "CHF", "CAD"]
    group_symbols = mt5.symbols_get(group="*USD*,*EUR*,*JPY*,*GBP*, *AUD*, *NZD*, *CHF*, *CAD*, !*CFD*, !*i")

    my_target_symbol_names = []
    for symbol in group_symbols:
        if (len(symbol.name) == 6 and symbol.name[0:3] in my_targets and symbol.name[3:6] in my_targets and symbol.spread < spread_limit):
            my_target_symbol_names += [symbol.name]
    return my_target_symbol_names

def get_rates(symbol, number_of_data = 100, timeframe=mt5.TIMEFRAME_M5):
    mt5.initialize()
    # Compute now date
    month_dict = {"Dec" : 12, "Nov" : 11, "Oct" : 10, "Sep" : 9, "Aug" : 8, "Jul" : 7, "Jun" : 6, "May" : 5, "Apr" : 4, "Mar" : 3, "Feb" : 2, "Jan" : 1}
    current_time = time.ctime().split()
    current_year  = int(current_time[-1])
    current_month = month_dict[current_time[1]]
    current_day   = int(current_time[2])
    
    # Extract n Ticks before now
    rates = mt5.copy_rates_from(symbol, timeframe, datetime(current_year+1, current_month, current_day), number_of_data) # yaer + 1 to ensure to get most recent data
    rates = rates[:-1] # last candle is not closed yet

    # Transform Tuple into a DataFrame
    df_rates = pd.DataFrame(rates)

    # Convert number format of the date into date format
    df_rates["time"] = pd.to_datetime(df_rates["time"], unit="s")
    
    return df_rates

def remove_all_orders():
    mt5.initialize()
    time_out_counter = 0
    while(mt5.orders_total() > 0):
        orders = mt5.orders_get()
        if(orders == None):
            mt5.initialize()
            orders = mt5.orders_get()
        if(orders != None or orders != ()):
            for order in orders:
                order_remove(order)
        if(time_out_counter > 10):
            return
        time_out_counter += 1
        
            
def order_remove(order):
    request = {
        "action" : mt5.TRADE_ACTION_REMOVE,
        "order"  : order.ticket
        }
    order_send_info = mt5.order_send(request)
    if(order_send_info.retcode == 10013):
        print(order.symbol)
    else:
        print(order_send_info.comment)

def close_all_positions():
    mt5.initialize()
    time_out_counter = 0
    while(mt5.positions_total() > 0):
        positions = mt5.positions_get()
        if(positions == None):
            mt5.initialize()
            positions = mt5.positions_get()
        if(positions != None or positions != ()):
            for position in positions:
                close_position(position)
        if(time_out_counter > 10):
            return
        time_out_counter += 1

def close_position(position):
    request = {
        "position"  : position.ticket,
        "symbol" : position.symbol,
        "volume" : position.volume,
        "action" : mt5.TRADE_ACTION_DEAL,
        "deviation" : 5,
    }
    if(is_buy_position(position)):
        request["type"]   = mt5.ORDER_TYPE_SELL
        request["price"]  = mt5.symbol_info(position.symbol).bid
    else:
        request["type"] = mt5.ORDER_TYPE_BUY
        request["price"]  = mt5.symbol_info(position.symbol).ask
        
    order_send_info = mt5.order_send(request)
    if(order_send_info.retcode == 10013):
        print(order_send_info)
        print("\n")
        print(request)
        print("\n")
    else:
        print(order_send_info.comment)
    
def is_buy_position(position):
    sl = position.sl
    tp = position.tp
    price_open = position.price_open
    price = position.price_current
    profit = position.profit
    if((sl != 0 and sl < price_open) or
        (tp != 0 and tp > price_open) or
        (price_open > price and profit < 0) or
        (price_open < price and profit > 0)):
        return True
    else:
        return False

def modify_order(order, price = -1, sl = -1, tp = -1):
    mt5.initialize()
    request = {
        "position" : order.ticket,
        "order" : order.ticket,
        "price" : order.price_open * (price == -1) + price * (price != -1),
        "sl" : order.sl * (sl == -1) + sl * (sl != -1),
        "tp" : order.tp * (tp == -1) + tp * (tp != -1),
        "action" : mt5.TRADE_ACTION_MODIFY,
        "volume" : order.volume_current,
        "symbol" : order.symbol
    }
    return mt5.order_send(request)

def modify_position(position, sl = -1, tp = -1):
    mt5.initialize()
    request = {
        "position" : position.ticket,
        "sl" : position.sl * (sl == -1) + sl * (sl != -1),
        "tp" : position.tp * (tp == -1) + tp * (tp != -1),
        "action" : mt5.TRADE_ACTION_SLTP
    }
    return mt5.order_send(request)

def get_orders(symbol):
    mt5.initialize()
    return mt5.orders_get(symbol = symbol)
def get_positions(symbol):
    mt5.initialize()
    return mt5.positions_get(symbol = symbol)

def get_bid(symbol):
    return mt5.symbol_info(symbol).bid
def get_ask(symbol):
    return mt5.symbol_info(symbol).ask

def account_info():
    return mt5.account_info()

def send_order(request):
    return mt5.order_send(request)

def get_symbol_info(symbol):
    return mt5.symbol_info(symbol)

def market_connection_status():
    return mt5.initialize()

def market_last_error():
    return mt5.last_error()

def get_spread(symbol_name):
    mt5.initialize()
    return mt5.symbol_info(symbol_name).spread