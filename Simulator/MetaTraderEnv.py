from gymnasium import Env
from gymnasium.spaces import Box, Discrete, Dict
import numpy as np
from time import sleep
import torch
device = 'cpu'
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# Local Imports ==========================================================
from ConnectionWithMQL5.TrBotPYSideClient import TrBotPYSideClient

class MetaTrader5Env(Env):
    """
    this class is a standard Gymnasium env for
    intractions with Mql5 Side Client.
    """
# ==================================================================================================================================================
# ======================================================== Main Functions ==========================================================================
# ==================================================================================================================================================
    def __init__(self, config : dict = {}):
        self.tbc = TrBotPYSideClient(config.get("host address", "127.0.0.1"),
                                     config.get("host port", 65333),
                                     config.get("say hello period", 10))
        
        self.action_space = Discrete(3)  # buy, sell and nothing
        
        self.observation_space = Dict({
                                        # rate based data
                                        "5m timeframe hlc" : Box(low = 0., high = 2.0, shape=(1, 50), dtype=np.float32),
                                        "30m timeframe hlc": Box(low = 0., high = 2.0, shape=(1, 50), dtype=np.float32),
                                        "4h timeframe hlc" : Box(low = 0., high = 2.0, shape=(1, 50), dtype=np.float32),
                                        "1d timeframe vol" : Box(low = 0., high = 100, shape=(1, 20), dtype=np.float32),
                                        
                                        # time
                                        "day of week" : Discrete(7),
                                        "hour" : Discrete(24),
                                        
                                        # indicators data from metatrader 5
                                        "strength of left currency" : Box(low = -1., high = 1.0, shape=(1, 6), dtype=np.float32),
                                        "strength of right currency" : Box(low = -1., high = 1.0, shape=(1, 6), dtype=np.float32),
                                        "last daily atr" : Box(low = 0., high = 100, shape=(1, 1), dtype=np.float32),
                                        
                                        # robot status
                                        "current position" : Discrete(3), # long, short, nothing
                                        "current profit" : Box(low = -100000., high = 100000.0, shape=(1, 1), dtype=np.float32)
        })
        
        self.obs = {}
        self.last_reward = 0
        
    def reset(self, *, seed=None, options=None):
        """Resets the episode.

        Returns:
           Initial observation of the new episode and an info dict.
        """
        self.update_observations_and_reward()
        return self.last_observation, {}

    def step(self, action):
        """Takes a single step in the episode given `action`.

        Returns:
            New observation, reward, terminated-flag, truncated-flag, info-dict (empty).
        """
        # send action
        self.tbc.send_action(action)
        # get observations and reward
        self.update_observations_and_reward()
        
        return self.obs, self.last_reward, self.done, False, {}

# ==================================================================================================================================================
# ======================================================== Utility Functions =======================================================================
# ==================================================================================================================================================
    def update_observations_and_reward(self):
        reward = None
        while not reward:
            states , reward, self.done = self.tbc.get_market_states_if_available()
            if not reward :
                sleep(.01)
        
        self.transform_tbc_states_to_standard_states(states)
        self.transform_tbc_reward_struct_to_standard_raward(reward)
    
    def transform_tbc_states_to_standard_states(self, states):
        # self.obs["5m timeframe hlc"] = states.rates_5m
        # self.obs["30m timeframe hlc"] = states.rates_30m
        # self.obs["4h timeframe hlc"] = states.rates_4h
        # self.obs["1d timeframe vol"] = states.vol_1d
        
        # self.obs["day of week"] = states.day_of_week
        # self.obs["hour"] = states.hour
        
        # self.obs["strength of left currency"] = states.left_currency_strength
        # self.obs["strength of right currency"] = states.right_currency_strength
        # self.obs["last daily atr"] = states.daily_atr
        
        # self.obs["current position"] = states.current_position
        # self.obs["current profit"] = states.current_profit
        self.obs = states
        
        
    def transform_tbc_reward_struct_to_standard_raward(self, reward):
        self.last_reward = reward.ballance_diff
    
    def market_states_to_Tensor(self, states):
        state_tensor = torch.zeros(0)
        state_tensor = torch.concatenate((state_tensor, torch.from_numpy(states.rates_5m.high_array)))
        state_tensor = torch.concatenate((state_tensor, torch.from_numpy(states.rates_5m.low_array)))
        state_tensor = torch.concatenate((state_tensor, torch.from_numpy(states.rates_5m.close_array)))
        state_tensor = torch.concatenate((state_tensor, torch.from_numpy(states.rates_30m.high_array)))
        state_tensor = torch.concatenate((state_tensor, torch.from_numpy(states.rates_30m.low_array)))
        state_tensor = torch.concatenate((state_tensor, torch.from_numpy(states.rates_30m.close_array)))
        state_tensor = torch.concatenate((state_tensor, torch.from_numpy(states.rates_4h.high_array)))
        state_tensor = torch.concatenate((state_tensor, torch.from_numpy(states.rates_4h.low_array)))
        state_tensor = torch.concatenate((state_tensor, torch.from_numpy(states.rates_4h.close_array)))
        state_tensor = torch.concatenate((state_tensor, torch.from_numpy(states.vol_1d)))
        
        state_tensor = torch.concatenate((state_tensor, torch.Tensor([states.day_of_week])))
        state_tensor = torch.concatenate((state_tensor, torch.Tensor([states.hour])))
        
        state_tensor = torch.concatenate((state_tensor, torch.from_numpy(states.left_currency_strength)))
        state_tensor = torch.concatenate((state_tensor, torch.from_numpy(states.right_currency_strength)))
        state_tensor = torch.concatenate((state_tensor, torch.Tensor([states.daily_atr])))
        
        state_tensor = torch.concatenate((state_tensor, torch.Tensor([states.current_position.value])))
        state_tensor = torch.concatenate((state_tensor, torch.Tensor([states.current_profit])))
        
        return state_tensor.to(device)
        
        
        
    
    def reward_to_Tensor(self, reward):
        reward -= 0.0005
        return torch.Tensor([reward]).to(device).to(torch.float64) 