import numpy as np


def there_is_a_up_fractal_there(df_rates, i):
    return (df_rates.high[i] >= df_rates.high[i+1] and 
            df_rates.high[i] >= df_rates.high[i+2] and 
            df_rates.high[i] >= df_rates.high[i-1] and 
            df_rates.high[i] >= df_rates.high[i-2])
def there_is_a_down_fractal_there(df_rates, i):
    return (df_rates.low[i] <= df_rates.low[i+1] and 
            df_rates.low[i] <= df_rates.low[i+2] and 
            df_rates.low[i] <= df_rates.low[i-1] and 
            df_rates.low[i] <= df_rates.low[i-2])
def get_up_fractals_from_df(df_rates):
    x = []
    y = []
    for i in range(len(df_rates)):
        if i < 2 or i > len(df_rates)-1-2:
            pass
        elif there_is_a_up_fractal_there(df_rates, i):
            y += [df_rates.high.iloc[i]*1.00015]
            x += [df_rates.index[i]]
    return np.array(x), np.array(y)
def get_down_fractals_from_df(df_rates):
    x = []
    y = []
    for i in range(len(df_rates)):
        if i < 2 or i > len(df_rates)-1-2:
            pass
        elif there_is_a_down_fractal_there(df_rates, i):
            y += [df_rates.low.iloc[i]*0.99985]
            x += [df_rates.index[i]]
    return np.array(x), np.array(y)

def plot_fractals_for_a_df_by_index(df_rates, ax):
    up_index, up_fractals = get_up_fractals_from_df(df_rates)
    down_index, down_fractals = get_down_fractals_from_df(df_rates)
    
    ax.scatter(up_index, up_fractals, marker = '^', c='g')
    ax.scatter(down_index, down_fractals, marker = 'v', c='orange')