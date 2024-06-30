# map_state.py
class MapState:
    def __init__(self):
        self.tiles = []

    class Tile:
        def __init__(self, x, y, tile_type, has_top_sprite):
            self.x = x
            self.y = y
            self.tile_type = tile_type
            self.has_top_sprite = has_top_sprite
