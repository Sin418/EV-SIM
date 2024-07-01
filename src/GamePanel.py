import pygame
import random
import math
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
        self.font = pygame.font.SysFont(None, 24)
        self.map_state = MapState()
        self.load_sprites()
        self.generate_background()
        self.generate_top_sprite_positions()
        self.player = Human("Player", 100, (self.PANEL_WIDTH // 2, self.PANEL_HEIGHT // 2))
        self.map_state.add_character(self.player)
        self.map_state.add_character(Human("AI_1", 100, (300, 300)))
        self.map_state.add_character(Human("AI_2", 100, (850, 500)))
        self.character_stats_to_display = []

    def load_sprites(self):
        self.grass_sprites = [pygame.image.load(f"sprites/plain_grass{i+1}.png") for i in range(4)]
        self.water_sprite = pygame.image.load("sprites/plain_water1.png")
        self.top_sprite = pygame.image.load("sprites/plant1.png")
        self.movable_sprite = pygame.image.load("sprites/blue_1.png")
        self.ai_sprite = pygame.image.load("sprites/red_1.png")

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
                self.map_state.add_tile(xPos, yPos, "water" if is_water else "grass")

    def generate_top_sprite_positions(self):
        cols = self.PANEL_WIDTH // self.SPRITE_WIDTH + 2
        rows = self.PANEL_HEIGHT // (self.SPRITE_HEIGHT // 2) + 2
        
        self.top_sprite_positions = [[False for _ in range(cols)] for _ in range(rows)]

        for y in range(rows):
            for x in range(cols):
                if not self.water_positions[y][x] and random.randint(0, 16) == 0:
                    self.top_sprite_positions[y][x] = True
                    self.map_state.update_tile(x * self.SPRITE_WIDTH, y * (self.SPRITE_HEIGHT // 2) - self.SPRITE_HEIGHT // 2, True)

    def handle_player_movement(self, key):
        if key == pygame.K_w:
            self.player.move(0, -5)
        elif key == pygame.K_a:
            self.player.move(-5, 0)
        elif key == pygame.K_s:
            self.player.move(0, 5)
        elif key == pygame.K_d:
            self.player.move(5, 0)
        
        self.map_state.update_character(self.player)

    def handle_character_stats(self, pos):
        chars = self.map_state.characters.values()
        pos_x, pos_y = pos
        self.character_stats_to_display = []

        for char in chars:
            char_x, char_y = char.get_position()
            distance = math.sqrt((pos_x - char_x) ** 2 + (pos_y - char_y) ** 2)
            if distance <= 30:
                self.character_stats_to_display.append(char)

    def handle_interactions(self):
        target_id = self.map_state.attack_check(self.player)
        if target_id:
            target_character = self.map_state.get_character(target_id)
            Interactions.attack_player(self.player, target_id, self.map_state.characters.values())
            self.map_state.update_character(target_character)
            self.map_state.update_character(self.player)

    def draw_character_stats(self):
        y_offset = 50  # Initial y position for the first character's stats
        for char in self.character_stats_to_display:
            stats = f"""Name: {char.get_name()}
Health: {char.get_health()}
Weapon: {char.get_weapon().get_name()}
Weapon Health: {char.get_weapon().get_health()}
Weapon Strength: {char.get_weapon().get_damage()}
Position: {char.get_position()}"""            
            lines = stats.split('\n')
            # Determine the width and height of the rectangle based on the text
            rect_width = 400
            rect_height = len(lines) * 30 + 20
            bg_color = (255, 225, 225)  # Background color
            border_color = (0, 0, 0)    # Border color
            text_color = (0, 0, 0)      # Text color
            padding = 10
            border_width = 3
            
            # Draw background rectangle
            pygame.draw.rect(self.screen, bg_color, pygame.Rect(50, y_offset, rect_width, rect_height), border_radius=10)
            
            # Draw border rectangle
            pygame.draw.rect(self.screen, border_color, pygame.Rect(50, y_offset, rect_width, rect_height), border_radius=10, width=border_width)
            
            for i, line in enumerate(lines):
                text_surface = self.font.render(line.strip(), True, text_color)
                self.screen.blit(text_surface, (60, y_offset + i * 30 + padding))
            y_offset += rect_height + 20  # Update y_offset for the next character's stats


    def run(self):
        running = True
        clock = pygame.time.Clock()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_player_movement(event.key)
                    if event.key == pygame.K_e:
                        self.handle_interactions()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    self.handle_character_stats(pos)

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
            for char_id, char in self.map_state.characters.items():
                if char_id != self.player.id:
                    self.screen.blit(self.ai_sprite, char.position)

            self.draw_character_stats()

            pygame.display.flip()
            clock.tick(60)
        pygame.quit()
