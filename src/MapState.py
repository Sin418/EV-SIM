import math
from typing import List, Dict, Tuple, Union

class MapState:
    def __init__(self, width: int, height: int):
        self.tiles = []
        self.characters = {}
        self.food_locations = []
        self.width = width
        self.height = height

    class Tile:
        def __init__(self, x: int, y: int, tile_type: str, has_top_sprite: bool = False, attributes: Dict[str, Union[str, int, bool]] = None):
            self.x = x
            self.y = y
            self.tile_type = tile_type
            self.has_top_sprite = has_top_sprite
            self.attributes = attributes if attributes else {}

    class Character:
        def __init__(self, char_id: int, position: Tuple[int, int], health: int, attack_radius: float, inventory: Dict[str, int] = None):
            self.id = char_id
            self.position = position
            self.health = health
            self.attack_radius = attack_radius
            self.inventory = inventory if inventory else {}

        def update_position(self, x: int, y: int):
            self.position = (x, y)

        def update_health(self, amount: int):
            self.health += amount

        def add_to_inventory(self, item: str, quantity: int):
            if item in self.inventory:
                self.inventory[item] += quantity
            else:
                self.inventory[item] = quantity

        def remove_from_inventory(self, item: str, quantity: int):
            if item in self.inventory:
                self.inventory[item] -= quantity
                if self.inventory[item] <= 0:
                    del self.inventory[item]

    def add_tile(self, x: int, y: int, tile_type: str, has_top_sprite: bool = False, attributes: Dict[str, Union[str, int, bool]] = None):
        tile = self.Tile(x, y, tile_type, has_top_sprite, attributes)
        self.tiles.append(tile)

    def update_tile(self, x: int, y: int, has_top_sprite: bool):
        for tile in self.tiles:
            if tile.x == x and tile.y == y:
                tile.has_top_sprite = has_top_sprite
                return

    def add_character(self, character: Character):
        self.characters[character.id] = character

    def update_character(self, character: Character):
        if character.id in self.characters:
            self.characters[character.id] = character

    def remove_character(self, character_id: int):
        if character_id in self.characters:
            del self.characters[character_id]

    def get_character(self, character_id: int) -> Union[Character, None]:
        return self.characters.get(character_id, None)

    def attack_check(self, character: Character) -> Union[int, None]:
        self_x, self_y = character.position
        for char_id, char in self.characters.items():
            if char_id != character.id:
                char_x, char_y = char.position
                distance = math.sqrt((char_x - self_x) ** 2 + (char_y - self_y) ** 2)
                if distance <= character.attack_radius:
                    return char_id
        return None

    def add_food(self, x: int, y: int, food_type: str = "generic"):
        self.food_locations.append((x, y, food_type))

    def remove_food(self, x: int, y: int):
        for i, (fx, fy, _) in enumerate(self.food_locations):
            if fx == x and fy == y:
                del self.food_locations[i]
                return

    def check_food(self, character: Character) -> bool:
        self_x, self_y = character.position
        for food_x, food_y, food_type in self.food_locations:
            distance = math.sqrt((food_x - self_x) ** 2 + (food_y - self_y) ** 2)
            if distance <= 30:
                self.remove_food(food_x, food_y)
                return True
        return False

    def get_game_state(self) -> Dict[str, Union[List[Tuple[int, Tuple[int, int], int]], List[Tuple[int, int, str]]]]:
        state = {
            "characters": [(char.id, char.position, char.health, char.inventory) for char in self.characters.values()],
            "food_locations": [(x, y, food_type) for x, y, food_type in self.food_locations]
        }
        return state

    def to_dict(self) -> Dict[str, Union[List[Dict[str, Union[int, str, bool]]], Dict[int, Dict[str, Union[int, Tuple[int, int], Dict[str, int]]]], List[Tuple[int, int, str]]]]:
        return {
            "tiles": [tile.__dict__ for tile in self.tiles],
            "characters": {char_id: char.__dict__ for char_id, char in self.characters.items()},
            "food_locations": [(x, y, food_type) for x, y, food_type in self.food_locations]
        }
