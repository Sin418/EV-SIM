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
        self.weapon = Weapon(False)
        self.attack_radius = 25  # Define attack radius

        

    def move(self, x, y):
        self.position = (self.position[0] + x, self.position[1] + y)

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

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
        self.health = new_health 

    def attack_check(self):
        with open("state/character_state.json", 'r') as file:
            json_data = json.load(file)

        self_x, self_y = self.position
        for character in json_data['characters']:
            if character['id'] != self.id:
                character_x = character['x']
                character_y = character['y']
                distance = math.sqrt((character_x - self_x) ** 2 + (character_y - self_y) ** 2)
                if distance <= self.attack_radius:
                    return character['id']
        return None


    
