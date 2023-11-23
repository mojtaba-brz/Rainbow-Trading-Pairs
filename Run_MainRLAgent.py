import torch
import numpy as np
from time import sleep
import os
def clc():
    os.system('cls' if os.name == 'nt' else 'clear')
device = 'cpu'
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")    
# Local Import ========================================================
from ConnectionWithMQL5.TrBotPYSideClient import TrBotPYSideClient
from ConnectionWithMQL5.typedefs import *
from Simulator.MetaTraderEnv import MetaTrader5Env
from RLTools.Rainbow import RainbowAlgorithm

agent_configs = {
    'lr' : 1e-6,
    'gamma' : 1,
    'DoubleQLearning' : True,
    'file dir' : 'EURUSD M5',
    'save periode' : 100
}
Agent = RainbowAlgorithm(487, len(TR_ACTIONS), agent_configs)

env = MetaTrader5Env()
action = TR_ACTIONS.DO_NOTHING.value
state = None
save_counter = 1
rewards_sum = 0

while True:
    next_state, reward, _, _, _ = env.step(action)
    if next_state :
        rewards_sum += reward
        next_state = env.market_states_to_Tensor(next_state)
        if state is not None:
            reward = env.reward_to_Tensor(reward)
            Agent.train(state, action, next_state, reward, torch.Tensor([False]).to(device).to(torch.float64))
            if save_counter > agent_configs['save periode']:
                Agent.self_train(10)
                print(f"r : {rewards_sum:>.5f},   action : {action},  loss : {Agent.get_last_loss():>5.7f}")
                Agent.save()
                save_counter = 0
        save_counter += 1
        state  = next_state
        action = Agent.Q_to_greedy_action_vector(state, 0.2)
    sleep(.01)
