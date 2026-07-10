import pygame
import random
import math
import torch
from MapState import MapState
from Human import Human
from AI_Human import AI_Human
from Interactions import Interactions
from AI_manager import AIManager  # Fix to use correct class name
from Food import Food  # Add this import
import time

class GamePanel:
    # Base dimensions for 16:9 ratio - increased map size
    BASE_WIDTH = 2400
    BASE_HEIGHT = 1350
    SPRITE_WIDTH = 64
    SPRITE_HEIGHT = 31
    UI_SCALE = 0.7  # Scale down UI elements
    MIN_ZOOM = 0.5
    MAX_ZOOM = 2.0

    def __init__(self):
        pygame.init()
        
        # Get the screen info
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h
        
        # Calculate scale factor to fit screen while maintaining aspect ratio
        width_scale = screen_width / self.BASE_WIDTH
        height_scale = screen_height / self.BASE_HEIGHT
        self.scale_factor = min(width_scale, height_scale) * 0.95  # 95% of screen size
        
        # Calculate actual game dimensions
        self.width = int(self.BASE_WIDTH * self.scale_factor)
        self.height = int(self.BASE_HEIGHT * self.scale_factor)
        
        # Create the screen
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Evolution Simulation")
        
        # Camera/View settings
        self.camera_x = 0
        self.camera_y = 0
        self.zoom = 1.0
        self.dragging = False
        self.last_mouse_pos = None
        
        # Load a better font
        try:
            # Try to use a system font that's likely to exist
            self.font = pygame.font.SysFont("Arial", int(24 * self.scale_factor * self.UI_SCALE))
        except:
            # Fallback to default font if Arial not available
            self.font = pygame.font.SysFont(None, int(24 * self.scale_factor * self.UI_SCALE))
        
        # Initialize game state
        self.initialize_game_state()

    def initialize_game_state(self):
        self.agents = []
        self.food_items = []
        self.map_state = MapState(self.BASE_WIDTH, self.BASE_HEIGHT)  # Use base dimensions for map
        self.ai_manager = AIManager(width=self.BASE_WIDTH, height=self.BASE_HEIGHT)
        
        # Initialize with some agents and food
        self.initialize_agents(20)
        self.initialize_food(30)
        self.initialize_resources(50)
        
        # Game state
        self.running = True
        self.clock = pygame.time.Clock()
        self.generation = 1
        self.generation_start_time = time.time()
        self.fps = 30
        
        # Debug info
        self.debug_info = {
            'fps': 0,
            'agents': 0,
            'food': 0,
            'generation': 1,
            'generation_time': 0,
            'epsilon': 0.1,
            'top_reward': 0,
            'zoom': '1.0x'
        }

    def initialize_agents(self, num_agents):
        for _ in range(num_agents):
            agent = AI_Human(f"AI_{random.randint(1, 1000)}", 150,  # Increased initial health
                           (random.randint(0, self.width), random.randint(0, self.height)))
            self.agents.append(agent)
            self.ai_manager.create_ai_agent(agent.id)

    def initialize_food(self, num_food):
        for _ in range(num_food):
            self.spawn_food()

    def initialize_resources(self, num_resources):
        """Initialize resources on the map"""
        for _ in range(num_resources):
            # Randomly choose resource type
            resource_type = random.choice(['wood', 'stone'])
            amount = random.randint(5, 15)
            position = (random.randint(0, self.width), random.randint(0, self.height))
            self.map_state.add_resource(position, resource_type, amount)

    def spawn_food(self):
        food = Food((random.randint(0, self.width), random.randint(0, self.height)))
        self.food_items.append(food)

    def world_to_screen(self, x, y):
        """Convert world coordinates to screen coordinates"""
        screen_x = (x - self.camera_x) * self.zoom + self.width / 2
        screen_y = (y - self.camera_y) * self.zoom + self.height / 2
        return screen_x, screen_y

    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates to world coordinates"""
        world_x = (screen_x - self.width / 2) / self.zoom + self.camera_x
        world_y = (screen_y - self.height / 2) / self.zoom + self.camera_y
        return world_x, world_y

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.dragging = True
                    self.last_mouse_pos = event.pos
                elif event.button == 4:  # Mouse wheel up
                    self.zoom = min(self.MAX_ZOOM, self.zoom * 1.1)
                    self.debug_info['zoom'] = f"{self.zoom:.1f}x"
                elif event.button == 5:  # Mouse wheel down
                    self.zoom = max(self.MIN_ZOOM, self.zoom / 1.1)
                    self.debug_info['zoom'] = f"{self.zoom:.1f}x"
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click
                    self.dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if self.dragging and self.last_mouse_pos:
                    dx = (event.pos[0] - self.last_mouse_pos[0]) / self.zoom
                    dy = (event.pos[1] - self.last_mouse_pos[1]) / self.zoom
                    self.camera_x -= dx
                    self.camera_y -= dy
                    self.last_mouse_pos = event.pos

    def draw(self):
        self.screen.fill((0, 0, 0))  # Black background
        
        # Draw resources
        for resource in self.map_state.resources:
            screen_x, screen_y = self.world_to_screen(resource.position[0], resource.position[1])
            if 0 <= screen_x <= self.width and 0 <= screen_y <= self.height:  # Only draw if on screen
                color = (139, 69, 19) if resource.type == 'wood' else (128, 128, 128)
                scaled_radius = int(6 * self.scale_factor * self.UI_SCALE * self.zoom)
                pygame.draw.circle(self.screen, color, (int(screen_x), int(screen_y)), scaled_radius)
                if resource.amount < 15:
                    # Render text with better quality
                    text = self.font.render(str(resource.amount), True, (255, 255, 255))
                    text_shadow = self.font.render(str(resource.amount), True, (0, 0, 0))
                    text_rect = text.get_rect(center=(screen_x, screen_y - 15 * self.zoom))
                    shadow_rect = text_shadow.get_rect(center=(screen_x + 1, screen_y - 15 * self.zoom + 1))
                    self.screen.blit(text_shadow, shadow_rect)
                    self.screen.blit(text, text_rect)
        
        # Draw buildings
        for building in self.map_state.buildings:
            screen_x, screen_y = self.world_to_screen(building.position[0], building.position[1])
            if 0 <= screen_x <= self.width and 0 <= screen_y <= self.height:
                size = int(16 * self.scale_factor * self.UI_SCALE * self.zoom)
                # Draw building base
                pygame.draw.rect(self.screen, (180, 180, 180), 
                               (screen_x - size//2, screen_y - size//2, size, size))
                
                # Draw building roof
                roof_points = [
                    (screen_x, screen_y - size//2 - 4 * self.zoom),
                    (screen_x - size//2 - 2 * self.zoom, screen_y - size//2),
                    (screen_x + size//2 + 2 * self.zoom, screen_y - size//2)
                ]
                pygame.draw.polygon(self.screen, (160, 160, 160), roof_points)
                
                if building.health < 100:
                    health_width = int(size * (building.health / 100.0))
                    # Health bar with shadow
                    pygame.draw.rect(self.screen, (0, 0, 0),
                                   (screen_x - size//2 - 1, screen_y - size//2 - 9 * self.zoom,
                                    size + 2, 5 * self.zoom))
                    pygame.draw.rect(self.screen, (0, 255, 0),
                                   (screen_x - size//2, screen_y - size//2 - 8 * self.zoom,
                                    health_width, 3 * self.zoom))
        
        # Draw food
        for food in self.food_items:
            screen_x, screen_y = self.world_to_screen(food.position[0], food.position[1])
            if 0 <= screen_x <= self.width and 0 <= screen_y <= self.height:
                scaled_radius = int(4 * self.scale_factor * self.UI_SCALE * self.zoom)
                pygame.draw.circle(self.screen, (0, 255, 0), (int(screen_x), int(screen_y)), scaled_radius)
        
        # Draw agents
        for agent in self.agents:
            screen_x, screen_y = self.world_to_screen(agent.position[0], agent.position[1])
            if 0 <= screen_x <= self.width and 0 <= screen_y <= self.height:
                scaled_radius = int(8 * self.scale_factor * self.UI_SCALE * self.zoom)
                pygame.draw.circle(self.screen, (255, 0, 0), (int(screen_x), int(screen_y)), scaled_radius)
                
                if agent.health < 100:
                    health_width = int(16 * self.scale_factor * self.UI_SCALE * self.zoom * (agent.health / 100.0))
                    bar_height = int(3 * self.scale_factor * self.UI_SCALE * self.zoom)
                    bar_y_offset = int(15 * self.scale_factor * self.UI_SCALE * self.zoom)
                    # Health bar with shadow
                    pygame.draw.rect(self.screen, (0, 0, 0),
                                   (screen_x - 8 * self.scale_factor * self.UI_SCALE * self.zoom - 1,
                                    screen_y - bar_y_offset - 1,
                                    16 * self.scale_factor * self.UI_SCALE * self.zoom + 2,
                                    bar_height + 2))
                    pygame.draw.rect(self.screen, (0, 255, 0),
                                   (screen_x - 8 * self.scale_factor * self.UI_SCALE * self.zoom,
                                    screen_y - bar_y_offset,
                                    health_width, bar_height))
                
                if any(amount > 0 for amount in agent.inventory.values()):
                    inv_y = screen_y + int(15 * self.scale_factor * self.UI_SCALE * self.zoom)
                    for i, (resource, amount) in enumerate(agent.inventory.items()):
                        if amount > 0:
                            color = (139, 69, 19) if resource == 'wood' else (128, 128, 128) if resource == 'stone' else (0, 255, 0)
                            pygame.draw.circle(self.screen, color, 
                                             (int(screen_x - 15 + i*10 * self.zoom), int(inv_y)), 
                                             int(2 * self.scale_factor * self.UI_SCALE * self.zoom))
        
        # Draw debug info (always on screen, not affected by camera)
        self.draw_debug_info()
        
        pygame.display.flip()

    def draw_debug_info(self):
        # Update debug info
        self.debug_info.update({
            'fps': int(self.clock.get_fps()),
            'agents': len(self.agents),
            'food': len(self.food_items),
            'generation': self.generation,
            'generation_time': f"{time.time() - self.generation_start_time:.1f}s",
            'epsilon': f"{self.ai_manager.epsilon:.3f}",
            'top_reward': f"{max(self.ai_manager.rewards.values()) if self.ai_manager.rewards else 0:.1f}",
            'zoom': f"{self.zoom:.1f}x"
        })
        
        # Draw debug text with better quality
        y_offset = 5
        x_offset = 5
        for i, (key, value) in enumerate(self.debug_info.items()):
            # Render text with better quality
            text = self.font.render(f"{key}: {value}", True, (255, 255, 255))
            text_shadow = self.font.render(f"{key}: {value}", True, (0, 0, 0))
            # Arrange in two columns
            if i % 2 == 0:
                self.screen.blit(text_shadow, (x_offset + 1, y_offset + 1))
                self.screen.blit(text, (x_offset, y_offset))
            else:
                self.screen.blit(text_shadow, (x_offset + 151, y_offset + 1))
                self.screen.blit(text, (x_offset + 150, y_offset))
                y_offset += 20

    def create_new_generation(self):
        print(f"\nGeneration {self.generation} ended after {time.time() - self.generation_start_time:.1f} seconds")
        print("Creating new generation...")
        
        # Evolve agents
        num_agents = 20  # Start with 20 agents each generation
        new_agents = self.ai_manager.evolve_agents(num_agents, self.agents)
        
        # Clear current agents and food
        self.agents = []
        self.food_items = []
        
        # Add new agents
        self.agents.extend(new_agents)
        
        # Initialize new food
        self.initialize_food(20)
        
        # Update generation info
        self.generation += 1
        self.generation_start_time = time.time()
        
        # Update epsilon
        self.ai_manager.update_epsilon()

    def game_loop(self):
        while self.running:
            # Handle events (including camera controls)
            self.handle_events()
            
            # Update game state
            self.handle_ai_actions()
            
            # Check if we need a new generation
            if len(self.agents) == 0:
                self.create_new_generation()
            
            # Draw everything
            self.draw()
            
            # Cap the frame rate
            self.clock.tick(self.fps)

    def handle_ai_actions(self):
        # Track which agents are exactly at their buildings
        agents_at_buildings = set()
        
        # First pass: check which agents are exactly at their buildings
        for building in self.map_state.buildings:
            for agent in self.agents:
                # Check if agent is exactly at building position (within 1 pixel)
                if (abs(agent.position[0] - building.position[0]) <= 1 and 
                    abs(agent.position[1] - building.position[1]) <= 1):
                    agents_at_buildings.add(agent.id)
                    
                    # If agent has food in inventory, store it in building
                    if agent.inventory.get('food', 0) > 0:
                        food_amount = agent.inventory['food']
                        building.add_food(food_amount)
                        agent.inventory['food'] = 0
                    
                    # If agent needs food and building has some, take it
                    if agent.health < 70 and building.stored_food > 0:
                        food_to_take = min(5, building.stored_food)  # Take up to 5 food at a time
                        food_received = building.remove_food(food_to_take)
                        agent.health = min(100, agent.health + food_received * 4)  # Each food gives 4 health
        
        # Second pass: handle agent actions
        for agent in self.agents:
            if isinstance(agent, AI_Human):
                # Get action and current state
                action, current_state = self.ai_manager.get_action(agent.id, agent, self)
                
                # Execute action based on action index
                if action == 0:  # Move
                    self.move_ai_agent(agent)
                elif action == 1:  # Eat/Gather
                    if self.handle_eating(agent):
                        continue
                    self.handle_gathering(agent)
                elif action == 2:  # Attack
                    self.handle_attacking(agent)
                elif action == 3:  # Build
                    self.handle_building(agent)
                elif action == 4:  # Reproduce
                    self.handle_reproduction(agent)
                
                # Get next state after action
                next_state = self.ai_manager.get_state(agent, self.agents, self.food_items)
                
                # Calculate reward based on survival and resource gathering
                reward = self.ai_manager.calculate_reward(agent, action, self.agents, self.food_items)
                
                # Store experience in memory
                done = agent.health <= 0
                self.ai_manager.store_experience(agent.id, current_state, action, reward, next_state, done)
                
                # Update agent's reward
                self.ai_manager.update_reward(agent.id, reward)
                
                # Decrease health over time (slower rate only if they are exactly at their building)
                health_decay = 0.02 if agent.id in agents_at_buildings else 0.05
                agent.health -= health_decay
                
                # Remove dead agents
                if agent.health <= 0:
                    self.agents.remove(agent)
                    self.ai_manager.remove_ai_agent(agent.id)
                    if agent.id in agents_at_buildings:
                        agents_at_buildings.remove(agent.id)

    def move_ai_agent(self, agent):
        # Get current position
        x, y = agent.position
        
        # Calculate movement based on nearest food and agents
        dx, dy = 0, 0
        
        # Find nearest food
        nearest_food = None
        min_food_dist = float('inf')
        for food in self.food_items:
            dist = ((food.position[0] - x) ** 2 + (food.position[1] - y) ** 2) ** 0.5
            if dist < min_food_dist:
                min_food_dist = dist
                nearest_food = food
        
        # Find nearest agent
        nearest_agent = None
        min_agent_dist = float('inf')
        for other in self.agents:
            if other.id != agent.id:
                dist = ((other.position[0] - x) ** 2 + (other.position[1] - y) ** 2) ** 0.5
                if dist < min_agent_dist:
                    min_agent_dist = dist
                    nearest_agent = other
        
        # Move towards food if health is low, otherwise move randomly
        if agent.health < 30 and nearest_food:
            dx = (nearest_food.position[0] - x) / max(1, min_food_dist)
            dy = (nearest_food.position[1] - y) / max(1, min_food_dist)
        else:
            # Random movement with small steps
            dx = random.uniform(-3, 3)
            dy = random.uniform(-3, 3)
        
        # Normalize movement vector
        length = (dx ** 2 + dy ** 2) ** 0.5
        if length > 0:
            dx = dx / length * 3  # Max speed of 3 pixels
            dy = dy / length * 3
        
        # Update position with bounds checking
        new_x = max(0, min(self.width, x + dx))
        new_y = max(0, min(self.height, y + dy))
        agent.position = (new_x, new_y)

    def handle_eating(self, agent):
        # Find nearest food
        x, y = agent.position
        nearest_food = None
        min_dist = float('inf')
        
        for food in self.food_items:
            dist = ((food.position[0] - x) ** 2 + (food.position[1] - y) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                nearest_food = food
        
        # Eat if close enough
        if nearest_food and min_dist < 20:
            agent.health = min(100, agent.health + 20)
            self.food_items.remove(nearest_food)
            # Spawn new food
            self.spawn_food()
            return True
        return False

    def handle_attacking(self, agent):
        # Find nearest agent
        x, y = agent.position
        nearest_agent = None
        min_dist = float('inf')
        
        for other in self.agents:
            if other.id != agent.id:
                dist = ((other.position[0] - x) ** 2 + (other.position[1] - y) ** 2) ** 0.5
                if dist < min_dist:
                    min_dist = dist
                    nearest_agent = other
        
        # Attack if close enough
        if nearest_agent and min_dist < 20:
            nearest_agent.health -= 10
            agent.health -= 5  # Attacking costs health

    def handle_reproduction(self, agent):
        # Can only reproduce if health is high enough
        if agent.health >= 80:
            # Create new agent
            new_agent = AI_Human(f"AI_{random.randint(1, 1000)}", 50, agent.position)
            self.agents.append(new_agent)
            self.ai_manager.create_ai_agent(new_agent.id)
            # Parent loses health
            agent.health -= 40

    def handle_gathering(self, agent):
        """Handle resource gathering"""
        nearby_resources = self.map_state.get_nearby_resources(agent.position, agent.gathering_range)
        for resource in nearby_resources:
            if agent.can_gather(resource.position) and resource.amount > 0:
                gather_amount = min(2, resource.amount)  # Gather up to 2 at a time
                agent.add_resource(resource.type, gather_amount)
                resource.amount -= gather_amount
                if resource.amount <= 0:
                    resource.respawn_time = 30.0  # 30 seconds respawn time
                return True
        return False

    def handle_building(self, agent):
        """Handle building construction"""
        if not agent.can_build:
            return False
            
        # Try to build near the agent
        build_pos = (agent.position[0] + random.randint(-20, 20),
                    agent.position[1] + random.randint(-20, 20))
        
        if agent.can_build_at(build_pos):
            # Check if there's already a building nearby
            nearby_buildings = self.map_state.get_nearby_buildings(build_pos, 30)
            if not nearby_buildings:
                # Use resources to build
                if agent.use_resource('wood', 5) and agent.use_resource('stone', 3):
                    self.map_state.add_building(build_pos, 'shelter', agent.id)
                    return True
        return False
