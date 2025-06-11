from Human import Human
import random
from Weapon import Weapon

class AI_Human(Human):
    def __init__(self, name, health, position):
        super().__init__(name, health, position)
        # Give AI agents a basic weapon
        self.weapon = Weapon("Basic Sword", 100, 10)
        self.id = name  # Use name as ID for AI agents
    
    def get_position(self):
        return self.position
    
    def set_position(self, pos):
        self.position = pos
    
    def get_health(self):
        return self.health
    
    def set_health(self, value):
        self.health = value
    
    def get_weapon(self):
        return self.weapon
    
    def get_name(self):
        return self.name
    
    def take_damage(self, amount):
        self.health -= amount
        return self.health <= 0  # Return True if dead
    
    
