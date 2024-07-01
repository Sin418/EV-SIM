import math
class MapState:
    def __init__(self):
        self.tiles = []
        self.characters = {}
        self.food_locations = []

    class Tile:
        def __init__(self, x, y, tile_type, has_top_sprite):
            self.x = x
            self.y = y
            self.tile_type = tile_type
            self.has_top_sprite = has_top_sprite

    def add_tile(self, x, y, tile_type, has_top_sprite=False):
        tile = self.Tile(x, y, tile_type, has_top_sprite)
        self.tiles.append(tile)

    def update_tile(self, x, y, has_top_sprite):
        for tile in self.tiles:
            if tile.x == x and tile.y == y:
                tile.has_top_sprite = has_top_sprite
                return

    def add_character(self, character):
        self.characters[character.id] = character

    def update_character(self, character):
        if character.id in self.characters:
            self.characters[character.id] = character

    def remove_character(self, character_id):
        if character_id in self.characters:
            del self.characters[character_id]

    def get_character(self, character_id):
        return self.characters.get(character_id, None)

    def attack_check(self, character):
        self_x, self_y = character.position
        for char_id, char in self.characters.items():
            if char_id != character.id:
                char_x, char_y = char.position
                distance = math.sqrt((char_x - self_x) ** 2 + (char_y - self_y) ** 2)
                if distance <= character.attack_radius:
                    return char_id
        return None

    def add_food(self, x, y):
        self.food_locations.append((x, y))

    def remove_food(self, x, y):
        if (x, y) in self.food_locations:
            self.food_locations.remove((x, y))

    def check_food(self, character):
        self_x, self_y = character.position
        for food_x, food_y in self.food_locations:
            distance = math.sqrt((food_x - self_x) ** 2 + (food_y - self_y) ** 2)
            if distance <= 30:
                self.remove_food(food_x, food_y)
                return True
        return False

    def get_game_state(self):
        state = {
            "characters": [(char.id, char.position, char.health) for char in self.characters.values()],
            "food_locations": self.food_locations
        }
        return state

    def to_dict(self):
        return {
            "tiles": [tile.__dict__ for tile in self.tiles],
            "characters": {char_id: char.__dict__ for char_id, char in self.characters.items()},
            "food_locations": self.food_locations
        }
