import MetaTrader5 as mt5
from TR_Bots.BSF_Bot import BSF_Class, print_header
from Market.MarketTools import find_low_spread_pairs
from threading import Thread

mt5.initialize()
# symbol_names = find_low_spread_pairs(spread_limit = 2000)

symbol_names = [x.name for x in mt5.symbols_get(group="*USD*,*EUR*,*JPY*,*GBP*, *AUD*, *NZD*, *CHF*, *CAD*, !*CFD*, !*i, !*X*")]
# symbol_names = [x.name for x in mt5.symbols_get(group="*GBPU*, !*CFD*, !*i")]
BSF_array = []      

for symbol in symbol_names:
    if (symbol not in [x.name for x in BSF_array]):
        BSF_array += [BSF_Class(symbol)]
                     
Thread(target = print_header).start()
for bot in BSF_array:
    Thread(target = bot.run).start()