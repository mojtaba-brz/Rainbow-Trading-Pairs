//+------------------------------------------------------------------+
//|                                                  MessagesLib.mqh |
//|                                  Copyright 2023, MetaQuotes Ltd. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2023, MetaQuotes Ltd."
#property link      "https://www.mql5.com"

#include "typedefs.mqh"

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
int encode_default_massage(const string name, const MESSAGE_TYPE message_type, string message, uchar &data[])
  {
   message = "," + name + "," + IntegerToString(message_type) + "," + message + ",";
   return StringToCharArray(message, data);
  }
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
string encode_market_states_and_reward(MarketStates &states, RewardRawData &reward_raw_data, int done)
  {
// 5m timeframe hlc  : high;low;close| 50 data
// 30m timeframe hlc : high;low;close| 50 data
// 4h timeframe hlc  : high;low;close| 50 data
// 1d timeframe vol  : vol(0);vol(1);...| 20 data
// Indicators        : strength of left side currency in 7 other pairs; strength of right side currency in 7 other pairs; daily atr|
// time              : day of week;hour|
// robot status      : current position;current profit|
// reward            : ballance difference|

   string hlc_5m = "", hlc_30m = "", hlc_4h = "", vol_1d = "", indicators_data = "", time_data = "", robot_status = "", message = "";

   for(int i = 0; i<50; i++)
     {
      // 5m timeframe hlc  : high;low;close| 50 data
      // 30m timeframe hlc : high;low;close| 50 data
      // 4h timeframe hlc  : high;low;close| 50 data
      // 1d timeframe vol  : vol(0);vol(1);...| 20 data
      hlc_5m += DoubleToString(states.rates_5m[i].high) + ";" + DoubleToString(states.rates_5m[i].low) + ";" + DoubleToString(states.rates_5m[i].close) + "|";
      hlc_30m += DoubleToString(states.rates_30m[i].high) + ";" + DoubleToString(states.rates_30m[i].low) + ";" + DoubleToString(states.rates_30m[i].close) + "|";
      hlc_4h += DoubleToString(states.rates_4h[i].high) + ";" + DoubleToString(states.rates_4h[i].low) + ";" + DoubleToString(states.rates_4h[i].close) + "|";

      // 1d timeframe vol  : vol(0);vol(1);...| 20 data
      if(i < 19)
        {
         vol_1d += IntegerToString(states.vol_1d[i]) + ";";
        }
      else
         if(i == 19)
           {
            vol_1d += IntegerToString(states.vol_1d[i]) + "|";
           }

      // Indicators        : strength of left side currency in 7 other pairs; strength of right side currency in 7 other pairs; daily atr|
      if(i<6)
        {
         indicators_data += DoubleToString(states.left_currency_strength[i]) + ";";
        }
      else
         if(i < 12)
           {
            indicators_data += DoubleToString(states.right_currency_strength[i-6]) + ";";
           }
         else
            if(i == 12)
              {
               indicators_data += DoubleToString(states.daily_atr) + "|";
              }

     }
     
   message += hlc_5m + hlc_30m + hlc_4h + vol_1d + indicators_data;

// time              : day of week;hour|
   message += IntegerToString(states.day_of_week) +";"+ IntegerToString(states.hour)+"|";

// robot status      : current position;current profit|
   message += IntegerToString(states.current_position) +";"+ DoubleToString(states.current_profit, 5)+"|";
   
   // reward            : ballance difference|
   message += DoubleToString(reward_raw_data.ballance_diff_percent, 4) + "|";
   
   message += IntegerToString(done) + "|";
   
   return message;
  }
//+------------------------------------------------------------------+
int encode_say_hello_massage(const string name, uchar &data[])
  {
   return encode_default_massage(name, SAY_HELLO, "hello from client", data);
  }
//+------------------------------------------------------------------+
// Decoders ==============================================================================================================================================
// =======================================================================================================================================================
void decode_default_message(const uchar &data[], const int len, DefaultMassage &message_struct[], int max_len)
  {
   string Name = "";
   string message = "";
   MESSAGE_TYPE message_type = UNKNOWN;
   DECODER_STATE decoder_state = EXTRACTING_NAME;
   int k = 0;
   for(int i=1; i<len; i++)
     {
      switch(decoder_state)
        {
         case  EXTRACTING_NAME:
            if(data[i] != ',')
               Name += CharToString(data[i]);
            else
               decoder_state = EXTRACTING_MESSAGE_TYPE;
            break;

         case  EXTRACTING_MESSAGE_TYPE:
            if(data[i] != ',')
               message_type = (MESSAGE_TYPE)StringToInteger(CharToString(data[i]));
            else
               decoder_state = EXTRACTING_MESSAGE;
            break;
         case  EXTRACTING_MESSAGE:
            if(data[i] != ',')
               message += CharToString(data[i]);
            else
               decoder_state = EXTRACTING_NAME;
            message_struct[k].message = message;
            message = "";
            message_struct[k].message_type = message_type;
            message_type = UNKNOWN;
            message_struct[k].name = Name;
            Name = "";
            k++;
            i++;
            break;
         default:
            break;
        }
      if(k >= max_len)
         break;
     }
  }
//+------------------------------------------------------------------+

//+------------------------------------------------------------------+
