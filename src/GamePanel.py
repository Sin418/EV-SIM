import pygame
import random
import math
import torch
from MapState import MapState
from Human import Human
from AI_Human import AI_Human
from Interactions import Interactions
from AI_manager import AIManager  # Import AIManager

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
        self.TARGET_FOOD_COUNT = 20
        self.generate_food_positions(self.TARGET_FOOD_COUNT)
        self.ai_manager = AIManager(epsilon=0.1)
        self.generation = 1
        self.spawn_ai_agents(5)
        self.character_stats_to_display = []
        self.last_health_decrease_time = pygame.time.get_ticks()

    def load_sprites(self):
        self.grass_sprites = [pygame.image.load(f"sprites/plain_grass{i+1}.png") for i in range(4)]
        self.water_sprite = pygame.image.load("sprites/plain_water1.png")
        self.food_sprite = pygame.image.load("sprites/plant1.png")
        self.movable_sprite = pygame.image.load("sprites/blue_1.png")
        self.ai_sprite = pygame.image.load("sprites/red_1.png")

    def generate_background(self):
        self.background = pygame.Surface((self.PANEL_WIDTH, self.PANEL_HEIGHT))
        cols = self.PANEL_WIDTH // self.SPRITE_WIDTH + 2
        rows = self.PANEL_HEIGHT // (self.SPRITE_HEIGHT // 2) + 2
        self.water_positions = [[False for _ in range(cols)] for _ in range(rows)]

        for y in range(rows):
            yPos = y * (self.SPRITE_HEIGHT // 2) - self.SPRITE_HEIGHT // 2
            for x in range(cols):
                xPos = x * self.SPRITE_WIDTH
                if y % 2 != 0:
                    xPos -= self.SPRITE_WIDTH // 2
                is_water = random.randint(0, 11) == 0
                bottom_sprite = self.water_sprite if is_water else random.choice(self.grass_sprites)
                self.water_positions[y][x] = is_water
                self.background.blit(bottom_sprite, (xPos, yPos))
                self.map_state.add_tile(xPos, yPos, "water" if is_water else "grass")

    def generate_food_positions(self, target_count):
        while len(self.map_state.food_locations) < target_count:
            xPos = random.randint(0, self.PANEL_WIDTH - self.SPRITE_WIDTH)
            yPos = random.randint(0, self.PANEL_HEIGHT - self.SPRITE_HEIGHT)
            tile_x = xPos // self.SPRITE_WIDTH
            tile_y = yPos // (self.SPRITE_HEIGHT // 2)
            if not self.water_positions[tile_y][tile_x]:
                self.map_state.add_food(xPos, yPos)

    def replenish_food(self):
        current_food_count = len(self.map_state.food_locations)
        if current_food_count < self.TARGET_FOOD_COUNT - 5:
            self.generate_food_positions(self.TARGET_FOOD_COUNT)

    def spawn_ai_agents(self, num_agents):
        for i in range(num_agents):
            x = random.randint(0, self.PANEL_WIDTH - self.SPRITE_WIDTH)
            y = random.randint(0, self.PANEL_HEIGHT - self.SPRITE_HEIGHT)
            ai_agent = AI_Human(f"AI_{i+1}", 100, (x, y))
            self.map_state.add_character(ai_agent)
            self.ai_manager.create_ai_agent(ai_agent.id)

    def handle_character_stats(self, pos):
        chars = self.map_state.characters.values()
        pos_x, pos_y = pos
        self.character_stats_to_display = []

        for char in chars:
            char_x, char_y = char.get_position()
            distance = math.sqrt((pos_x - char_x) ** 2 + (pos_y - char_y) ** 2)
            if distance <= 30:
                self.character_stats_to_display.append(char)

    def handle_attack_interactions(self):
        for char in list(self.map_state.characters.values()):
            target_id = self.map_state.attack_check(char)
            if target_id:
                target_character = self.map_state.get_character(target_id)
                Interactions.attack_player(char, target_id, self.map_state.characters.values())
                self.map_state.update_character(target_character)
                self.map_state.update_character(char)
                self.ai_manager.update_reward(char.id, 10)  # Reward for attacking
        self.check_and_remove_characters()

    def handle_eating_interactions(self):
        for char in list(self.map_state.characters.values()):
            if self.map_state.check_food(char):
                char.set_health(char.get_health() + 10)
                self.map_state.update_character(char)
                self.ai_manager.update_reward(char.id, 20)  # Reward for eating food

    def draw_character_stats(self):
        y_offset = 50
        for char in self.character_stats_to_display:
            stats = f"""Name: {char.get_name()}
Health: {char.get_health()}
Weapon: {char.get_weapon().get_name()}
Weapon Health: {char.get_weapon().get_health()}
Weapon Strength: {char.get_weapon().get_damage()}
Position: {char.get_position()}"""
            lines = stats.split('\n')

            rect_width = 400
            rect_height = len(lines) * 30 + 20
            bg_color = (255, 225, 225)
            border_color = (0, 0, 0)
            text_color = (0, 0, 0)
            padding = 10
            border_width = 3

            pygame.draw.rect(self.screen, bg_color, pygame.Rect(50, y_offset, rect_width, rect_height), border_radius=10)
            pygame.draw.rect(self.screen, border_color, pygame.Rect(50, y_offset, rect_width, rect_height), border_radius=10, width=border_width)

            for i, line in enumerate(lines):
                text_surface = self.font.render(line.strip(), True, text_color)
                self.screen.blit(text_surface, (60, y_offset + i * 30 + padding))
            y_offset += rect_height + 20

    def decrease_health(self, value):
        chars_to_remove = []
        for char_id, char in list(self.map_state.characters.items()):
            char.set_health(char.get_health() - value)
            if char.get_health() <= 0:
                chars_to_remove.append(char_id)
        for char_id in chars_to_remove:
            self.map_state.remove_character(char_id)
            self.ai_manager.remove_ai_agent(char_id)

    def check_and_remove_characters(self):
        chars_to_remove = [char_id for char_id, char in list(self.map_state.characters.items()) if char.get_health() <= 0]
        for char_id in chars_to_remove:
            self.map_state.remove_character(char_id)
            self.ai_manager.remove_ai_agent(char_id)

    def draw_food_sprites(self):
        for (x, y) in self.map_state.food_locations:
            self.screen.blit(self.food_sprite, (x + 15, y))

    def draw_characters(self):
        for char in self.map_state.characters.values():
            self.screen.blit(self.ai_sprite, char.position)

    def all_agents_dead(self):
        return len(self.map_state.characters) == 0

    def create_new_generation(self):
        previous_agents = list(self.map_state.characters.values())
        num_agents = len(previous_agents)
        new_agents = self.ai_manager.evolve_agents(num_agents, previous_agents)
        self.map_state.characters = {}
        for agent in new_agents:
            self.map_state.add_character(agent)
        self.generation += 1
        self.ai_manager.update_epsilon()
        print(f"Generation {self.generation} created, epsilon: {self.ai_manager.epsilon}")

    def handle_ai_actions(self):
        for char in self.map_state.characters.values():
            if isinstance(char, AI_Human):
                action = self.ai_manager.get_action(char.id)
                if action == 'move':
                    self.move_ai_agent(char)
                elif action == 'attack':
                    self.attack_with_ai_agent(char)
                elif action == 'eat':
                    self.eat_with_ai_agent(char)

    def move_ai_agent(self, agent):
        x, y = agent.position
        x += random.randint(-10, 10)
        y += random.randint(-10, 10)
        x = max(0, min(x, self.PANEL_WIDTH - self.SPRITE_WIDTH))
        y = max(0, min(y, self.PANEL_HEIGHT - self.SPRITE_HEIGHT))
        agent.position = (x, y)
        self.map_state.update_character(agent)

    def attack_with_ai_agent(self, agent):
        target_id = self.map_state.attack_check(agent)
        if target_id:
            target_character = self.map_state.get_character(target_id)
            Interactions.attack_player(agent, target_id, self.map_state.characters.values())
            self.map_state.update_character(target_character)
            self.map_state.update_character(agent)
            self.ai_manager.update_reward(agent.id, 10)

    def eat_with_ai_agent(self, agent):
        if self.map_state.check_food(agent):
            agent.set_health(agent.get_health() + 10)
            self.map_state.update_character(agent)
            self.ai_manager.update_reward(agent.id, 20)

    def game_loop(self):
        running = True
        clock = pygame.time.Clock()
        while running:
            self.handle_ai_actions()
            self.handle_attack_interactions()
            self.handle_eating_interactions()
            self.replenish_food()
            if self.all_agents_dead():
                self.create_new_generation()

            self.screen.blit(self.background, (0, 0))
            self.draw_food_sprites()
            self.draw_characters()
            self.draw_character_stats()
            pygame.display.flip()
            clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    self.handle_character_stats(pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_d:
                        current_time = pygame.time.get_ticks()
                        if current_time - self.last_health_decrease_time > 5000:  # 5 seconds
                            self.decrease_health(10)
                            self.last_health_decrease_time = current_time

        pygame.quit()
