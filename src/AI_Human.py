from Human import Human
import random
from Weapon import Weapon

class AI_Human(Human):
    def __init__(self, name, health, position):
        super().__init__(name, health, position)
        # Give AI agents a basic weapon
        self.weapon = Weapon("Basic Sword", 100, 10)
        self.id = name  # Use name as ID for AI agents
        
        # Add inventory for resources
        self.inventory = {
            'wood': 0,
            'stone': 0,
            'food': 0
        }
        
        # Building capabilities
        self.building_range = 50
        self.gathering_range = 30
        self.can_build = False  # Will be set to True when they have enough resources
    
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
        
    def add_resource(self, resource_type, amount):
        if resource_type in self.inventory:
            self.inventory[resource_type] += amount
            # Update building capability
            self.can_build = self.inventory['wood'] >= 5 and self.inventory['stone'] >= 3
            
    def use_resource(self, resource_type, amount):
        if resource_type in self.inventory and self.inventory[resource_type] >= amount:
            self.inventory[resource_type] -= amount
            return True
        return False
        
    def can_gather(self, resource_pos):
        """Check if agent is in range to gather a resource"""
        return ((self.position[0] - resource_pos[0])**2 + 
                (self.position[1] - resource_pos[1])**2)**0.5 <= self.gathering_range
                
    def can_build_at(self, build_pos):
        """Check if agent can build at the given position"""
        return (self.can_build and 
                ((self.position[0] - build_pos[0])**2 + 
                 (self.position[1] - build_pos[1])**2)**0.5 <= self.building_range)
    
    
