import torch
# local imports ========================
from ReplayMemory import PrioritizedReplayMemory

PRM = PrioritizedReplayMemory('test')

data1 = [torch.Tensor([1,2,3,4,5]), torch.Tensor([1]), torch.Tensor([2,2,7,5,1]), torch.Tensor([1]), torch.Tensor([0]), torch.Tensor([0.1])]
data2 = [torch.Tensor([1,2,2,4,5]), torch.Tensor([1]), torch.Tensor([2,2,7,5,1]), torch.Tensor([1]), torch.Tensor([0]), torch.Tensor([0.1])]

PRM.push(data1[0], data1[1], data1[2], data1[3], data1[4], data1[5])
PRM.push(data1[0], data1[1], data1[2], data1[3], data1[4], data1[5])
PRM.push(data1[0]+0.2, data1[1], data1[2], data1[3], data1[4], data1[5])
PRM.push(data1[0]+0.1, data1[1], data1[2], data1[3], data1[4], data1[5])
PRM.push(data2[0], data1[1], data1[2], data1[3], data1[4], data1[5])
PRM.push(data2[0], data1[1], data1[2], data1[3], data1[4], data1[5])
PRM.push(data2[0], data1[1], data1[2], data1[3]+.1, data1[4], data1[5])
PRM.push(data2[0], data1[1], data1[2], data1[3], data1[4], data1[5])
PRM.push(data1[0]+0.3, data1[1], data1[2], data1[3], data1[4], data1[5])

for i in range(len(PRM.actions_buffer)):
    print(PRM.states_buffer[i], PRM.actions_buffer[i],  PRM.next_states_buffer[i],  PRM.rewards_buffer[i],  PRM.priotity_buffer[i])