from datetime import date, datetime
import time
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import os

def add_days_of_the_week(df, start_day_index = None):
  
    n = len(df)
    df = pd.concat([df, pd.DataFrame({'day_of_week' : np.zeros(n, dtype=np.int8)})], axis=1)
    if start_day_index is None :
        augmented = False
        fri_index = -1
        for i in range(n-1):
            day = int(df.time.iloc[i].strftime("%d-%m-%Y, %H:%M:%S").split()[0].split("-")[0])
            next_day = int(df.time.iloc[i+1].strftime("%d-%m-%Y, %H:%M:%S").split()[0].split("-")[0])
            
            if (next_day - day < 0):
                next_day += day
                augmented = True
                
            if (next_day - day > 1):
                fri_index = i
                break
            
            if augmented:
                next_day -= day
                augmented = False

        day_index = 5-1    
        for i in range(fri_index,n):
            df.day_of_week.iloc[i] = day_index
            if i!= 0 and i < n-1 :
                day = int(df.time.iloc[i].strftime("%d-%m-%Y, %H:%M:%S").split()[0].split("-")[0])
                next_day = int(df.time.iloc[i+1].strftime("%d-%m-%Y, %H:%M:%S").split()[0].split("-")[0])
                if day != next_day:
                    day_index += 1
                    if day_index >= 5 :
                        day_index = 0
                
                
        day_index = 5-1  
        for i in range(fri_index,-1, -1):
            df.day_of_week.iloc[i] = day_index
            if i != fri_index and i > 1 :
                day = int(df.time.iloc[i].strftime("%d-%m-%Y, %H:%M:%S").split()[0].split("-")[0])
                pre_day = int(df.time.iloc[i+1].strftime("%d-%m-%Y, %H:%M:%S").split()[0].split("-")[0])
                if day != pre_day:
                    day_index -= 1
                    if day_index < 0 :
                        day_index = 5-1
    else:
        day_index = start_day_index
        for i in range(n):
            df.day_of_week.iloc[i] = day_index
            if i!= 0 and i < n-1 :
                day = int(df.time.iloc[i].strftime("%d-%m-%Y, %H:%M:%S").split()[0].split("-")[0])
                next_day = int(df.time.iloc[i+1].strftime("%d-%m-%Y, %H:%M:%S").split()[0].split("-")[0])
                if day != next_day:
                    day_index += 1
                    if day_index >= 5 :
                        day_index = 0    
    return df

def save_rates(symbol, time_frame_str, n = None):
    mt5.initialize()
    path = f"{__file__[:-23]}\\OHLC_Data\\{symbol}_{time_frame_str}.csv"
    month_dict = {"Dec" : 12, "Nov" : 11, "Oct" : 10, "Sep" : 9, "Aug" : 8, "Jul" : 7, "Jun" : 6, "May" : 5, "Apr" : 4, "Mar" : 3, "Feb" : 2, "Jan" : 1}
    current_time = time.ctime().split()
    current_year  = int(current_time[-1])
    current_month = month_dict[current_time[1]]
    current_day   = int(current_time[2])
    current_hour  = int(current_time[3].split(':')[0])
    current_min   = int(current_time[3].split(':')[1])
    current_sec   = int(current_time[3].split(':')[2])
    return_n_flag = False
    if time_frame_str == 'M5':
        time_frame = mt5.TIMEFRAME_M5
    elif time_frame_str == 'M30' :
        time_frame = mt5.TIMEFRAME_M30
    elif time_frame_str == 'M15' :
        time_frame = mt5.TIMEFRAME_M15
    elif time_frame_str == 'H1' :
        time_frame = mt5.TIMEFRAME_H1
    elif time_frame_str == 'H4' :
        time_frame = mt5.TIMEFRAME_H4
    elif time_frame_str == 'D1' :
        time_frame = mt5.TIMEFRAME_D1
    else :
        print(f"wrong Time Frame --> symbol : {symbol} , TF : {time_frame_str}")
        assert()
    if os.path.exists(path) :
        file = pd.read_csv(path)
        file.drop(columns=['Unnamed: 0'], inplace=True)
        start_day    = int(file.time.iloc[-1].split()[0].split("-")[2])-1
        start_mounth = int(file.time.iloc[-1].split()[0].split("-")[1])
        start_year   = int(file.time.iloc[-1].split()[0].split("-")[0])
        start_hour   = int(file.time.iloc[-1].split()[1].split(":")[0])
        start_min    = int(file.time.iloc[-1].split()[1].split(":")[1])
        start_sec    = int(file.time.iloc[-1].split()[1].split(":")[2])
        start_time = datetime(start_year, start_mounth, start_day, start_hour, start_min, start_sec)
        stop_time = datetime(current_year, current_month, current_day, current_hour, current_min, current_sec)
        rates = mt5.copy_rates_range(symbol, time_frame, start_time, stop_time)
        rates_frame = pd.DataFrame(rates)
        rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
        rates_frame_start_index = 0
        for i in range(len(rates_frame)):
            if rates_frame.time.iloc[i].strftime("%Y-%m-%d %H:%M:%S") == file.time.iloc[-1]:
                rates_frame_start_index = i
                break
        if(i > len(rates_frame)-5):
            return
        rates_frame = rates_frame.loc[rates_frame_start_index:].reset_index()
        rates_frame = add_days_of_the_week(rates_frame, file.day_of_week.iloc[-1])
        rates_frame = rates_frame.loc[1:].reset_index()
        rates_frame = pd.concat([file, rates_frame.drop(columns=['level_0'])]).reset_index().drop(columns=['level_0', 'index'])
    else:       
        if n is None :
            return_n_flag = True
            L = 1000;    n = 500
            while L >= n:
                n *= 2
                rates = mt5.copy_rates_from(symbol,
                                    time_frame,
                                    datetime(current_year, current_month, current_day),
                                    n)
                if rates is None:
                    print(f'MT5 returned None by this err : {mt5.last_error()}')
                    print(symbol,
                            time_frame,
                            datetime(current_year, current_month, current_day, current_hour, current_min, current_sec),
                            n)
                    n //= 2
                    rates = mt5.copy_rates_from(symbol,
                                    time_frame,
                                    datetime(current_year, current_month, current_day, current_hour, current_min, current_sec),
                                    n)
                    break
                else:
                    L = len(rates)            
        else :
            rates = mt5.copy_rates_from(symbol,
                                        time_frame,
                                        datetime(current_year, current_month, current_day, current_hour, current_min, current_sec),
                                        n)
        if (rates is None):
            print(f"rates is None for {symbol}_{time_frame_str}")
            assert()
        rates_frame = pd.DataFrame(rates)
        rates_frame['time']=pd.to_datetime(rates_frame['time'], unit='s')
        rates_frame = add_days_of_the_week(rates_frame)
    rates_frame = time_decomposition(rates_frame)
    rates_frame.to_csv(path)
    if return_n_flag is True:
        return n
    
