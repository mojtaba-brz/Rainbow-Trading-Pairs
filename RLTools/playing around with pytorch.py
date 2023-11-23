import gymnasium as gym
import torch
device = 'cpu'
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
import os
import matplotlib.pyplot as plt

# Local Imports =====================================================
from Rainbow import RainbowAlgorithm

env = gym.make("CartPole-v1")

agent_configs = {
    'lr' : 1e-3,
    'gamma' : 0.95,
    'DoubleQLearning' : True,
    'file dir' : 'CartPole'
}

Agent = RainbowAlgorithm(env.observation_space.shape[0], env.action_space.n, agent_configs)
total_episodes = 10000
n = 1
mean_rewards = 0
for episode in range(total_episodes):
    done, truncated = False, False
    states, _ = env.reset()
    states = torch.from_numpy(states).to(device)
    total_reward = 0
    while not (done or truncated):
        action = Agent.Q_to_greedy_action_vector(states, epsilon=0.1)  # Noisy NetWork Does the Exploration
        
        next_state, reward, done, truncated, _ = env.step(action.item())
        next_state = torch.from_numpy(next_state).to(device)
        reward = torch.Tensor([reward]).to(device)
        done = torch.Tensor([done]).to(device) 
        
        Agent.train(states, action, next_state, reward, done)
        
        states = next_state
        total_reward += reward
    
    mean_rewards += (total_reward.item() - mean_rewards)/n
    n += 1
    
    if episode%10 == 0:
        Agent.self_train()
        print(f"progress : {(1+episode)/total_episodes*100 :> .2f}%,  last loss : {Agent.get_last_loss():0.3f},      mean_rewards : {mean_rewards:>.0f}") 
        n = 1
        mean_rewards = 0
        # Agent.save()

# Agent.save()
