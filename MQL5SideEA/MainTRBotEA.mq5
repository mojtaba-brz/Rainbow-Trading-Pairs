//+------------------------------------------------------------------+
//|                                                   Mql Side TRBot |
//|                              Email : mojtababahrami147@gmail.com |
//+------------------------------------------------------------------+
#property description "Main TRBot EA"
#property description "Athur : Mojtaba Bahrami"
#property description "Email : mojtababahrami147@gmail.com"
#property copyright "MIT"

#include "AllNeededLibs.mqh"

// User Config =======================================================
input static long robot_magic_number = 145679;
// Server  related Configs
input static string server_IP = "127.0.0.1";
input static int    server_port = 65333;
input static int    say_hello_period_sec = 200;

// Global Variables ==================================================

// flags
static bool    new_candle = false,
               params_sent = false,
               states_sent = false,
               action_recived = false,
               modes_cycle_done = false;
// ints
static TR_ACTIONS requested_action = DO_NOTHING;
static int current_time, pre_time = 0, atr_handler;
static MAIN_EA_STATES MainEAState = SENDING_STATES;
static POSITION_STATE position_state = NO_POSITION;
// strings
static string main_bot_name = "Mql Main TRBotEA";

// Classes
static TrBotClient tbc(main_bot_name, server_IP, server_port);

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
//--- create timer
//EventSetTimer(say_hello_period_sec);
   atr_handler = iATR(Symbol(), PERIOD_D1, 14);
   tbc.send_message_to_server(SAY_HELLO);
   return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
//--- destroy timer
   EventKillTimer();

  }
//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
//---
   current_time = current_candle_time_sec();
   new_candle = current_time > pre_time;

   if(new_candle && tbc.is_connected_to_py())
     {
      position_state = get_current_position_state(Symbol(), robot_magic_number);
      warn_if_there_are_more_than_one_position(position_state);
      modes_cycle_done = false;
      while(!modes_cycle_done)
        {
         switch(MainEAState)
           {
            case  SENDING_STATES:// ===============================================================
               states_sent = false;
               while(!states_sent)
                 {
                  states_sent = tbc.send_market_states_and_rewrad(Symbol(), robot_magic_number);
                 }
               MainEAState = WAIT_FOR_ACTION;
               break;

            case  WAIT_FOR_ACTION:// ===============================================================
               action_recived = false;
               while(!action_recived)
                 {
                  requested_action = tbc.get_last_action(action_recived);
                 }
               printf("action recieved : %i", requested_action);
               if((requested_action == DO_NOTHING || requested_action == CLOSE_POS) && position_state == NO_POSITION)
                 {
                  MainEAState = IDLE_MODE;
                 }
               else
                 {
                  MainEAState = MANAGE_THE_POSITION;
                 }

               break;

            case  MANAGE_THE_POSITION:// ===============================================================
               if(position_state == NO_POSITION)
                 {
                  if(requested_action == BUY_NOW)
                    {
                     enter_long_position_nnf_method(Symbol(), robot_magic_number, atr_handler);
                    }
                  else
                     if(requested_action == SELL_NOW)
                       {
                        enter_short_position_nnf_method(Symbol(), robot_magic_number, atr_handler);
                       }

                 }
               else
                  if(position_state == LONG_POSITION)
                    {
                     if(requested_action == BUY_NOW || requested_action == DO_NOTHING)
                       {
                        manage_positions_nnf_method(Symbol(), robot_magic_number);
                       }
                     else
                        if(requested_action == SELL_NOW)
                          {
                           close_all_specified_positions(Symbol(), robot_magic_number);
                           enter_short_position_nnf_method(Symbol(), robot_magic_number, atr_handler);
                          }
                        else
                           if(requested_action == CLOSE_POS)
                             {
                              close_all_specified_positions(Symbol(), robot_magic_number);
                             }
                    }
                  else
                     if(position_state == SHORT_POSITION)
                       {
                        if(requested_action == SELL_NOW || requested_action == DO_NOTHING)
                          {
                           manage_positions_nnf_method(Symbol(), robot_magic_number);
                          }
                        else
                           if(requested_action == BUY_NOW)
                             {
                              close_all_specified_positions(Symbol(), robot_magic_number);
                              enter_long_position_nnf_method(Symbol(), robot_magic_number, atr_handler);
                             }
                           else
                              if(requested_action == CLOSE_POS)
                                {
                                 close_all_specified_positions(Symbol(), robot_magic_number);
                                }
                       }
               MainEAState = IDLE_MODE;
               break;

            case IDLE_MODE:
            default:
               modes_cycle_done = true;
               MainEAState = SENDING_STATES;
               break; // ===============================================================
           }
        }
      pre_time = current_time;
     }
  }
