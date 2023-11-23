# TODO : distributional, n-step 
# Note : no NoisyNet is used
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import os
import math

# Local Imports =====================================================
from RLTools.ReplayMemory import PrioritizedReplayMemory

# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
device = 'cpu'

class ConventionalNN(torch.nn.Module):
    # this class duty is to estimate Q(s, a)
    def __init__(self, n_input : int, n_output : int):
        super(ConventionalNN, self).__init__()
        self.hidden_layer_nodes = 2 ** min(12, n_input)
        self.neural_network = torch.nn.Sequential(
            # define a conventional multi layer neural network here ======
            torch.nn.Linear(n_input, self.hidden_layer_nodes),
            torch.nn.Tanh(),
            # torch.nn.Linear(self.hidden_layer_nodes, self.hidden_layer_nodes),
            # torch.nn.Tanh(),
            torch.nn.Linear(self.hidden_layer_nodes, n_output)
            # ============================================================
            ).to(torch.float64)
        
    def forward(self, u : torch.Tensor):
        return self.neural_network(u.to(torch.float64).to(device))
         
class RainbowAlgorithm():
    def __init__(self, n_input : int, n_actions : int, rainbow_config : dict  ={}):
        self.file_dir = rainbow_config.get('file dir', '')
        self.DoubleQLearning_is_on = rainbow_config.get('DoubleQLearning', False)
        
        # Q Learning
        if os.path.isfile(self.file_dir + "_Qnet.pt"):
            self.Qnet = torch.load(self.file_dir + "_Qnet.pt").to(device)
        else:
            self.Qnet = ConventionalNN(n_input, n_actions).to(device)
        self.n_inputs = n_input
        self.n_actions = n_actions
        self.optimizer = torch.optim.AdamW(self.Qnet.parameters(), lr = rainbow_config.get('lr', 1e-4))
        self.loss_fn = torch.nn.MSELoss()
        self.gamma = rainbow_config.get('gamma', 1)
        
        # Double Q Learning
        if self.DoubleQLearning_is_on:
            if os.path.isfile(self.file_dir + "_DoubleQnet.pt"):
                self.DoubleQnet = torch.load(self.file_dir + "_DoubleQnet.pt").to(device)
            else:
                self.DoubleQnet = ConventionalNN(n_input, n_actions).to(device)
        
            self.Doubleoptimizer = torch.optim.AdamW(self.DoubleQnet.parameters(), lr = rainbow_config.get('lr', 1e-4))
            self.Doubleloss_fn = torch.nn.MSELoss()
        
        # Prioritized Replay Memory
        self.PRM = PrioritizedReplayMemory(self.file_dir)  
        
        
    def train(self, states : torch.Tensor, actions : torch.Tensor, next_states : torch.Tensor, 
              rewards : torch.Tensor, dones : torch.Tensor, w : torch.Tensor = torch.Tensor([1.])):
        
        states = states.to(device)
        actions = actions.to(device)
        next_states = next_states.to(device)
        rewards = rewards.to(device)
        dones = dones.to(device)
        w = w.to(device)
        
        if self.DoubleQLearning_is_on:
            if len(rewards) > 1:
                Q_s_and_a_estimated = self.Qnet(states).gather(1, actions)
                Q_s_and_a = rewards + self.gamma * torch.max(self.DoubleQnet(next_states), 1)[0][0].t()*(1 - dones)
                DoubleQ_s_and_a_estimated = self.DoubleQnet(states).gather(1, actions)
                DoubleQ_s_and_a = rewards + self.gamma * torch.max(self.Qnet(next_states), 1)[0][0].t()*(1 - dones)
            else: 
                Q_s_and_a_estimated = torch.reshape(self.Qnet(states)[actions], (1,))
                Q_s_and_a = rewards + self.gamma * torch.max(self.DoubleQnet(next_states))*(1 - dones)
                DoubleQ_s_and_a_estimated = torch.reshape(self.DoubleQnet(states)[actions], (1,))
                DoubleQ_s_and_a = rewards + self.gamma * torch.max(self.Qnet(next_states))*(1 -  dones)
            
            self.Doubleloss = self.loss_fn(w * (DoubleQ_s_and_a_estimated-DoubleQ_s_and_a.detach()), torch.zeros((len(rewards), 1)).to(device).to(torch.float64))
            self.Doubleoptimizer.zero_grad()
            self.Doubleloss.backward()
            torch.nn.utils.clip_grad_norm_(self.DoubleQnet.parameters(), 5)
            self.Doubleoptimizer.step()
            
        else: # simple DQN
            if len(rewards) > 1:
                Q_s_and_a_estimated = self.Qnet(states).gather(1, actions)
                Q_s_and_a = rewards + self.gamma * torch.max(self.Qnet(next_states), 1)[0][0].t()*(1 - dones)
            else: 
                Q_s_and_a_estimated = torch.reshape(self.Qnet(states)[actions], (1,))
                Q_s_and_a = rewards + self.gamma * torch.max(self.Qnet(next_states))*(1 - dones)
                
        self.loss = self.loss_fn(w * (Q_s_and_a_estimated - Q_s_and_a.detach()), torch.zeros((len(rewards), 1)).to(device).to(torch.float64))
        self.optimizer.zero_grad()
        self.loss.backward()
        torch.nn.utils.clip_grad_norm_(self.Qnet.parameters(), 5)
        self.optimizer.step()
            
        # Prioritized Replay Memory
        priorities = torch.abs(Q_s_and_a_estimated.detach() - Q_s_and_a.detach())
        if len(rewards) > 1:
            self.PRM.update_pririties_idxs(priorities) 
        else:
            self.PRM.push(states, actions, next_states, rewards, dones, priorities)
    
    def Q_to_greedy_action_vector(self, state : torch.Tensor, epsilon = -1):
        limit = torch.rand(1)
        if limit < epsilon:
            return torch.randint(0, self.n_actions, (1,))[0]
        else:
            return self.Qnet(state).argmax()
    
    def save(self):
        torch.save(self.Qnet, self.file_dir+"_Qnet.pt")  
        self.PRM.save()
        if self.DoubleQLearning_is_on:
            torch.save(self.DoubleQnet, self.file_dir + "_DoubleQnet.pt") 
    
    def get_last_loss(self):
        try:
            return self.loss.item()
        except AttributeError:
            return -1
    
    def self_train(self, epoches = 1):
        for _ in range(epoches):
            s,a,n_s,r,d,w = self.PRM.sample(min(10000, len(self.PRM.rewards_buffer)))
            self.train(s, a, n_s, r, d, w)