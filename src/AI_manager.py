import torch
import torch.nn as nn
from AI_model import create_ai_model
import random
import numpy as np
from collections import deque
from Human import Human
from AI_Human import AI_Human

class AIManager:
    def __init__(self, memory_size=1000, epsilon=1.0, epsilon_min=0.01, decay_rate=0.995, learning_rate=0.001, width=1600, height=900):
        self.models = {}
        self.optimizers = {}
        self.memory = {}
        self.memory_size = memory_size
        self.rewards = {}
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.decay_rate = decay_rate
        self.learning_rate = learning_rate
        self.batch_size = 32
        self.gamma = 0.95  # Discount factor for future rewards
        self.steps = 0
        self.min_memory_size = 100
        self.generation_rewards = {}  # Track rewards per generation
        self.best_model_state = None  # Store best model state
        self.best_reward = float('-inf')
        self.criterion = nn.MSELoss()
        self.width = width
        self.height = height

    def calculate_distance(self, pos1, pos2):
        """Calculate Euclidean distance between two positions."""
        return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5

    def create_ai_agent(self, agent_id):
        self.models[agent_id] = create_ai_model()
        self.optimizers[agent_id] = torch.optim.Adam(self.models[agent_id].parameters(), lr=self.learning_rate)
        self.memory[agent_id] = deque(maxlen=self.memory_size)
        self.rewards[agent_id] = 0

    def get_state(self, agent, agents, food_items):
        # Enhanced state representation with 15 dimensions
        state = []
        
        # Agent's own state (3 dimensions)
        state.append(agent.health / 100.0)  # Normalized health
        state.append(agent.position[0] / self.width)  # Normalized x position
        state.append(agent.position[1] / self.height)  # Normalized y position
        
        # Resource information (3 dimensions)
        wood_count = agent.inventory.get('wood', 0)
        stone_count = agent.inventory.get('stone', 0)
        food_count = agent.inventory.get('food', 0)
        state.append(min(1.0, wood_count / 20.0))  # Normalized wood count
        state.append(min(1.0, stone_count / 20.0))  # Normalized stone count
        state.append(min(1.0, food_count / 10.0))  # Normalized food count
        
        # Food-related information (3 dimensions)
        closest_food_dist = float('inf')
        closest_food_angle = 0.0
        food_count = 0
        
        for food in food_items:
            dist = self.calculate_distance(agent.position, food.position)
            if dist < closest_food_dist:
                closest_food_dist = dist
                dx = food.position[0] - agent.position[0]
                dy = food.position[1] - agent.position[1]
                closest_food_angle = np.arctan2(dy, dx) / np.pi
            food_count += 1
        
        state.append(min(1.0, closest_food_dist / 2200.0))
        state.append(closest_food_angle)
        state.append(min(1.0, food_count / 10.0))
        
        # Agent-related information (3 dimensions)
        closest_agent_dist = float('inf')
        closest_agent_angle = 0.0
        agent_count = 0
        
        for other in agents:
            if other.id != agent.id:
                dist = self.calculate_distance(agent.position, other.position)
                if dist < closest_agent_dist:
                    closest_agent_dist = dist
                    dx = other.position[0] - agent.position[0]
                    dy = other.position[1] - agent.position[1]
                    closest_agent_angle = np.arctan2(dy, dx) / np.pi
                agent_count += 1
        
        state.append(min(1.0, closest_agent_dist / 2200.0))
        state.append(closest_agent_angle)
        state.append(min(1.0, agent_count / 10.0))
        
        # Environment information (3 dimensions)
        state.append(agent.position[0] / self.width)  # Distance from left edge
        state.append((self.width - agent.position[0]) / self.width)  # Distance from right edge
        state.append(min(agent.position[1] / self.height, (self.height - agent.position[1]) / self.height))
        
        return torch.FloatTensor(state)

    def calculate_reward(self, agent, action, agents, food_items):
        reward = 0.0
        
        # Base reward for being alive
        reward += 0.1
        
        # Penalty for low health
        if agent.health < 30:
            reward -= 0.2
        
        # Small penalty for any action to encourage efficiency
        reward -= 0.05
        
        # Resource gathering rewards
        if action == 1:  # Eat/Gather action
            if agent.inventory.get('wood', 0) > 0:
                reward += 0.2  # Reward for gathering wood
            if agent.inventory.get('stone', 0) > 0:
                reward += 0.3  # Reward for gathering stone
            if agent.inventory.get('food', 0) > 0:
                reward += 0.4  # Reward for gathering food
        
        # Building rewards
        if action == 3 and agent.can_build:  # Build action
            reward += 0.5  # Reward for successful building
        
        # If agent died, large negative reward
        if agent.health <= 0:
            reward = -10.0
            
        return reward

    def get_action(self, agent_id, agent, map_state):
        if agent_id not in self.models:
            self.create_ai_agent(agent_id)

        state = self.get_state(agent, map_state.agents, map_state.food_items)
        
        # Epsilon-greedy action selection
        if random.random() < self.epsilon:
            action = random.randint(0, 3)  # Random action (0: move, 1: eat, 2: attack, 3: reproduce)
        else:
            with torch.no_grad():
                q_values = self.models[agent_id](state.unsqueeze(0))
                action = torch.argmax(q_values).item()
        
        return action, state  # Return both action and state

    def can_reproduce(self, agent, map_state):
        # Only check if agent has enough health
        return agent.health >= 70

    def reproduce(self, agent, map_state):
        if not self.can_reproduce(agent, map_state):
            return None
            
        # Create new agent with combined traits
        x, y = agent.position
        new_agent = AI_Human(f"AI_{random.randint(1, 1000)}", 50, 
                           (x + random.randint(-20, 20), y + random.randint(-20, 20)))
        
        # Create new AI model for the child
        self.create_ai_agent(new_agent.id)
        
        # Combine parent's model with mutation
        parent_state = self.models[agent.id].state_dict()
        child_state = self.models[new_agent.id].state_dict()
        
        # Mix parameters from parent with mutation
        for key in parent_state:
            if random.random() < 0.5:  # 50% chance to inherit from parent
                child_state[key] = parent_state[key]
            # Always add some mutation
            child_state[key] += torch.randn_like(child_state[key]) * 0.1
            
        self.models[new_agent.id].load_state_dict(child_state)
        
        # Parent loses health
        agent.health -= 40
        
        return new_agent

    def train_agent(self, agent_id):
        if agent_id not in self.memory:
            return
            
        if len(self.memory[agent_id]) < self.batch_size:
            return
            
        # Sample random batch from memory
        batch = random.sample(self.memory[agent_id], self.batch_size)
        
        # Prepare batch data
        states = torch.stack([x[0] for x in batch])
        actions = torch.tensor([x[1] for x in batch], dtype=torch.long)
        rewards = torch.tensor([x[2] for x in batch], dtype=torch.float)
        next_states = torch.stack([x[3] for x in batch])
        dones = torch.tensor([x[4] for x in batch], dtype=torch.float)
        
        # Get current Q values
        current_q_values = self.models[agent_id](states).gather(1, actions.unsqueeze(1))
        
        # Get next Q values
        with torch.no_grad():
            next_q_values = self.models[agent_id](next_states).max(1)[0]
            target_q_values = rewards + (1 - dones) * self.gamma * next_q_values
            
        # Compute loss and update
        loss = self.criterion(current_q_values.squeeze(), target_q_values)
        self.optimizers[agent_id].zero_grad()
        loss.backward()
        self.optimizers[agent_id].step()
        
        # Don't clear memory after training - keep experiences for future learning

    def update_reward(self, agent_id, reward):
        # Simple reward update without decay
        self.rewards[agent_id] += reward
        # Train the agent
        self.train_agent(agent_id)

    def evolve_agents(self, num_agents, previous_agents):
        new_agents = []
        
        # Handle case when all agents died
        if not previous_agents:
            print("All agents died. Starting fresh generation...")
            for i in range(num_agents):
                new_agent = AI_Human(f"AI_{random.randint(1, 1000)}", 100, 
                    (random.randint(0, 1920), random.randint(0, 1080)))
                self.create_ai_agent(new_agent.id)
                new_agents.append(new_agent)
            return new_agents

        # Sort agents by their total reward
        sorted_agents = sorted(previous_agents, key=lambda agent: self.rewards[agent.id], reverse=True)
        
        # Store best model if it's better than previous best
        if sorted_agents and self.rewards[sorted_agents[0].id] > self.best_reward:
            self.best_reward = self.rewards[sorted_agents[0].id]
            self.best_model_state = self.models[sorted_agents[0].id].state_dict()
        
        # Keep top 20% of agents for next generation
        top_agents = sorted_agents[:max(1, len(sorted_agents) // 5)]
        
        # Calculate and print generation statistics
        avg_reward = sum(self.rewards[agent.id] for agent in previous_agents) / len(previous_agents)
        print(f"\nGeneration stats:")
        print(f"Top agent reward: {self.rewards[top_agents[0].id]:.2f}")
        print(f"Average reward: {avg_reward:.2f}")
        print(f"Number of agents: {len(previous_agents)}")
        
        for i in range(num_agents):
            # 70% chance to use best model as parent, 30% chance to use random top agent
            if self.best_model_state and random.random() < 0.7:
                parent_agent = random.choice(top_agents)
                new_agent = AI_Human(f"AI_{random.randint(1, 1000)}", 100, parent_agent.position)
                self.create_ai_agent(new_agent.id)
                self.models[new_agent.id].load_state_dict(self.best_model_state)
            else:
                parent_agent = random.choice(top_agents)
                new_agent = AI_Human(f"AI_{random.randint(1, 1000)}", 100, parent_agent.position)
                self.create_ai_agent(new_agent.id)
                self.models[new_agent.id].load_state_dict(self.models[parent_agent.id].state_dict())
            
            # Mutate the new agent
            self.mutate_agent(new_agent.id)
            new_agents.append(new_agent)
        
        # Reset rewards for new generation
        self.rewards = {agent.id: 0 for agent in new_agents}
        return new_agents

    def mutate_agent(self, agent_id):
        mutation_rate = 0.05  # Slightly higher mutation rate since we're learning from scratch
        with torch.no_grad():
            for param in self.models[agent_id].parameters():
                # Add random noise to parameters
                noise = torch.randn_like(param) * mutation_rate
                param.add_(noise)
                
                # Occasionally make larger mutations (10% chance)
                if random.random() < 0.1:
                    param.add_(torch.randn_like(param) * mutation_rate * 2)

    def update_epsilon(self):
        # Slower epsilon decay for better exploration
        if self.epsilon > self.epsilon_min:
            self.epsilon *= 0.999
            self.epsilon = max(self.epsilon_min, self.epsilon)
        print(f"Current epsilon: {self.epsilon:.3f}")

    def remove_ai_agent(self, agent_id):
        if agent_id in self.models:
            del self.models[agent_id]
            del self.optimizers[agent_id]
            if agent_id in self.memory:
                del self.memory[agent_id]
            if agent_id in self.rewards:
                del self.rewards[agent_id]
        else:
            raise ValueError(f"Model with ID {agent_id} does not exist")

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

    def store_experience(self, agent_id, state, action, reward, next_state, done):
        """Store a complete experience tuple in the agent's memory."""
        if agent_id not in self.memory:
            self.memory[agent_id] = deque(maxlen=self.memory_size)
        self.memory[agent_id].append((state, action, reward, next_state, done))
