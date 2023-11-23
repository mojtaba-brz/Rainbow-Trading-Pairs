import numpy as np
# Local Imports =========================
from ConnectionWithMQL5.typedefs import *

# decoders ==============================================================================              
def default_decoder(data):
    temp = data.decode().split(',') # name, message type, message, END
    default_messages = np.array([], dtype=DefaultMessage)
    
    for i in range(1, len(temp), 4):
        name = temp[i]
        message_type = np.array(MESSAGE_TYPE)[int(temp[i+1])]
        message = temp[i+2]
        
        temp_default_message = DefaultMessage()
        temp_default_message.set_all(name, message_type, message)
        default_messages = np.append(default_messages, temp_default_message)
        
    return default_messages

def market_states_decoder(message):
# // 5m timeframe hlc  : high;low;close| 50 data
# // 30m timeframe hlc : high;low;close| 50 data
# // 4h timeframe hlc  : high;low;close| 50 data
# // 1d timeframe vol  : vol(0);vol(1);... 20 data| 
# // Indicators        : strength of left side currency in 6 other pairs; strength of right side currency in 7 other pairs; daily atr|
# // time              : day of week;hour|
# // robot status      : current position;current profit|
    
    messages_array = message.split('|')[:-1] 
    market_states = MarketStates()
    
    for x in messages_array[0:50]:
        market_states.append_hlc_rates_5m(tuple(x.split(';')))
    for x in messages_array[50:100]:
        market_states.append_hlc_rates_30m(tuple(x.split(';')))
    for x in messages_array[100:150]:
        market_states.append_hlc_rates_4h(tuple(x.split(';')))
    
    vols = messages_array[150].split(';')
    for x in vols:
        market_states.vol_1d = np.append(market_states.vol_1d, int(x))
    
    indicators = messages_array[151].split(';')
    for x in indicators[:6]:
        market_states.left_currency_strength = np.append(market_states.left_currency_strength, float(x))
    for x in indicators[6:12]:
        market_states.right_currency_strength = np.append(market_states.right_currency_strength, float(x))
    market_states.daily_atr = float(indicators[12])
    
    times = messages_array[152].split(';')
    market_states.day_of_week = int(times[0])
    market_states.hour = int(times[1])
    
    status = messages_array[153].split(';')
    market_states.current_position = np.array(POSITION_STATE)[int(status[0])]
    market_states.current_profit = float(status[1])
    
    reward_raw_string = messages_array[154].split(';')
    reward_raw_data = RewardRawData()
    reward_raw_data.ballance_diff = float(reward_raw_string[0])
    
    done = int(messages_array[155]) > 0.5
    
    return market_states, reward_raw_data, done

# =======================================================================================
# =======================================================================================
# Encoders ==============================================================================
# =======================================================================================
# =======================================================================================
def default_encoder(name, message_type, message):
    return f",{name},{message_type},{message},".encode('utf-8')