def time_decomposition(df):
    if type(df.time.iloc[0]) is str:
        years   = np.array([int(x.split()[0].split('-')[0]) for x in df.time])
        mounths = np.array([int(x.split()[0].split('-')[1]) for x in df.time])
        days    = np.array([int(x.split()[0].split('-')[2]) for x in df.time])
        n = len(df.time.iloc[0].split())
        if n > 1:
            hours   = np.array([int(x.split()[1].split(':')[0]) for x in df.time])
            mins    = np.array([int(x.split()[1].split(':')[1]) for x in df.time])
            secs    = np.array([int(x.split()[1].split(':')[2]) for x in df.time])
        else:
            n = len(df.time)
            hours   = np.zeros(n, dtype=np.int8)
            mins    = np.zeros(n, dtype=np.int8)
            secs    = np.zeros(n, dtype=np.int8)
    else:
        years   = np.array([int(x.strftime("%Y-%m-%d %H:%M:%S").split()[0].split('-')[0]) for x in df.time])
        mounths = np.array([int(x.strftime("%Y-%m-%d %H:%M:%S").split()[0].split('-')[1]) for x in df.time])
        days    = np.array([int(x.strftime("%Y-%m-%d %H:%M:%S").split()[0].split('-')[2]) for x in df.time])
        hours   = np.array([int(x.strftime("%Y-%m-%d %H:%M:%S").split()[1].split(':')[0]) for x in df.time])
        mins    = np.array([int(x.strftime("%Y-%m-%d %H:%M:%S").split()[1].split(':')[1]) for x in df.time])
        secs    = np.array([int(x.strftime("%Y-%m-%d %H:%M:%S").split()[1].split(':')[2]) for x in df.time])
    return pd.concat([df, pd.DataFrame({'year' : years, 'mounth': mounths, 'day':days, 'hour':hours, 'minute':mins, 'second':secs})], axis=1)

def gather_ohlc_data(my_target_symbols = None) :
    
    if type(my_target_symbols) is not list and my_target_symbols is not None:
        print(f"\nmy_target_symbols must be a list or None\n===========================\n")
        assert()
    if(not mt5.terminal_info()):
        if mt5.initialize():
            print("MetaTrader 5 Initialized succesfully")
        else:
            print("initialize() failed, error code =",mt5.last_error())
            quit()
    if my_target_symbols is None :
        my_targets = ["USD", "EUR", "JPY","GBP", "AUD", "NZD", "CHF", "CAD"]
        group_symbols = mt5.symbols_get(group="*USD*,*EUR*,*JPY*,*GBP*, *AUD*, *NZD*, *CHF*, *CAD*, !*CFD*, !*i")

        my_target_symbols = []
        for symbol in group_symbols:
            if (len(symbol.name) == 6 and symbol.name[0:3] in my_targets and symbol.name[3:6] in my_targets):
                my_target_symbols += [symbol.name]       
    ### Start Gathering
    for symbol in my_target_symbols:
        # M5 TimeFrame
        n = save_rates(symbol, 'M5')

        # M15 TimeFrame
        save_rates(symbol, 'M15', n)
    
        # M30 TimeFrame
        save_rates(symbol, 'M30', n)
    
        # H1 TimeFrame
        save_rates(symbol, 'H1', n)

        # H4 TimeFrame
        save_rates(symbol, 'H4', n)
        
        # D1 TimeFrame
        save_rates(symbol, 'D1', n)
        
if __name__ == '__main__':
    gather_ohlc_data()

    