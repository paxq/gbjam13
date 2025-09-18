import sys
import pygame
import asyncio
import random
import math
from settings import *
from sprites import *

pygame.init()
pygame.display.set_caption("GBJam13 [insert name here]")
screen = pygame.display.set_mode((SCREEN_WIDTH * SCALE_MODIFIER, SCREEN_HEIGHT * SCALE_MODIFIER))
aspect_ratio = 10 / 9

clock = pygame.time.Clock()
deltaTime = 0
running = True


# IMG & SOUND SAVED
# font = pygame.font.SysFont("Arial", 20)
# text = font.render("Hello World!", False, (255, 255, 255))

# img = pygame.image.load("img/char_idle-1.png")
# img = pygame.transform.scale(img, (64, 64))

# pygame.mixer.init()
# sfx = pygame.mixer.Sound("sfx/step.wav")

sprites = load_sprites()

class GameObject:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def move(self, x, y):
        self.x += x
        self.y += y

class Tile(GameObject):
    def __init__(self, x, y, ID):
        self.x = x # world units
        self.y = y # world units
        self.id = ID
        self.rect = pygame.Rect(x, y, 16 * SCALE_MODIFIER, 16 * SCALE_MODIFIER) # pixel units

        img = ""
        for sprite in sprites:
            if sprite['id'] == self.id:
                img = sprite['img']

        self.img = pygame.transform.scale(img, (self.rect.width, self.rect.height))

        super().__init__(self.x, self.y)

    def update(self):
        self.rect.left = self.x * self.rect.width
        self.rect.top = self.y * self.rect.height

class WorldEvent:
    def __init__(self, event_type, location, function):
        self.type = event_type
        self.pos = location
        self.event = function

class World:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.backgrounds = []
        self.tiles = [Tile(6, 8, 0)]
        self.interactions = []
        self.entities = []

    def move(self, x, y):
        self.x += y
        self.y += y

        # for background in self.backgrounds:
        #     background.move(x, y)
        for tile in self.tiles:
            tile.move(x, y)
        # for interaction in self.interactions:
        #     interaction.move(x, y)
        # for entity in self.entities:
        #     entity.move(x, y)

    def draw(self, screen):
        for tile in self.tiles:
            screen.blit(tile.img, tile.rect)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.width = 16 * SCALE_MODIFIER
        self.height = 16 * SCALE_MODIFIER

        self.center_pos = (self.x + self.width / 2, self.y + self.height / 2)
        self.player_collider = pygame.Rect(((self.center_pos[0] - self.width / 2) * self.width), ((self.center_pos[1] - self.height / 2) * self.height), self.width, self.height)

        self.speed = 0.035
        self.velocityX = 0
        self.velocityY = 0
        self.jump_strength = 0.0925 # for some reason this acts like an exponential sacle but it works
        self.better_jump_strength = self.jump_strength
        self.gravity = 0.032
        self.is_grounded = False
        self.jumping = 1

        self.playerImg = pygame.image.load('Assets/Player_placeholder.png')
        self.playerImg = pygame.transform.scale(self.playerImg, (self.width, self.height))

    def move(self):
        # dx = 0
        # dy = 0

        self.velocityX /= 2
        self.velocityY /= 1.4

        if self.y == 8: # will need to chage this to accept colidble blocks as valid is_grouded spaces
            self.is_grounded = True

        # Get keypresses
        key = pygame.key.get_pressed()
        if key[pygame.K_w] or key[pygame.K_SPACE] or key[pygame.K_UP]:
            if self.is_grounded:
                self.is_grounded = False
                self.jumping = 20
                self.better_jump_strength = self.jump_strength
            if self.jumping > 0:
                self.jumping += 0.4
                self.better_jump_strength += 0.0010
            
        if key[pygame.K_a] or key[pygame.K_LEFT]:
            self.velocityX -= self.speed
        if key[pygame.K_d] or key[pygame.K_RIGHT]:
            self.velocityX += self.speed

        if self.jumping > 0:
            self.better_jump_strength *= 0.95
            self.velocityY -= self.better_jump_strength
            self.jumping -= 1

        self.velocityY += self.gravity

        # self.x += self.velocityX
        # self.y += self.velocityY

        # Check for collisions
        # (add world first)
        if self.y + self.velocityY < 0:
            self.y = 0
            self.velocityY = 0
        if self.y + self.velocityY > 8:
            self.y = 8
            self.velocityY = 0
        if self.x + self.velocityX < 0:
            self.x = 0
            self.velocityX = 0
        if self.x + self.velocityX > 9:
            self.x = 9
            self.velocityX = 0

        self.center_pos = ((self.x + self.width / 2), (self.y + self.height / 2))
        self.player_collider = pygame.Rect(((self.center_pos[0] - self.width / 2) * self.width), ((self.center_pos[1] - self.height / 2) * self.height), self.width, self.height)

        return {
                "x" : self.x,
                "y" : self.y,
                "velX" : self.velocityX,
                "velY" : self.velocityY,
                "c_pos" : self.center_pos,
                "collider" : self.player_collider
               }

    def draw(self, surface):
        surface.blit(self.playerImg, ((self.x * self.width), (self.y * self.height), self.width, self.height))

    #def update(self, events):
    #    pass

