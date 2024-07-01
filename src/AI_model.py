import torch
import torch.nn as nn
import torch.optim as optim

class AIModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(AIModel, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        return out

def create_ai_model():
    input_size = 15  # Updated input size: 2 (position) + 1 (health) + 12 (food positions)
    hidden_size = 128
    output_size = 6  # Output: 6 possible actions (idle, up, down, left, right, attack, eat)
    model = AIModel(input_size, hidden_size, output_size)
    return model
