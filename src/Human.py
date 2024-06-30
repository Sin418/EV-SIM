import json
import math
import uuid

class Human:
    def __init__(self, name, health, position):
        self.id = str(uuid.uuid4())  # Generate a unique ID
        self.name = name
        self.health = health
        self.position = position
        self.weapon = None
        self.attack_radius = 10  # Define attack radius

    def move(self, x, y):
        self.position = (self.position[0] + x, self.position[1] + y)

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def equip_weapon(self, weapon):
        self.weapon = weapon

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
                    return character
        return None

    def attack(self):
        target = self.attack_check()
        if target and self.weapon:
            damage = self.weapon.get_damage()
            target_id = target['id']

            # Update target's health in the JSON file
            with open("state/character_state.json", 'r') as file:
                json_data = json.load(file)

            for character in json_data['characters']:
                if character['id'] == target_id:
                    character['health'] -= damage
                    if character['health'] < 0:
                        character['health'] = 0
                    break

            with open("state/character_state.json", 'w') as file:
                json.dump(json_data, file, indent=4)

            print(f"{self.name} attacked {target['name']} and dealt {damage} damage.")
