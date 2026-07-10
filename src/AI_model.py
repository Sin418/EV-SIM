import torch
import torch.nn as nn
import torch.optim as optim

class EnhancedAIModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(EnhancedAIModel, self).__init__()
        # Larger network with dropout for better learning
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size * 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size * 2, hidden_size * 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size * 2, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size)
        )
        
        # Initialize weights for better learning
        for layer in self.network:
            if isinstance(layer, nn.Linear):
                nn.init.kaiming_normal_(layer.weight, nonlinearity='relu')
                nn.init.zeros_(layer.bias)
    
    def forward(self, x):
        return self.network(x)

def create_ai_model():
    input_size = 15  # Increased state representation to include resources
    hidden_size = 64
    output_size = 5  # Added building action (0: move, 1: eat/gather, 2: attack, 3: build, 4: reproduce)
    model = EnhancedAIModel(input_size, hidden_size, output_size)
    return model

def setup_training(model):
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    return optimizer