//+------------------------------------------------------------------+
//| Timer function                                                   |
//+------------------------------------------------------------------+
/* The Timer event is periodically generated by the client terminal for
the Expert Advisor that has activated the timer by the EventSetTimer function.
Usually, this function is called by OnInit. Timer event processing is performed
by the OnTimer function. After the operation of the Expert Advisor is completed,
it is necessary to destroy the timer using the EventKillTimer function, which is
usually called in the OnDeinit function. */
void OnTimer()
  {
//---
   tbc.send_message_to_server(SAY_HELLO);
  }
//+------------------------------------------------------------------+
//| Trade function                                                   |
//+------------------------------------------------------------------+
/* The Trade event is generated when a trade operation is completed on a trade server.
The Trade event is handled by the OnTrade() function for the following trade operations:
•sending, modifying or removing of a pending order;
•cancellation of a pending order with not enough of money or expiration;
•activation of a pending order;
•opening, adding or closing a position (or part of the position);
•modifying of the open position (change stops – Stop Loss and/or Take Profit).*/
void OnTrade()
  {
//---

  }
//+------------------------------------------------------------------+
//| TradeTransaction function                                        |
//+------------------------------------------------------------------+
/*
When performing some definite actions on a trade account, its state changes.
Such actions include:
•Sending a trade request from any MQL5 application in the client terminal using OrderSend and OrderSendAsync functions and its further execution;
•Sending a trade request via the terminal graphical interface and its further execution;
•Pending orders and stop orders activation on the server;
•Performing operations on a trade server side.

The following trade transactions are performed as a result of these actions:
•handling a trade request;
•changing open orders;
•changing orders history;
•changing deals history;
•changing positions.

For example, when sending a market buy order, it is handled, an appropriate
buy order is created for the account, the order is then executed and removed
from the list of the open ones, then it is added to the orders history, an
appropriate deal is added to the history and a new position is created.
All these actions are trade transactions. Arrival of such a transaction at
the terminal is a TradeTransaction event. This event is handled by OnTradeTransaction function.
*/
void OnTradeTransaction(const MqlTradeTransaction& trans,
                        const MqlTradeRequest& request,
                        const MqlTradeResult& result)
  {
//---

  }
//+------------------------------------------------------------------+
//| Tester function                                                  |
//+------------------------------------------------------------------+
// The Tester event is generated after testing of an Expert Advisor on history data is over
double OnTester()
  {
//---
   double ret=0.0;
//---

//---
   return(ret);
  }
//+------------------------------------------------------------------+
//| TesterInit function                                              |
//+------------------------------------------------------------------+
// The TesterInit event is generated with the start of optimization in the strategy tester before the first optimization pass.
void OnTesterInit()
  {
//---
   EventKillTimer();
  }
//+------------------------------------------------------------------+
//| TesterPass function                                              |
//+------------------------------------------------------------------+
// The TesterPass event is generated when a new data frame is received
void OnTesterPass()
  {
//---

  }
//+------------------------------------------------------------------+
//| TesterDeinit function                                            |
//+------------------------------------------------------------------+
// The TesterDeinit event is generated after the end of optimization of an Expert Advisor in the strategy tester
void OnTesterDeinit()
  {
//---

  }
//+------------------------------------------------------------------+
//| ChartEvent function                                              |
//+------------------------------------------------------------------+
/*
The ChartEvent event is generated by the client terminal when a user
is working with a chart:
•keystroke, when the chart window is in focus;
•graphical object created
•graphical object deleted
•mouse press on the graphical object of the chart
•move of the graphical object using the mouse
•end of text editing in LabelEdit.

Also there is a custom event ChartEvent, which can be sent to an
Expert Advisor by any mql5 program by using the EventChartCustom
function. The event is processed by the OnChartEvent function.
*/
void OnChartEvent(const int id,
                  const long &lparam,
                  const double &dparam,
                  const string &sparam)
  {
//---

  }
//+------------------------------------------------------------------+
//| BookEvent function                                               |
//+------------------------------------------------------------------+
/*
The BookEvent event is generated by the client terminal after the
Depth Of Market is changed; it is processed by the OnBookEvent function.
To start generation of BookEvent for the specified symbol, it is necessary
to subscribe the symbol to this event by using the MarketBookAdd function.

To unsubscribe from BookEvent for a specified symbol, it is necessary to call
the MarketBookRelease function. The BookEvent event is a broadcasting-type event -
it means that it is sufficient to subscribe just one Expert Advisor for this event,
and all other Expert Advisors that have the OnBookEvent event handler, will receive it.
That's why it is necessary to analyze the symbol name, which is passed to a handler as a parameter.
*/
void OnBookEvent(const string &symbol)
  {
//---

  }
//+------------------------------------------------------------------+

//+------------------------------------------------------------------+
