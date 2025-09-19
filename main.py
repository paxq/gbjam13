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
    def __init__(self, x, y, ID, collidable=True):
        self.x = x # world units
        self.y = y # world units
        self.id = ID
        self.rect = pygame.Rect(x, y, TILE_SIZE * SCALE_MODIFIER, TILE_SIZE * SCALE_MODIFIER) # pixel units
        self.collidable = collidable

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
        self.tiles = [] #Tile(6, 8, 'A0'), Tile(7, 8, 'A0'), Tile(6, 7, 'A1', collidable=False), Tile(3, 6, 'A0')
        self.interactions = []
        self.entities = []

        # Load world info
        with open('world.txt') as world_data:
            data = world_data.read().replace('\n', '').split('NL')

            world_size = data.pop(0)
            worldX = int(world_size.split("x")[0])
            worldY = int(world_size.split("x")[1])

            start_pos = data.pop(0)
            startX = float(start_pos.split("x")[0])
            startY = float(start_pos.split("x")[1])

            offsetX = worldX - startX
            offsetY = worldY - startY

            for column in range(0, len(data) - 1):
                row = 0
                while row < worldX * 2:
                    ID = data[column][row] + data[column][row + 1]
                    collision = True
                    if ID == "00" or ID == "A1":
                        collision = False

                    tile = Tile(row / 2 + offsetX, column + offsetY, ID, collidable=collision)
                    self.tiles.append(tile)
                    row += 2

    def move(self, x, y):
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

        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.center_pos = self.rect.center
        self.player_trigger = pygame.Rect(((self.center_pos[0] - self.width / 2) * self.width), ((self.center_pos[1] - self.height / 2) * self.height), self.width, self.height)

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

    def move(self, world):
        self.velocityX /= 2
        self.velocityY /= 1.4
        
        if self.velocityY > 0:
            self.is_grounded = False

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

        # Check for collisions
        # (add world first)
        for tile in world.tiles:
            # Test x dir
            test_rect = pygame.Rect((self.x + self.velocityX) * self.width, self.y * self.height, self.width, self.height)
            if test_rect.colliderect(tile.rect) and tile.collidable:
                self.velocityX = 0
            # Test y dir
            test_rect = pygame.Rect(self.x * self.width, (self.y + self.velocityY) * self.height, self.width, self.height)
            if test_rect.colliderect(tile.rect) and tile.collidable:
                # Reset is_grounded
                if self.velocityY > 0:
                    self.is_grounded = True
                # Reset velocity on headbang
                if self.velocityY < 0:
                    self.jumping = 0
                self.velocityY = 0
        
        # quit game if u ded
        if self.y > 16:
            pygame.quit()

        self.update_vars()

        return {
                "x" : self.x,
                "y" : self.y,
                "velX" : self.velocityX,
                "velY" : self.velocityY,
                "c_pos" : self.center_pos,
                "collider" : self.player_trigger
               }

    def draw(self, surface):
        surface.blit(self.playerImg, ((self.x * self.width), (self.y * self.height), self.width, self.height))

    def update_vars(self):
        self.center_pos = ((self.x + self.width / 2), (self.y + self.height / 2))
        self.rect.top = self.y
        self.rect.left = self.x
        self.player_trigger = pygame.Rect(((self.center_pos[0] - self.width / 2) * self.width), ((self.center_pos[1] - self.height / 2) * self.height), self.width, self.height)


class Camera:
    def __init__(self):
        self.padding_horizontal = 48 * SCALE_MODIFIER
        self.padding_vertical = 32 * SCALE_MODIFIER
        self.correctional_strength = 0.1

        self.correctional_timer = 0

        self.camera_collider_x = pygame.Rect((SCREEN_WIDTH * SCALE_MODIFIER) / 2 - self.padding_horizontal / 2, (SCREEN_HEIGHT * SCALE_MODIFIER) - TILE_SIZE * SCALE_MODIFIER, self.padding_horizontal, TILE_SIZE * SCALE_MODIFIER)
        self.camera_collider_y = pygame.Rect((SCREEN_WIDTH * SCALE_MODIFIER) / 2 - (TILE_SIZE * SCALE_MODIFIER) / 2, (SCREEN_HEIGHT * SCALE_MODIFIER) - self.padding_vertical, TILE_SIZE * SCALE_MODIFIER, self.padding_vertical)

    def calculate_movements(self, player_info, world_info):
        player_trigger = player_info['collider']
        playerX = player_info['x']
        playerY = player_info['y']
        velocityX = player_info['velX']
        velocityY = player_info['velY']

        worldX = world_info.x
        worldY = world_info.y

        # Reset Padding zone
        if velocityX <= 0.03 and velocityX >= -0.03:
            self.camera_collider_x.width = self.padding_horizontal
            self.camera_collider_x.left = (SCREEN_WIDTH * SCALE_MODIFIER) / 2 - self.padding_horizontal / 2
            self.correctional_timer = 0

        # Move padding zone
        self.camera_collider_x.bottom = player_trigger.bottom
        self.camera_collider_y.right = player_trigger.right

        # Shrink padding zone symmetrically
        if self.correctional_timer > 0:
            pr = -1/32 * (self.correctional_timer - 32) ** 2 + 32 # Smoothing function

            self.camera_collider_x.width -= self.correctional_strength * pr
            self.camera_collider_x.left += self.correctional_strength * pr / 2
        if self.correctional_timer < 64:
            self.correctional_timer += 1


        # Calculate Movement
        if self.camera_collider_x.colliderect(player_trigger):
            # Calculate Player movement
            playerX += velocityX
        else:
            # X-axis
            if player_trigger.left > SCREEN_WIDTH * SCALE_MODIFIER / 2: #EDIT: FIXED.  center pos takes the 0-9 coorinate system and adds half the pixel width  ##Upon closer inspection the previous information is false. I don't know how it works or why, but it works, soo....
                worldX -= velocityX
                if self.correctional_timer > 0 and player_trigger.left > self.camera_collider_x.right:
                    playerX = self.camera_collider_x.right / player_trigger.width
            elif player_trigger.right < SCREEN_WIDTH * SCALE_MODIFIER / 2:
                worldX -= velocityX
                if self.correctional_timer > 0 and player_trigger.right < self.camera_collider_x.left:    
                    playerX = (self.camera_collider_x.left - player_trigger.width) / player_trigger.width
                
        # Y-Axis
        worldY -= velocityY
        if player_trigger.bottom <= self.camera_collider_y.top:
            self.camera_collider_y.top = player_trigger.centery
        elif player_trigger.top >= self.camera_collider_y.bottom:
            self.camera_collider_y.bottom = player_trigger.centery
        else:
            playerY += velocityY
            worldY += velocityY # Cancel it out

        return {
            'playerX' : playerX,
            'playerY' : playerY,
            'worldX' : worldX,
            'worldY' : worldY
            }

class Game:
    def __init__(self):
        self.running = True

        self.player = Player(4.5, 7)
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
        player_info = self.player.move(self.world)
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

        pygame.draw.rect(screen, (0, 255, 0), game.camera.camera_collider_x) # Debug
        pygame.draw.rect(screen, (0, 200, 100), game.camera.camera_collider_y) # Debug
        pygame.draw.rect(screen, (255, 0, 255), game.player.player_trigger) # Debug

        # game._debug_draw_grid(screen)
        game.draw(screen)
        
        pygame.display.update()

        deltaTime = clock.tick(FPS) / 1000
        await asyncio.sleep(0) # do not forget that one, it must be called on every frame
        
    # Closing the game (not strictly required)
    pygame.quit()

asyncio.run(main())