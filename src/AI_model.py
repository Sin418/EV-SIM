import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import StepLR

class EnhancedAIModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(EnhancedAIModel, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.bn1 = nn.BatchNorm1d(hidden_size)
        self.relu = nn.LeakyReLU(0.01)  # Leaky ReLU activation
        self.dropout1 = nn.Dropout(p=0.5)  # Dropout layer to prevent overfitting

        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.bn2 = nn.BatchNorm1d(hidden_size)
        self.dropout2 = nn.Dropout(p=0.5)  # Dropout layer for the second hidden layer

        self.fc3 = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        x = self.fc1(x)
        x = self.bn1(x)
        x = self.relu(x)
        x = self.dropout1(x)

        x = self.fc2(x)
        x = self.bn2(x)
        x = self.relu(x)
        x = self.dropout2(x)

        x = self.fc3(x)
        return x

def create_enhanced_ai_model():
    input_size = 15  # Updated input size: 2 (position) + 1 (health) + 12 (food positions)
    hidden_size = 128
    output_size = 6  # Output: 6 possible actions (idle, up, down, left, right, attack, eat)
    model = EnhancedAIModel(input_size, hidden_size, output_size)
    return model

# Example setup for training
def setup_training(model):
    criterion = nn.CrossEntropyLoss()  # Assuming classification task
    optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)  # Adam optimizer with weight decay
    scheduler = StepLR(optimizer, step_size=10, gamma=0.7)  # Learning rate scheduler

    return criterion, optimizer, scheduler
