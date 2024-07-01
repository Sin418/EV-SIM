# ai_manager.py

import torch
from AI_model import create_ai_model
import random
from collections import deque
from Human import Human
class AIManager:
    def __init__(self, memory_size=100):
        self.models = {}
        self.memory = {}
        self.memory_size = memory_size

    def create_ai_agent(self, agent_id):
        self.models[agent_id] = create_ai_model()
        self.memory[agent_id] = deque(maxlen=self.memory_size)  # Create a memory buffer for each agent

    def get_action(self, agent_id, state):
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

    def evolve_agents(self, num_agents, previous_agents):
        new_agents = []
        for i in range(num_agents):
            parent_agent = random.choice(previous_agents)
            new_agent = Human(f"AI_{random.randint(1, 1000)}", 100, parent_agent.position)
            self.create_ai_agent(new_agent.id)
            self.mutate_agent(new_agent.id)
            new_agents.append(new_agent)
        return new_agents

    def mutate_agent(self, agent_id):
        mutation_rate = 0.1
        with torch.no_grad():
            for param in self.models[agent_id].parameters():
                param.add_(torch.randn(param.size()) * mutation_rate)
