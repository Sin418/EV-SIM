import json
import math
import uuid
from Weapon import Weapon

class Human:
    def __init__(self, name, health, position):
        self.id = str(uuid.uuid4())  # Generate a unique ID
        self.name = name
        self.health = health
        self.position = position
        self.weapon = Weapon()  # Default to fist
        self.attack_radius = 25  # Define attack radius

    def move(self, x, y):
        self.position = (self.position[0] + x, self.position[1] + y)

    def set_position(self, pos):
        self.position = pos

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
        return self.health <= 0  # Return True if dead

    def equip_weapon(self, weapon):
        self.weapon = weapon

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_health(self):
        return self.health

    def get_position(self):
        return self.position

    def get_attack_radius(self):
        return self.attack_radius

    def get_weapon(self):
        return self.weapon
    
    def set_health(self, new_health):
        self.health = min(100, max(0, new_health))  # Clamp between 0 and 100

    


    
