from Human import Human
import random

class AI_Human(Human):
    def __init__(self, name, health, position):
        super().__init__(name, health, position)
    
    def ai_move(self):
        # Simple AI movement logic: random movement
        directions = [(0, 0), (0, 0), (0, 0), (0, 0)]
        move = random.choice(directions)
        self.move(*move)
