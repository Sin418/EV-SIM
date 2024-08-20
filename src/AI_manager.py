import torch
from AI_model import create_ai_model
import random
from collections import deque
from Human import Human

class AIManager:
    def __init__(self, memory_size=100, epsilon=1.0, epsilon_min=0.01, decay_rate=0.995):
        self.models = {}
        self.memory = {}
        self.memory_size = memory_size
        self.rewards = {}
        self.epsilon = epsilon  # Epsilon for epsilon-greedy strategy
        self.epsilon_min = epsilon_min  # Minimum epsilon value
        self.decay_rate = decay_rate  # Epsilon decay rate

    def create_ai_agent(self, agent_id):
        self.models[agent_id] = create_ai_model()
        self.memory[agent_id] = deque(maxlen=self.memory_size)  # Create a memory buffer for each agent
        self.rewards[agent_id] = 0  # Initialize rewards for each agent

    def update_epsilon(self):
        # Decay epsilon after each generation
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.decay_rate
            self.epsilon = max(self.epsilon_min, self.epsilon)
    
    def get_action(self, agent_id, state):
        if agent_id not in self.models:
            self.create_ai_agent(agent_id)

        # Epsilon-greedy strategy
        if random.random() < self.epsilon:
            action = random.randint(0, 6)  # Random action
        else:
            state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
            action_probs = self.models[agent_id](state_tensor)
            action = torch.argmax(action_probs).item()

        self.memory[agent_id].append((state, action))  # Store state and action in memory
        return action

    def remove_ai_agent(self, agent_id):
        if agent_id in self.models:
            del self.models[agent_id]
        if agent_id in self.memory:
            del self.memory[agent_id]
        if agent_id in self.rewards:
            del self.rewards[agent_id]

    def evolve_agents(self, num_agents, previous_agents):
        new_agents = []
        sorted_agents = sorted(previous_agents, key=lambda agent: self.rewards[agent.id], reverse=True)
        top_agents = sorted_agents[:max(1, len(sorted_agents) // 2)]  # Select top 50% agents

        for i in range(num_agents):
            parent_agent = random.choice(top_agents)
            new_agent = Human(f"AI_{random.randint(1, 1000)}", 100, parent_agent.position)
            self.create_ai_agent(new_agent.id)
            self.mutate_agent(new_agent.id, parent_agent.id)
            new_agents.append(new_agent)
        return new_agents

    def mutate_agent(self, new_agent_id, parent_agent_id):
        mutation_rate = 0.1
        with torch.no_grad():
            for new_param, parent_param in zip(self.models[new_agent_id].parameters(), self.models[parent_agent_id].parameters()):
                new_param.copy_(parent_param + torch.randn(parent_param.size()) * mutation_rate)

    def update_reward(self, agent_id, reward):
        self.rewards[agent_id] += reward

    def save_model(self, agent_id, file_path):
        if agent_id in self.models:
            torch.save(self.models[agent_id].state_dict(), file_path)
        else:
            raise ValueError(f"Model with ID {agent_id} does not exist")

    def load_model(self, agent_id, file_path):
        if agent_id in self.models:
            self.models[agent_id].load_state_dict(torch.load(file_path))
        else:
            raise ValueError(f"Model with ID {agent_id} does not exist")

    def get_top_agents(self, top_n=5):
        sorted_agents = sorted(self.rewards.items(), key=lambda x: x[1], reverse=True)
        return sorted_agents[:top_n]

    def get_agent_statistics(self, agent_id):
        if agent_id in self.models:
            return {
                'epsilon': self.epsilon,
                'reward': self.rewards.get(agent_id, 0),
                'actions_taken': len(self.memory.get(agent_id, []))
            }
        else:
            raise ValueError(f"Model with ID {agent_id} does not exist")
