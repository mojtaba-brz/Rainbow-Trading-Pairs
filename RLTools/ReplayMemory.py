import torch
import os
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
device = 'cpu'
class PrioritizedReplayMemory():
    # this class duty is to save state, action, next state, reward, done and priority data
    # my solution is to use pytorch and six seperated but synced index Tensors
    def __init__(self, files_dir = "./no_name", alpha : float = 0.5, beta : float = 0.5):
        # files_dir : "folder/.../name"
        # later files will be saved or loaded by _xxx.pt extention
        self.states_dir         = files_dir + "_states.pt"
        self.actions_dir        = files_dir + "_actions.pt"
        self.next_states_dir    = files_dir + "_next_states.pt"
        self.rewards_dir        = files_dir + "_rewards.pt"
        self.dones_dir          = files_dir + "_dones.pt"
        self.priotity_dir       = files_dir + "_priotities.pt"
        self.beta               = beta
        self.alpha              = alpha
        self.offset             = 0.1 # to ensure all samples can be selected
        
        if (os.path.isfile(self.states_dir)         and 
            os.path.isfile(self.actions_dir)        and
            os.path.isfile(self.next_states_dir)    and
            os.path.isfile(self.rewards_dir)        and
            os.path.isfile(self.dones_dir)          and
            os.path.isfile(self.priotity_dir)):
            self.load()
        else:
            self.states_buffer      = torch.zeros(0).to(device)
            self.actions_buffer     = torch.zeros(0, dtype=torch.int8).to(device)
            self.next_states_buffer = torch.zeros(0).to(device)
            self.rewards_buffer     = torch.zeros(0).to(device)
            self.dones_buffer       = torch.zeros(0).to(device)
            self.priotity_buffer    = torch.zeros(0).to(device)
    
    def push(self, current_state, current_action, next_state, reward, done, priority):
        # adds new data to memory
        # inputs must be like Tensor:[[list]]
        if len(current_state.shape) == 1:
            current_state = torch.reshape(current_state, (1, len(current_state)))
            try:
                current_action = torch.reshape(current_action, (1, len(current_action)))
            except TypeError:
                current_action = torch.reshape(current_action, (1, 1))
            next_state = torch.reshape(next_state, (1, len(next_state)))
            reward = torch.reshape(reward, (1, len(reward)))
            done = torch.reshape(done, (1, 1))
            priority = torch.reshape(priority, (1, 1))
        
        current_state = current_state.to(device)
        current_action = current_action.to(device)
        next_state = next_state.to(device)
        reward = reward.to(device)
        done = done.to(device)
        priority = priority.to(device) + self.offset
        idx = None
        if current_state.shape[0] == 1 and len(self.states_buffer) > 0: 
            # a = torch.prod(current_state == self.states_buffer, 1)
            # b = torch.prod(current_action == self.actions_buffer, 1)
            # c = torch.prod(next_state     == self.next_states_buffer, 1)
            # d = torch.prod(reward         == self.rewards_buffer, 1)
            
            idx = (torch.prod(current_state == self.states_buffer, 1)     *
                   torch.prod(current_action == self.actions_buffer, 1)   *
                   torch.prod(next_state     == self.next_states_buffer, 1) *
                   torch.prod(reward         == self.rewards_buffer, 1) ) == 1
        
        if idx is not None and torch.sum(idx):
            self.states_buffer[idx] = current_state
            self.actions_buffer[idx] = current_action
            self.next_states_buffer[idx] = next_state
            self.rewards_buffer[idx] = reward
            self.dones_buffer[idx] = done
            self.priotity_buffer[idx] = priority
        else:    
            self.states_buffer = torch.concat((self.states_buffer, current_state))
            self.actions_buffer = torch.concat((self.actions_buffer, current_action))
            self.next_states_buffer = torch.concat((self.next_states_buffer, next_state))
            self.rewards_buffer = torch.concat((self.rewards_buffer, reward))
            self.dones_buffer = torch.concat((self.dones_buffer, done))
            self.priotity_buffer = torch.concat((self.priotity_buffer, priority))
        
    def sample(self, batch_size, sample_method = 0):
        # kind of pull methode
        n = len(self.states_buffer)
        
        if batch_size > n:
            batch_size = n
            print("batch size was more then data length. it has been saturated to length of data.")
        
        idxs    = torch.multinomial(self.priotity_buffer.t(), batch_size, replacement=True)[0]
        weights = (self.priotity_buffer[idxs] * n) ** -self.beta
        self.new_pririties_idxs = idxs
        return self.states_buffer[idxs], self.actions_buffer[idxs], self.next_states_buffer[idxs], self.rewards_buffer[idxs], self.dones_buffer[idxs], weights
    
    def save(self):
        # saves data to a file
        torch.save(self.states_buffer,      self.states_dir)
        torch.save(self.actions_buffer,     self.actions_dir)
        torch.save(self.next_states_buffer, self.next_states_dir)
        torch.save(self.rewards_buffer,     self.rewards_dir)
        torch.save(self.dones_buffer,       self.dones_dir)
        torch.save(self.priotity_buffer,    self.priotity_dir)
    
    def load(self):
        # loads data from file
        self.states_buffer      = torch.load(self.states_dir).to(device)
        self.actions_buffer     = torch.load(self.actions_dir).to(device)
        self.next_states_buffer = torch.load(self.next_states_dir).to(device)
        self.rewards_buffer     = torch.load(self.rewards_dir).to(device)
        self.dones_buffer       = torch.load(self.dones_dir).to(device)
        self.priotity_buffer    = torch.load(self.priotity_dir).to(device)
        
    def update_pririties_idxs(self, priorities):
        priorities = priorities.to(device)
        idxs = torch.zeros(0, dtype=int).to(device)
        weight = torch.zeros(0).to(device)
        priorities_tensor = torch.zeros(0).to(device)
        for i in range(len(priorities)):
            if self.new_pririties_idxs[i] in idxs:
                idx = self.new_pririties_idxs[i] == idxs
                weight[idx] += 1
                priorities_tensor[idx] += (priorities[i] - priorities_tensor[idx])/weight[idx]
            else:
                idxs = torch.concatenate((idxs, torch.Tensor([self.new_pririties_idxs[i]]).to(device)))
                weight = torch.concatenate((weight, torch.Tensor([1]).to(device)))
                priorities_tensor = torch.concatenate((priorities_tensor, priorities[i]))

        self.priotity_buffer[idxs.to(torch.int64)] = torch.reshape(priorities_tensor, (len(priorities_tensor), 1))
