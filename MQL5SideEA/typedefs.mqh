//+------------------------------------------------------------------+
//|                                                     typedefs.mqh |
//|                                  Copyright 2023, MetaQuotes Ltd. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2023, MetaQuotes Ltd."
#property link      "https://www.mql5.com"

// Common Types ===========================================================
// these data must be sync with py side ===================================
enum MESSAGE_TYPE
  {
   SAY_HELLO = 0,
   ALGO_PARAMS = 1,
   MARKET_STATES = 2,
   ACTION = 3,
   REQUEST_MESSAGE = 4,
   CONNECTION_CHECK = 5,
   UNKNOWN = 6
  };

struct DefaultMassage
  {
   string            name;
   MESSAGE_TYPE      message_type;
   string            message;
  };

enum TR_ACTIONS
  {
   BUY_NOW = 0,
   SELL_NOW = 1,
   DO_NOTHING = 2,
   CLOSE_POS = 3
  };

enum POSITION_STATE
  {
   NO_POSITION = 0,
   LONG_POSITION = 1,
   SHORT_POSITION = 2,
   MORE_THAN_ONE_POSITION = 3
  };

struct MarketStates
  {
   // 5m timeframe hlc  : high;low;close| 50 data
   // 30m timeframe hlc : high;low;close| 50 data
   // 4h timeframe hlc  : high;low;close| 50 data
   // 1d timeframe vol  : vol(0);vol(1);...| 20 data
   MqlRates          rates_5m[], rates_30m[], rates_4h[];
   long              vol_1d[];

   // Indicators        : strength of left side currency in 7 other pairs; strength of right side currency in 7 other pairs; daily atr|
   double            left_currency_strength[7], right_currency_strength[7], daily_atr;

   // time              : day of week;hour|
   int               day_of_week, hour;

   // robot status      : current position;current profit|
   POSITION_STATE    current_position;
   double            current_profit;
  };

struct RewardRawData
  {
   double ballance_diff_percent;
  };
// =============================================================================
// Mql Side Types ==============================================================
enum MAIN_EA_STATES
  {
   SENDING_STATES,
   WAIT_FOR_ACTION,
   MANAGE_THE_POSITION,
   IDLE_MODE
  };

enum DECODER_STATE
  {
   EXTRACTING_NAME,
   EXTRACTING_MESSAGE_TYPE,
   EXTRACTING_MESSAGE,
   END
  };

string AllSymbols[] = {"AUDCAD",
                       "AUDCHF",
                       "AUDJPY",
                       "AUDNZD",
                       "AUDUSD",
                       "CADCHF",
                       "CADJPY",
                       "CHFJPY",
                       "EURAUD",
                       "EURCAD",
                       "EURCHF",
                       "EURGBP",
                       "EURJPY",
                       "EURNZD",
                       "EURUSD",
                       "GBPAUD",
                       "GBPCAD",
                       "GBPCHF",
                       "GBPJPY",
                       "GBPNZD",
                       "GBPUSD",
                       "NZDCAD",
                       "NZDCHF",
                       "NZDJPY",
                       "NZDUSD",
                       "USDCAD",
                       "USDCHF",
                       "USDJPY"
                      };
int N_AllSymbols = 28;
//+------------------------------------------------------------------+
