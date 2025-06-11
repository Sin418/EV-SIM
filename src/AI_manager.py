import torch
import torch.nn as nn
from AI_model import create_ai_model
import random
import numpy as np
from collections import deque
from Human import Human

class AIManager:
    def __init__(self, memory_size=1000, epsilon=1.0, epsilon_min=0.01, decay_rate=0.995, learning_rate=0.001):
        self.models = {}
        self.target_models = {}  # Target networks for stable learning
        self.memory = {}
        self.memory_size = memory_size
        self.rewards = {}
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.decay_rate = decay_rate
        self.learning_rate = learning_rate
        self.batch_size = 32
        self.gamma = 0.99  # Discount factor for future rewards
        self.update_target_every = 100  # Update target network every N steps
        self.steps = 0

    def create_ai_agent(self, agent_id):
        self.models[agent_id] = create_ai_model()
        self.target_models[agent_id] = create_ai_model()
        self.target_models[agent_id].load_state_dict(self.models[agent_id].state_dict())
        self.memory[agent_id] = deque(maxlen=self.memory_size)
        self.rewards[agent_id] = 0
        self.optimizers[agent_id] = torch.optim.Adam(self.models[agent_id].parameters(), lr=self.learning_rate)

    def get_state(self, agent, map_state):
        # Create a state representation for the agent
        agent_x, agent_y = agent.get_position()
        state = []
        
        # Agent's own state
        state.extend([
            agent_x / map_state.width,  # Normalized position
            agent_y / map_state.height,
            agent.get_health() / 100.0,  # Normalized health
            agent.get_weapon().get_health() / 100.0,  # Normalized weapon health
            agent.get_weapon().get_damage() / 30.0,  # Normalized weapon damage
        ])
        
        # Find nearest food and character
        nearest_food_dist = float('inf')
        nearest_char_dist = float('inf')
        
        for food_x, food_y, _ in map_state.food_locations:
            dist = ((food_x - agent_x) ** 2 + (food_y - agent_y) ** 2) ** 0.5
            nearest_food_dist = min(nearest_food_dist, dist)
            
        for char in map_state.characters.values():
            if char.id != agent.id:
                char_x, char_y = char.get_position()
                dist = ((char_x - agent_x) ** 2 + (char_y - agent_y) ** 2) ** 0.5
                nearest_char_dist = min(nearest_char_dist, dist)
        
        # Add normalized distances
        state.extend([
            min(1.0, nearest_food_dist / 500.0),  # Normalize to max 500 units
            min(1.0, nearest_char_dist / 500.0),
        ])
        
        return torch.FloatTensor(state)

    def get_action(self, agent_id, agent, map_state):
        if agent_id not in self.models:
            self.create_ai_agent(agent_id)

        state = self.get_state(agent, map_state)
        
        if random.random() < self.epsilon:
            action = random.randint(0, 2)  # Random action (0=move, 1=attack, 2=eat)
        else:
            with torch.no_grad():
                q_values = self.models[agent_id](state.unsqueeze(0))
                action = torch.argmax(q_values).item()
        
        # Store state and action in memory
        self.memory[agent_id].append((state, action))
        return ['move', 'attack', 'eat'][action]

    def train_agent(self, agent_id):
        if len(self.memory[agent_id]) < self.batch_size:
            return

        # Sample random batch from memory
        batch = random.sample(self.memory[agent_id], self.batch_size)
        states, actions = zip(*batch)
        
        states = torch.stack(states)
        actions = torch.LongTensor(actions)
        
        # Get current Q values
        current_q_values = self.models[agent_id](states)
        next_q_values = self.target_models[agent_id](states).detach()
        
        # Compute target Q values
        target_q_values = current_q_values.clone()
        for i in range(self.batch_size):
            target_q_values[i][actions[i]] = self.rewards[agent_id] + self.gamma * torch.max(next_q_values[i])
        
        # Compute loss and update
        loss = nn.MSELoss()(current_q_values, target_q_values)
        self.optimizers[agent_id].zero_grad()
        loss.backward()
        self.optimizers[agent_id].step()
        
        # Update target network periodically
        self.steps += 1
        if self.steps % self.update_target_every == 0:
            self.target_models[agent_id].load_state_dict(self.models[agent_id].state_dict())

    def evolve_agents(self, num_agents, previous_agents):
        new_agents = []
        # Sort agents by their total reward
        sorted_agents = sorted(previous_agents, key=lambda agent: self.rewards[agent.id], reverse=True)
        top_agents = sorted_agents[:max(1, len(sorted_agents) // 2)]  # Select top 50% agents
        
        print(f"Top agent reward: {self.rewards[top_agents[0].id] if top_agents else 0}")
        
        for i in range(num_agents):
            # Select parent from top agents
            parent_agent = random.choice(top_agents)
            new_agent = Human(f"AI_{random.randint(1, 1000)}", 100, parent_agent.position)
            self.create_ai_agent(new_agent.id)
            
            # Copy and mutate parent's model
            self.models[new_agent.id].load_state_dict(self.models[parent_agent.id].state_dict())
            self.mutate_agent(new_agent.id)
            new_agents.append(new_agent)
            
        return new_agents

    def mutate_agent(self, agent_id):
        mutation_rate = 0.1
        with torch.no_grad():
            for param in self.models[agent_id].parameters():
                # Add random noise to parameters
                noise = torch.randn_like(param) * mutation_rate
                param.add_(noise)
                
                # Occasionally make larger mutations
                if random.random() < 0.1:  # 10% chance of larger mutation
                    param.add_(torch.randn_like(param) * mutation_rate * 5)

    def update_reward(self, agent_id, reward):
        self.rewards[agent_id] += reward
        # Train the agent after receiving a reward
        self.train_agent(agent_id)

    def update_epsilon(self):
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.decay_rate
            self.epsilon = max(self.epsilon_min, self.epsilon)
        print(f"Current epsilon: {self.epsilon:.3f}")  # Debug info

    def remove_ai_agent(self, agent_id):
        if agent_id in self.models:
            del self.models[agent_id]
        if agent_id in self.memory:
            del self.memory[agent_id]
        if agent_id in self.rewards:
            del self.rewards[agent_id]

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
