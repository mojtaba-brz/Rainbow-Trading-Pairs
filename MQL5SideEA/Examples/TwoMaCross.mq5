//+------------------------------------------------------------------+
//|                                                   TwoMaCross.mq5 |
//|                                  Copyright 2023, MetaQuotes Ltd. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2023, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"

#include "../TrBotClient.mqh"
#include "../TimeUtils.mqh"

//--- input parameters
input int magic_number = 12345;
input int      SlowMaPeriod = 10;
input int      FastMaPeriod = 5;

TrBotClient tbc("Mql MA Cross Example", "127.0.0.1", 65333);

// Flags ===============================================
static bool params_sent = false;
static bool new_candle = true;
static bool rates_sent = false;
static bool action_recived = false;
// =====================================================
static int pre_time = 0, current_time;
static TR_ACTIONS action = DO_NOTHING;
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
//---
   Comment("TwoMaCross EA Example is Running\n"+
           "make sure that python side program is running\n"+
           "\nDate Of Development: 14/4/2023");

   params_sent = tbc.send_message_to_server(ALGO_PARAMS, IntegerToString(SlowMaPeriod)+";"+IntegerToString(FastMaPeriod));
//---
   return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
//---
   Comment("");
  }
//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
//---
   current_time = current_candle_time_sec();
   new_candle = current_time > pre_time;
   pre_time = current_time;

   if(!params_sent)
      params_sent = tbc.send_message_to_server(ALGO_PARAMS, IntegerToString(SlowMaPeriod)+";"+IntegerToString(FastMaPeriod));
   else
      if(new_candle || !rates_sent)
        {
         rates_sent = tbc.send_market_states(Symbol(), magic_number, SlowMaPeriod);
         if (rates_sent) action_recived = false;
        }
   if(new_candle && rates_sent && !action_recived)
     {
      action = tbc.get_last_action(action_recived);

      if(action_recived)
        {
         printf("%i", action);
        }
     }


  }
//+------------------------------------------------------------------+
