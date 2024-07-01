import random

class Weapon:
    def __init__(self, has_weapon):
        if has_weapon:
            self.health = random.randint(6, 10)
            self.damage = random.randint(20, 30)
            self.fist = False
        else:
            self.health = 150
            self.damage = random.randint(5,10)
            self.fist = True
    def get_name(self):
        if self.fist:
            return 'fist'
        else:
            return 'sword'

    def get_health(self):
        return self.health

    def get_damage(self):
        return self.damage

    def get_fist(self):
        return self.fist
