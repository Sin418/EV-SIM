import random

class Weapon:
    def __init__(self, name="fist", health=150, damage=5):
        self.name = name
        self.health = health
        self.damage = damage
        self.fist = name == "fist"

    def get_name(self):
        return self.name

    def get_health(self):
        return self.health

    def get_damage(self):
        return self.damage

    def get_fist(self):
        return self.fist

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        return self.health <= 0  # Return True if weapon is broken
