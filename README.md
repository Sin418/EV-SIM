# AIManager

## Overview

`AIManager` manages AI agents in a reinforcement learning environment. It supports agent creation, action selection, agent evolution, and saving/loading models.

## Features

- Create and manage AI agents
- Use epsilon-greedy strategy for action selection
- Evolve agents using genetic algorithms
- Apply mutations to agents
- Save and load agent models

## Installation

```bash
pip install torch
```

## Usage

### Initialize AIManager

```python
from AI_manager import AIManager

ai_manager = AIManager()
```

### Create an Agent

```python
agent_id = 'agent_1'
ai_manager.create_ai_agent(agent_id)
```

### Get Action

```python
state = [0.5, 0.1, -0.3, 0.2]
action = ai_manager.get_action(agent_id, state)
```

### Update Reward

```python
reward = 10
ai_manager.update_reward(agent_id, reward)
```

### Evolve Agents

```python
previous_agents = [...]  # List of previous agents
new_agents = ai_manager.evolve_agents(num_agents=5, previous_agents=previous_agents)
```

### Save and Load Models

```python
ai_manager.save_model(agent_id, 'model.pth')
ai_mana`ger.load_model(agent_id, 'model.pth')
``

