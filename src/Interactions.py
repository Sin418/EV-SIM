import json
import math
from Human import Human

class Interactions:
    @staticmethod
    def attack_player(attacker, target_id, all_characters):
        for char in all_characters:
            if char.id == target_id:
                if attacker.weapon:
                    dmg = attacker.weapon.get_damage()
                    char.take_damage(dmg)
                return


    