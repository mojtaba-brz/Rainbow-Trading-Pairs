//+------------------------------------------------------------------+
//|                                                TimeUtils.mqh.mq5 |
//|                                  Copyright 2023, MetaQuotes Ltd. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property library
#property copyright "Copyright 2023, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
int current_candle_time_sec(string symbol = NULL, ENUM_TIMEFRAMES period = PERIOD_CURRENT)
  {
   if(symbol == NULL)
      symbol = Symbol();

   datetime time[1];
   CopyTime(Symbol(), PERIOD_CURRENT, 0, 1, time);

   return (int)time[0];
  }
//+------------------------------------------------------------------+
