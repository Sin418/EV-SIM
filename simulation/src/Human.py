from Weapon import Weapon
import random

class Human:
    def __init__(self, name, health, position):
        self.name = name
        self.health = health
        self.position = position
        self.weapon = Weapon(False)
        #this is 10 px for seeing if enemy is near
        self.awearness = 10
    def move(self, x, y):
        self.position = (self.position[0] + x, self.position[1] + y)

    def attack(self, target):
        if self.weapon:
            damage = self.weapon.get_damage()
            target.take_damage(damage)

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0

    def equip_weapon(self, weapon):
        self.weapon = weapon
