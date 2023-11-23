//+------------------------------------------------------------------+
//|                                                      ProjectName |
//|                                      Copyright 2020, CompanyName |
//|                                       http://www.companyname.net |
//+------------------------------------------------------------------+
#include "typedefs.mqh"
#include "MessagesLib.mqh"
#include "Data2StateTransformationTools.mqh"
#include <Math/Stat/Math.mqh>

#import "WinSocketLib.dll"
int  WinSocketCreate();
bool  WinSocketConnect(int socket_index, char &host[], int port);
bool  WinSocketClose(int socket_index);
bool  WinSocketConnected(int socket_index);
int  WinSocketRead(int socket_index, char &buf[], int len);
int  WinSocketSend(int socket_index, char &buf[], int len);
#import

#define MAX_MQL_LEN 1000
//+------------------------------------------------------------------+
//|  TrBotClient Class                                               |
//+------------------------------------------------------------------+
class TrBotClient
  {
private:
   string            host, name;
   char              host_c[];

   double            pre_ballance;

   int               port, time_out_limit, client_idx, num_of_connection_tries;
   TR_ACTIONS        last_recived_action;

   bool              connected_to_py, new_action_recived;

public:
   void              TrBotClient(string Name = "MqlTRBotClient",
                                 string _host = "127.0.0.1",
                                 int _port = 65333,
                                 int _time_out_limit = 1000,
                                 int _num_of_connection_tries = 10);
   void              try_to_connect();
   void              ~TrBotClient();

   bool              is_connected_to_py();
   bool              say_hello();
   TR_ACTIONS        get_last_action(bool &is_new);
   bool              send_message_to_server(MESSAGE_TYPE message_type, string message = "");
   bool              send_market_states_and_rewrad(string symbol, long magic_number);
  };

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
void TrBotClient::TrBotClient(const string Name, const string _host, const int _port, const int _time_out_limit, const int _num_of_connection_tries)
  {
   host = _host;
   StringToCharArray(host, host_c);
   port = _port;
   name = Name;
   time_out_limit = _time_out_limit;
   num_of_connection_tries = _num_of_connection_tries;

   pre_ballance = AccountInfoDouble(ACCOUNT_BALANCE);
   last_recived_action = DO_NOTHING;
   connected_to_py = false;
   new_action_recived = false;

   client_idx = WinSocketCreate();
   WinSocketConnect(client_idx, host_c, port);
  }

//+------------------------------------------------------------------+
//| High Level Functions                                             |
//+------------------------------------------------------------------+
bool TrBotClient::is_connected_to_py()
  {
   if(send_message_to_server(CONNECTION_CHECK))
      return connected_to_py;
   return false;
  }

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
TR_ACTIONS TrBotClient::get_last_action(bool &is_new)
  {
   send_message_to_server(ACTION);
   is_new = new_action_recived;
   return last_recived_action;
  }

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
bool TrBotClient::send_market_states_and_rewrad(string symbol, long magic_number)
  {
   MarketStates states;
   RewardRawData reward_raw_data;
// 5m timeframe hlc  : high;low;close| 50 data
// 30m timeframe hlc : high;low;close| 50 data
// 4h timeframe hlc  : high;low;close| 50 data
// 1d timeframe vol  : vol(0);vol(1);...| 20 data
   CopyRates(symbol, PERIOD_M5, 1, 50, states.rates_5m);
   CopyRates(symbol, PERIOD_M30, 1, 50, states.rates_30m);
   CopyRates(symbol, PERIOD_H4, 1, 50, states.rates_4h);
   CopyTickVolume(symbol, PERIOD_D1, 1, 20, states.vol_1d);

// Indicators        : strength of left side currency in 7 other pairs; strength of right side currency in 7 other pairs; daily atr|
   states.daily_atr = calculate_last_daily_atr(symbol);
   set_symbols_strength(symbol, 'L', states.left_currency_strength);
   set_symbols_strength(symbol, 'R', states.right_currency_strength);

// time              : day of week;hour|
   states.day_of_week = get_day_of_the_week();
   states.hour = get_hour();

// robot status      : current position;current profit|
   states.current_position = get_current_position_state(symbol, magic_number);
   states.current_profit = get_current_profit(symbol, magic_number);

   double ballance = MathRound(AccountInfoDouble(ACCOUNT_BALANCE), 2);
   reward_raw_data.ballance_diff_percent = (ballance - pre_ballance)/pre_ballance*100;
   pre_ballance = ballance;

   datetime time[1];
   CopyTime(Symbol(), PERIOD_CURRENT, 0, 1, time);
   
   MqlDateTime time_s;
   
   TimeToStruct(time[0], time_s);
   
   int done = (int)(time_s.hour == 23 && time_s.min == 55);
   
   string message = encode_market_states_and_reward(states, reward_raw_data, done);  
   return send_message_to_server(MARKET_STATES, message);
  }
