//+------------------------------------------------------------------+
//|                                                      ProjectName |
//|                                      Copyright 2020, CompanyName |
//|                                       http://www.companyname.net |
//+------------------------------------------------------------------+

#include "AllNeededLibs.mqh"

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
void warn_if_there_are_more_than_one_position(POSITION_STATE pos_state)
  {
   if(pos_state == MORE_THAN_ONE_POSITION)
     {
      Alert("There are more than one trade");
     }
  }

// enter the position with tp ==============================================================
void enter_long_position_nnf_method(string symbol, long magic, int &atr_handle)
  {
   CExecute ex1(symbol, magic); // without tp
   CExecute ex2(symbol, magic + 1); // with tp
   double sl_diff, tp_diff, vol, ask_price;

   ask_price = SymbolInfoDouble(symbol, SYMBOL_ASK);
   sl_tp_diff_nnf_method(symbol, atr_handle, sl_diff, tp_diff);
   vol = get_lot_by_sl_diff_and_risk(sl_diff, symbol, 1);
   vol = MathMin(vol, 1);
   
   ex1.Position(TYPE_POSITION_BUY, vol, ask_price-sl_diff);
   Sleep(5);
   ex2.Position(TYPE_POSITION_BUY, vol, ask_price-sl_diff, ask_price+tp_diff);
  }

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
void enter_short_position_nnf_method(string symbol, long magic, int &atr_handle)
  {
   CExecute ex1(symbol, magic); // without tp
   CExecute ex2(symbol, magic + 1); // with tp
   double sl_diff, tp_diff, vol, ask_price;

   ask_price = SymbolInfoDouble(symbol, SYMBOL_BID);
   sl_tp_diff_nnf_method(symbol, atr_handle, sl_diff, tp_diff);
   vol = get_lot_by_sl_diff_and_risk(sl_diff, symbol, 1);

   ex1.Position(TYPE_POSITION_SELL, vol, ask_price+sl_diff);
   Sleep(5);
   ex2.Position(TYPE_POSITION_SELL, vol, ask_price+sl_diff, ask_price-tp_diff);
  }

// close position ============================================================================
void close_all_specified_positions(string symbol, long magic)
  {
   CPosition cp1(symbol, magic), cp2(symbol, magic + 1);
   cp1.close_all_specified_positions();
   cp2.close_all_specified_positions();
  }

// manage the position without tp ===========================================================
void manage_positions_nnf_method(string symbol, long magic)
  {
   CPosition   cp1(symbol, magic),
               cp2(symbol, magic + 1);
   POSITION_STATE cp1_state = get_current_position_state(symbol, magic),
                  cp2_state = get_current_position_state(symbol, magic + 1);

   if(cp2_state == NO_POSITION)
     {
      if(cp1_state == LONG_POSITION)
        {
         cp1.Modify(cp1.GetPriceOpen());
        }
      else
         if(cp1_state == SHORT_POSITION)
           {
            cp1.Modify(cp1.GetPriceOpen());
           }

     }

  }

//+------------------------------------------------------------------+