class Camera:
    def __init__(self):
        self.padding_horizontal = 64 * SCALE_MODIFIER #px
        self.padding_vertical = 64 * SCALE_MODIFIER
        self.correctional_strength = 0.25

        self.camera_collider = pygame.Rect((SCREEN_WIDTH * SCALE_MODIFIER) / 2 - self.padding_horizontal / 2, (SCREEN_HEIGHT * SCALE_MODIFIER) - self.padding_vertical, self.padding_horizontal, self.padding_vertical)

    def calculate_movements(self, player_info, world_info):
        player_collider = player_info['collider']
        center = player_info['c_pos']
        centerX = center[0]
        centerY = center[1]
        playerX = player_info['x']
        playerY = player_info['y']
        velocityX = player_info['velX']
        velocityY = player_info['velY']

        worldX = world_info.x
        worldY = world_info.y

        # Calculate Movement
        if not self.camera_collider.colliderect(player_collider):
            # Calculate World movement
            if centerX - player_collider.width / 2 > 4: # center pos takes the 0-9 coorinate system and adds half the pixel width
                if velocityX > 0:
                    worldX -= velocityX
                elif velocityX < 0:
                    playerX += velocityX
            elif centerX - player_collider.width / 2 < 4:
                if velocityX < 0:
                    worldX -= velocityX
                elif velocityX > 0:
                    playerX += velocityX
            
            if centerY - player_collider.height / 2 > 4:
                playerY += velocityY
            else:
                worldY -= velocityY
        else:
            # Calculate Player movement
            playerX += velocityX
            playerY += velocityY

        return {
                'playerX' : playerX,
                'playerY' : playerY,
                'worldX' : worldX,
                'worldY' : worldY
               }

class Game:
    def __init__(self):
        self.running = True

        self.player = Player(4.5, 8)
        self.camera = Camera()
        self.world = World()
    
    def handle_pygame_events(self, events):
        # Handle game quit, gui interaction, and keyboard input
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False

    def update_world(self, world_events):
        # Handle all world-based interactions
        # Custom event order?
        # for event in world_events:
        #     if event.type == "placeholder-1":
        #         event.function()
        # for event in world_events:
        #     if event.type == "placeholder-2":
        #         event.function()
        pass

    def update(self):
        # Update Order:
        # • Block events
        for tile in self.world.tiles:
            tile.update()
        # • Entities
        #   – Player
        player_info = self.player.move()
        #   – Passive Entities
        #   – Enemies
        # • Interactions
        #   – Player interactions
        #   – NPC interactions

        # • Camera
        movement = self.camera.calculate_movements(player_info, self.world)
        self.player.x = movement['playerX']
        self.player.y = movement['playerY']

        self.world.move(movement['worldX'], movement['worldY'])
        # print(movement['worldX'], movement['worldY'])

        # print(self.player.x, self.player.y, self.player.velocityX, self.player.velocityY)


    def draw(self, screen):
        # Draw Order:
        # • Background_1
        # • Background_2
        # • World Tiles
        # • Debug Objects
        self.world.draw(screen)
        # • Interaction Tiles
        # • Entities
        # • Player
        self.player.draw(screen)
        # • Foreground_1

    def _debug_draw_grid(self, screen, block_per_width=10, block_per_height=9):
        # draw x lines
        for x in range(0, block_per_height):
            pygame.draw.line(screen, (255, 255, 255), (0, ((SCREEN_HEIGHT * SCALE_MODIFIER) / block_per_height) * x), (SCREEN_WIDTH * SCALE_MODIFIER, ((SCREEN_HEIGHT * SCALE_MODIFIER) / block_per_height) * x))
        # draw y lines
        for y in range(0, block_per_width):
            pygame.draw.line(screen, (255, 255, 255), (((SCREEN_WIDTH * SCALE_MODIFIER) / block_per_width) * y, 0), (((SCREEN_WIDTH * SCALE_MODIFIER) / block_per_width) * y, SCREEN_HEIGHT * SCALE_MODIFIER))

        
game = Game()
# player = Player(0, 8)

async def main():
    global game, deltaTime, clock

    while game.running:
        # Update things
        game.handle_pygame_events(pygame.event.get())
        game.update()

        # Draw things
        screen.fill((0, 0, 0))

        pygame.draw.rect(screen, (0, 255, 0), game.camera.camera_collider) # Debug
        pygame.draw.rect(screen, (255, 0, 255), game.player.player_collider) # Debug

        game._debug_draw_grid(screen)
        game.draw(screen)
        
        pygame.display.update()

        deltaTime = clock.tick(FPS) / 1000
        await asyncio.sleep(0) # do not forget that one, it must be called on every frame
        
    # Closing the game (not strictly required)
    pygame.quit()

asyncio.run(main())