//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
bool TrBotClient::say_hello()
  {
   return send_message_to_server(SAY_HELLO);
  }
//+------------------------------------------------------------------+
//| Communication Low Level                                          |
//+------------------------------------------------------------------+
void TrBotClient::try_to_connect()
  {
   WinSocketClose(client_idx);
   client_idx = WinSocketCreate();
   bool connected = WinSocketConnect(client_idx, host_c, port);
   int cntr = 0;
   int elapsed_time = 0;
   int time_limit = time_out_limit * num_of_connection_tries;

   while(!connected && elapsed_time < time_limit)
     {
      WinSocketClose(client_idx);
      client_idx = WinSocketCreate();
      connected = WinSocketConnect(client_idx, host_c, port);
      Sleep(50);
      cntr++;
      elapsed_time = 50 * cntr;
     }
  }

//+------------------------------------------------------------------+
//|                                                                  |
//+------------------------------------------------------------------+
bool TrBotClient::send_message_to_server(const MESSAGE_TYPE message_type, const string message)
  {
   try_to_connect();
   uchar data[];
   int len;
   switch(message_type)
     {
      case SAY_HELLO:
         len = encode_say_hello_massage(name, data);
         break;
      case CONNECTION_CHECK:
      case ACTION:
         len = encode_default_massage(name, message_type, "nothing", data);
         break;

      default:
         len = encode_default_massage(name, message_type, message, data);
         break;
     }

   bool ok = (WinSocketSend(client_idx, data, len) == len);
   if(!ok)
     {
      try_to_connect();
      ok = (WinSocketSend(client_idx, data, len) == len);
     }

   uchar r_data[10000];
   DefaultMassage default_message[1];

   if(ok)
     {
      switch(message_type)
        {
         case  CONNECTION_CHECK:
            len = WinSocketRead(client_idx, r_data, 10000);
            if(len)
              {
               decode_default_message(r_data, len, default_message, 1);
               if(default_message[0].message_type == CONNECTION_CHECK)
                  connected_to_py = default_message[0].message == "1";
               else
                 {
                  printf("connection check error. recvd : %s\ndecoded : %s,%i,%s", CharArrayToString(r_data),
                         default_message[0].name, default_message[0].message_type, default_message[0].message);
                  connected_to_py = false;
                 }
              }
            else
              {
               connected_to_py = false;
              }
            break;

         case ACTION:
            len = WinSocketRead(client_idx, r_data, 10000);
            if(len)
              {
               decode_default_message(r_data, len, default_message, 1);
               if(default_message[0].message_type == ACTION)
                 {
                  last_recived_action = (TR_ACTIONS) StringToInteger(default_message[0].message);
                  new_action_recived = true;
                 }
               else
                 {
                  printf("Action request error. recvd : %s\ndecoded : %s,%i,%s", CharArrayToString(r_data),
                         default_message[0].name, default_message[0].message_type, default_message[0].message);
                  new_action_recived = false;
                 }
              }
            else
              {
               new_action_recived = false;
              }
            break;
         default:
            break;
        }
     }

   return ok;
  }
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+

//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
void TrBotClient::~TrBotClient()
  {
   WinSocketClose(client_idx);
  }
//+------------------------------------------------------------------+
