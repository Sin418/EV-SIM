import pygame
import json
import random
from MapState import MapState
from Human import Human
from AI_Human import AI_Human
from Interactions import Interactions
class GamePanel:
    SPRITE_WIDTH = 64
    SPRITE_HEIGHT = 31
    PANEL_WIDTH = 1920
    PANEL_HEIGHT = 1080

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.PANEL_WIDTH, self.PANEL_HEIGHT))
        self.load_sprites()
        self.generate_background()
        self.generate_top_sprite_positions()
        self.player = Human("Player", 100, (self.PANEL_WIDTH // 2, self.PANEL_HEIGHT // 2))
        self.map_state = MapState()
        self.all_characters = [
            self.player,
            Human("AI_1", 100, (300, 300)),
            Human("AI_2", 100, (850, 500))
        ]
    def load_sprites(self):
        self.grass_sprites = [pygame.image.load(f"sprites/plain_grass{i+1}.png") for i in range(4)]
        self.water_sprite = pygame.image.load("sprites/plain_water1.png")
        self.top_sprite = pygame.image.load("sprites/plant1.png")
        self.movable_sprite = pygame.image.load("sprites/blue_1.png")
        self.ai_sprite = pygame.image.load("sprites/red_1.png")  # Add a different sprite for AI

    def generate_background(self):
        self.background = pygame.Surface((self.PANEL_WIDTH, self.PANEL_HEIGHT))
        cols = self.PANEL_WIDTH // self.SPRITE_WIDTH + 2
        rows = self.PANEL_HEIGHT // (self.SPRITE_HEIGHT // 2) + 2
        self.water_positions = [[False for _ in range(cols)] for _ in range(rows)]

        for y in range(rows):
            for x in range(cols):
                xPos = x * self.SPRITE_WIDTH
                yPos = y * (self.SPRITE_HEIGHT // 2) - self.SPRITE_HEIGHT // 2
                if y % 2 != 0:
                    xPos -= self.SPRITE_WIDTH // 2
                is_water = random.randint(0, 11) == 0
                bottom_sprite = self.water_sprite if is_water else random.choice(self.grass_sprites)
                self.water_positions[y][x] = is_water
                self.background.blit(bottom_sprite, (xPos, yPos))

    def generate_top_sprite_positions(self):
        cols = self.PANEL_WIDTH // self.SPRITE_WIDTH + 2
        rows = self.PANEL_HEIGHT // (self.SPRITE_HEIGHT // 2) + 2
        self.top_sprite_positions = [[False for _ in range(cols)] for _ in range(rows)]

        for y in range(rows):
            for x in range(cols):
                if not self.water_positions[y][x] and random.randint(0, 16) == 0:
                    self.top_sprite_positions[y][x] = True

    def save_character_state_to_json(self, filename):
        character_positions = [{
            "id": char.id,
            "name": char.name,
            "health": char.health,
            "x": char.position[0],
            "y": char.position[1]
        } for char in self.all_characters]
        
        data = {"characters": character_positions}

        with open(filename, "w") as file:
            json.dump(data, file, indent=4)

    def save_map_state_to_json(self, filename):
        tiles = []
        cols = self.PANEL_WIDTH // self.SPRITE_WIDTH + 2
        rows = self.PANEL_HEIGHT // (self.SPRITE_HEIGHT // 2) + 2

        for y in range(rows):
            for x in range(cols):
                xPos = x * self.SPRITE_WIDTH
                yPos = y * (self.SPRITE_HEIGHT // 2) - self.SPRITE_HEIGHT // 2
                if y % 2 != 0:
                    xPos -= self.SPRITE_WIDTH // 2
                tile_type = "water" if self.water_positions[y][x] else "grass"
                has_top_sprite = self.top_sprite_positions[y][x]
                tiles.append({"x": xPos, "y": yPos, "type": tile_type, "hasTopSprite": has_top_sprite})

        character_positions = [{
            "id": char.id,
            "name": char.name,
            "health": char.health,
            "x": char.position[0],
            "y": char.position[1]
        } for char in self.all_characters]
        
        data = {"tiles": tiles, "characters": character_positions}

        with open(filename, "w") as file:
            json.dump(data, file, indent=4)

    def run(self):
        self.save_map_state_to_json("state/map_state.json")
        running = True
        clock = pygame.time.Clock()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self.save_character_state_to_json("state/character_state.json")
                    if event.key == pygame.K_w:
                        self.player.move(0, -5)
                    elif event.key == pygame.K_a:
                        self.player.move(-5, 0)
                    elif event.key == pygame.K_s:
                        self.player.move(0, 5)
                    elif event.key == pygame.K_d:
                        self.player.move(5, 0)
                    elif event.key == pygame.K_e:
                        target_id = self.player.attack_check()
                        if target_id:
                            Interactions.attack_player(self.player, target_id, self.all_characters)

        

            self.screen.blit(self.background, (0, 0))
            for y in range(len(self.top_sprite_positions)):
                for x in range(len(self.top_sprite_positions[0])):
                    if self.top_sprite_positions[y][x]:
                        xPos = x * self.SPRITE_WIDTH
                        yPos = y * (self.SPRITE_HEIGHT // 2) - self.SPRITE_HEIGHT // 2
                        if y % 2 != 0:
                            xPos -= self.SPRITE_WIDTH // 2
                        self.screen.blit(self.top_sprite, (xPos, yPos))

            self.screen.blit(self.movable_sprite, self.player.position)
            for ai in self.all_characters:
                self.screen.blit(self.ai_sprite, ai.position)

            pygame.display.flip()
            clock.tick(60)
        pygame.quit()
