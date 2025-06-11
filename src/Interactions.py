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
                    # Weapon takes damage too
                    attacker.weapon.take_damage(1)
                    return True
        return False

    @staticmethod
    def eat_food(character, food_positions):
        char_x, char_y = character.get_position()
        for food_pos in list(food_positions):
            food_x, food_y, _ = food_pos  # Unpack all three values but ignore food_type
            distance = math.sqrt((char_x - food_x) ** 2 + (char_y - food_y) ** 2)
            if distance < 30:  # If within eating range
                food_positions.remove(food_pos)
                character.set_health(min(100, character.get_health() + 20))  # Heal up to 100
                return True
        return False

    @staticmethod
    def is_in_range(pos1, pos2, range=30):
        x1, y1 = pos1
        x2, y2 = pos2
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) < range


    