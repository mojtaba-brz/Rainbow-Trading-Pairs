# Local Imports ====================================================
from Simulator.MarketSim.MarketSim import PairSimulator, TradeSim 

config = {
    # Pair Symulator ===============
    "symbol name" : "EURUSD",
    "main timeframe" : "M5",
    
    # Trade Simulator ==============
    "starter cash" : 10000,
    "broker fee" : 0.002,
    "leverage" : 100
}


class ForexSimulator(PairSimulator, TradeSim):
    def __init__(self, config):
        super().__init__(config["symbol name"], config["main timeframe"])
        self.init_trade_sim(config["starting cash"], config["broker fee"], config["leverage"])
    
    def step(self, action = None):
        # action : discrete(4) -->  0:do nothing, 1:buy, 2:sell, 3:close
        # only one position is allowed
        pair_states =  self.get_pair_states()
        trade_states = self.get_trade_states()
        self.pair_sim_step()
        
    
    def reset(self, reset_index_to=100):
        super().reset(reset_index_to)
        self.reset_trade_sim()
        pair_states =  self.get_pair_states()
        trade_states = self.get_trade_states()
        return pair_states + trade_states
    
    def render(self):
        pass