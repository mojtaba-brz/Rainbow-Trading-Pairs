import matplotlib.pyplot as ax
from datetime import datetime

index_of_figures = 1

def draw_candle_stick(stock_prices, ax):
    # ref : https://www.geeksforgeeks.org/how-to-create-a-candlestick-chart-in-matplotlib/
    # with some improvements and adaptation
    # stock_prices : ohlc dataframe including ohlc data + time
    # ax : axes of candle stick chart
    
    if type(stock_prices.time.loc[0]) is str:
        n = len(stock_prices.time.loc[0].split())
        if n > 1:
            stock_prices.index = [datetime(int(x.split()[0].split("-")[0]), 
                                        int(x.split()[0].split("-")[1]), 
                                        int(x.split()[0].split("-")[2]),
                                        int(x.split()[1].split(":")[0]), 
                                        int(x.split()[1].split(":")[1]),
                                        int(x.split()[1].split(":")[2])) 
                                for x in stock_prices.time]
        else:    
            stock_prices.index = [datetime(int(x.split()[0].split("-")[0]), 
                                        int(x.split()[0].split("-")[1]), 
                                        int(x.split()[0].split("-")[2])) 
                                for x in stock_prices.time]
    else:
        stock_prices.index = stock_prices.time
    
    x = stock_prices.index[1]-stock_prices.index[0]   
    x = str(x).split()
    day = int(x[0])
    c = 1
    if day == 0:
        hour = int(x[2].split(':')[0])
        if hour == 4:
            c = 1./6
        elif hour == 1:
            c = 1./24
        else:
            minute = int(x[2].split(':')[1])
            if minute == 30:
                c = 1./48
            elif minute == 15:
                c = 1./(48*2)
            elif minute == 5:
                c = 1./(48*2*3)
    # "up" dataframe will store the stock_prices 
    # when the closing stock price is greater
    # than or equal to the opening stock prices
    up = stock_prices[stock_prices.close >= stock_prices.open]
    
    # "down" dataframe will store the stock_prices
    # when the closing stock price is
    # lesser than the opening stock prices
    down = stock_prices[stock_prices.close < stock_prices.open]
    
    # When the stock prices have decreased, then it
    # will be represented by
    col1 = 'blue'
    
    # When the stock prices have increased, then it 
    # will be represented by 
    col2 = 'red'
    
    # Setting width of candlestick elements
    width = .3*c
    width2 = .03*c
    
    # Plotting up prices of the stock
    ax.bar(up.index, up.close-up.open, width, bottom=up.open, color=col1)
    ax.bar(up.index, up.high-up.close, width2, bottom=up.close, color=col1)
    ax.bar(up.index, up.low-up.open, width2, bottom=up.open, color=col1)
    
    # Plotting down prices of the stock
    ax.bar(down.index, down.close-down.open, width, bottom=down.open, color=col2)
    ax.bar(down.index, down.high-down.open, width2, bottom=down.open, color=col2)
    ax.bar(down.index, down.low-down.close, width2, bottom=down.close, color=col2)
    
    # rotating the x-axis tick labels towards right
    ax.set_xticks(rotation=60, ha='right')

def draw_candle_stick_by_index(stock_prices, ax):
    # ref : https://www.geeksforgeeks.org/how-to-create-a-candlestick-chart-in-matplotlib/
    # with some improvements and adaptation
    # "up" dataframe will store the stock_prices 
    # when the closing stock price is greater
    # than or equal to the opening stock prices
    up = stock_prices[stock_prices.close >= stock_prices.open]
    
    # "down" dataframe will store the stock_prices
    # when the closing stock price is
    # lesser than the opening stock prices
    down = stock_prices[stock_prices.close < stock_prices.open]
    
    # When the stock prices have decreased, then it
    # will be represented by
    col1 = 'blue'
    
    # When the stock prices have increased, then it 
    # will be represented by 
    col2 = 'red'
    
    # Setting width of candlestick elements
    width = .5
    width2 = width/5
    
    # Plotting up prices of the stock
    ax.bar(up.index, up.close-up.open, width, bottom=up.open, color=col1)
    ax.bar(up.index, up.high-up.close, width2, bottom=up.close, color=col1)
    ax.bar(up.index, up.low-up.open, width2, bottom=up.open, color=col1)
    
    # Plotting down prices of the stock
    ax.bar(down.index, down.close-down.open, width, bottom=down.open, color=col2)
    ax.bar(down.index, down.high-down.open, width2, bottom=down.open, color=col2)
    ax.bar(down.index, down.low-down.close, width2, bottom=down.close, color=col2) 

def write_text_on_chart_by_index(text, location, ax):
    # note: ax must contain a graph
    # texts : should be a string
    #
    # location : must be "left" or "right"
    # 
    # ax : axes
    if location == "left":
        ax.text(ax.get_xbound()[0], ax.get_ybound()[1], text)
    elif location == "right":
        ax.text(ax.get_xbound()[1], ax.get_ybound()[1], text)
    else:
        assert False, "location must be left or right"

def draw_order_on_chart_by_index(order, ax):
    x = ax.get_xbound()
    sl = (order.sl, order.sl)
    tp = (order.tp, order.tp)
    price_open = (order.price_open, order.price_open)
    
    ax.plot(x, sl, c='r')
    ax.plot(x, tp, c='g')
    ax.plot(x, price_open, c='b')