//+------------------------------------------------------------------+
//|                                                      ProjectName |
//|                                      Copyright 2020, CompanyName |
//|                                       http://www.companyname.net |
//+------------------------------------------------------------------+
#include "../TrBotClient.mqh"

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
void OnStart(void)
  {
   string name = "MqlTRBotClient", host = "127.0.0.1";
   bool is_new;
   int host_port = 65333;
   TrBotClient tbc(name, host, host_port);
   TR_ACTIONS action;

   while(true)
     {
      tbc.say_hello();
      tbc.send_market_states(Symbol(), 123, 100);
      is_new = false;
      while(!is_new)
        {
         action = tbc.get_last_action(is_new);
        }
      printf("connected : %i,    action : %i, new_action : %i", tbc.is_connected_to_py(), action, is_new);
      Sleep(500);
     }
    
  }
//+------------------------------------------------------------------+
