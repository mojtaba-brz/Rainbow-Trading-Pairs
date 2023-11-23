//+------------------------------------------------------------------+
//|                                                      ProjectName |
//|                                      Copyright 2020, CompanyName |
//|                                       http://www.companyname.net |
//+------------------------------------------------------------------+

#include "typedefs.mqh"
#include "MQL_Easy/MQL_Easy/MQL_Easy.mqh"

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
double calculate_last_daily_atr(string symbol)
  {
   double close[14], high[14], low[14];
   CopyClose(symbol, PERIOD_D1, 2, 14, close);
   CopyHigh(symbol,  PERIOD_D1, 1, 14, high);
   CopyLow(symbol,   PERIOD_D1, 1, 14, low);

   double sum = 0, TR;

   for(int i=0; i<14; i++)
     {
      TR = MathMax(high[i]-low[i], MathAbs(low[i] - close[i]));
      TR = MathMax(TR,             MathAbs(high[i] - close[i]));
      sum += TR;
     }

   return (sum/14);
  }

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
POSITION_STATE get_current_position_state(string symbol, long magic)
  {
   CPosition cp(symbol, magic);

   if(cp.get_total_specified_positions() == 1)
     {
      int pos_type = cp.get_position_type();
      if(pos_type == POSITION_TYPE_BUY)
        {
         return LONG_POSITION;
        }
      if(pos_type == POSITION_TYPE_SELL)
        {
         return SHORT_POSITION;
        }
      return NO_POSITION;
     }
   else
      if(cp.get_total_specified_positions() > 1)
        {
         return MORE_THAN_ONE_POSITION;
        }
      else
        {
         return NO_POSITION;
        }
  }
  
double get_current_profit(string symbol, long magic)
{
   CPosition cp(symbol, magic);
   return cp.get_current_profit();
}

void get_related_symbols_and_their_side(char side, string symbol, string &related_symbols[],char &side_array_of_related_symbols[])
{
   char pair[3];
   char s[];
   StringToCharArray(symbol, s);

   if(side == 'R')
     {
      pair[0] = s[3];
      pair[1] = s[4];
      pair[2] = s[5];
     }
   else
     {
      pair[0] = s[0];
      pair[1] = s[1];
      pair[2] = s[2];
     }
   
   int k = 0;
   for(int i=0; i<N_AllSymbols; i++)
     {
      char sym_char[];
      StringToCharArray(AllSymbols[i], sym_char);
      if(s[0] == sym_char[0] && s[1] == sym_char[1] && s[2] == sym_char[2] && 
         s[3] == sym_char[3] && s[4] == sym_char[4] && s[5] == sym_char[5])
        {
         continue;
        }
         if(sym_char[3] == pair[0] && sym_char[4] == pair[1] && sym_char[5] == pair[2])
           {
            related_symbols[k] = AllSymbols[i];
            side_array_of_related_symbols[k] = 'R';
            k++;
           }
         if(sym_char[0] == pair[0] && sym_char[1] == pair[1] && sym_char[2] == pair[2])
         {
            related_symbols[k] = AllSymbols[i];
            side_array_of_related_symbols[k] = 'L';
            k++;
         }
     }

}

double get_symbol_normalized_strength(string symbol, ENUM_TIMEFRAMES tf)
{
   int rsi_handle = iRSI(symbol, tf, 14, PRICE_CLOSE);
   double temp[];
   CopyBuffer(rsi_handle, 0, 1, 1, temp);
   temp[0] -= 50;
   temp[0] *= 0.02;
   IndicatorRelease(rsi_handle);
   return temp[0];
}

void set_symbols_strength(string symbol, char side, double &normalized_strength[])
{
   // data len must be 6
   char pair[3];
   char sym_char[6];
   StringToCharArray(symbol, sym_char);
   
   if(side == 'R')
     {
      pair[0] = sym_char[0];
      pair[1] = sym_char[1];
      pair[2] = sym_char[2];
     }
   else
     {
      pair[0] = sym_char[3];
      pair[1] = sym_char[4];
      pair[2] = sym_char[5];    
     }
   
   string related_symbols[6];
   char side_array_of_related_symbols[6];
   get_related_symbols_and_their_side(side, symbol, related_symbols, side_array_of_related_symbols);
   
   for(int i=0;i<6;i++)
     {
      normalized_strength[i] = get_symbol_normalized_strength(symbol, PERIOD_M30);
      if(side_array_of_related_symbols[i] == 'R')
        {
         normalized_strength[i] = -normalized_strength[i];
        }
     }  
     
}

int get_day_of_the_week()
{
   long time = SymbolInfoInteger(Symbol(), SYMBOL_TIME);
   MqlDateTime time_struct;
   TimeToStruct(time, time_struct);
   return time_struct.day_of_week;
}

int get_hour()
{
   long time = SymbolInfoInteger(Symbol(), SYMBOL_TIME);
   MqlDateTime time_struct;
   TimeToStruct(time, time_struct);
   return time_struct.hour;
}
//+------------------------------------------------------------------+
